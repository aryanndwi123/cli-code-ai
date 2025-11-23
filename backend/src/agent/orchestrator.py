
from dataclasses import dataclass,field
from typing import List, Dict, Any, Optional, Literal
from pathlib import Path
import logging
from datetime import datetime

from anthropic import Anthropic, APIError, APIStatusError
from anthropic.types import Message, TextBlock, ToolUseBlock, ContentBlock

from tool_executor import ToolExecutor
from exceptions import (
    OrchestratorError,
    MaxIterationsError,
    ToolExecutionError,
    APICallError
)

import time




# workspace_path = ""

# config_api =  ANTHROPIC_API_KEY

# config_model_name = ""

# config_max_itr = 0



# llm_client()

# tool_executor()

# conv_history = []

# def config(config_api, model_name,max_itr):
#     while end_turn == false and itr < max_itr:
logger = logging.getLogger(__name__)    
        
@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator"""
    api_key:str
    model: str = "claude-sonnet-4-20250514"
    max_iterations: int = 25
    max_token:int = 4096
    temperature: float = 0.7
    workspace_path:str = "."
    max_context_token: int = 180000
    
    max_retires: int = 3
    retry_delay:float = 1.0
    
    require_confirmation_for_destructive: bool = True
    

@dataclass
class ExecutionResult:
    """Result of executing a task"""
    success: bool
    final_message:str
    iterations_used: int
    tools_called: List[str]
    files_modified: List[str]
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: Dict[str,Any] = field(default_factory=dict)
 
class Orchestrator:
    def __init__(self,config:OrchestratorConfig):
        self.config = config
        
        self.client = Anthropic(api_key = config.api_key)
        
        self.tool_executor = ToolExecutor(
            workspace_path = Path(config.workspace_path)
        )      
        
        self.messages: List[Dict[str,Any]] = []
        self.system_prompt:str = self.build_system_prompt()
        
        
        self.iteration_count: int = 0
        self.tools_called: List[str] = []
        self.files_modified: List[str] = []
        self.errors: List[str] = []
        
        
        self.is_running: bool = False
        self.start_time: Optional[datetime] = None
        
        logger.info(f"Orchestration initialized with model: {config.model}")
        
        
    def execute(self, task:str) -> ExecutionResult:
        logger.info(f"Starting task execution: {task[:100]}...")
        
        self.start_time = datetime.now()
        self.is_running = True
        self.iteration_count = 0
        
        self.message = []
        self.tools_called = []
        self.files_modified = []
        self.errors = []
        
        
        try:
            self.add_user_message(task)
            
            while self.iteration_count < self.config.max_iterations:
                self.iteration_count += 1
                logger.info(f"Iteration {self.iteration_count}/{self.config.max_iterations}")
                
                
                response = self._call_llm()
                
                self._add_assistant_message(response)
                
                stop_reason = response.stop_reason
                logger.info(f"Stop reason: {stop_reason}")
                
                if stop_reason == "end_turn":
                    
                    logger.info("Task completed - Claude signaled end_turn")
                    return self._create_success_result(response)
                
                elif stop_reason == "tool_use":
                    
                    tool_calls = self.extract_tool_calls(response)
                    
                    logger.info(f"Executing {len(tool_calls)} tool calls")
                    
                    tool_results = self._execute_tools(tool_calls)
                    
                    self._add_tool_results(tool_results)
                    
                elif stop_reason == "max_token":
                    logger.warning("Response hit max_token, continuing....")
                    continue
                
                else:
                    logger.error(f"Unexpected stop reason: {stop_reason}")
                    self.errors.append(f"Uneexpected stop reason: {stop_reason}")
                    continue
                
                
            logger.warning(f"Max iterations ({self.config.max_iterations})reached")
            raise MaxIterationsError(
                f"REached maximum iterations ({self.config.max_iterations}) without completion"
                
            )
            
        except MaxIterationsError as e:
            return self._create_timeout_result(str(e))
        
        except Exception as e:
            logger.error(f"Error during execution: {e}", exc_info = True)
            return self._create_error_result(e)
        
        finally:
            self.is_running = False
            execution_time = (datetime.now() - self.start_time).total_seconds()
            logger.info(f"Execution completed in {execution_time:.2f}s")
    
    
    def _call_llm(self) -> Message:
        
        tools = self.tool_executor.get_tool_schema()
        
        messages = self._build_api_message()
        
        for attempt in range(self.config.max_retries):
            try: 
                logger.debug(f"API call attempt {attempt + 1}/{self.config.max_retried}")
                
                
                response = self.client.message.create(
                    model = self.config.model,
                    max_token = self.config.max_token,
                    temperature = self.config.temperature,
                    system = self.system_prompt,
                    messages = messages,
                    tools = tools
                )
                
                logger.debug(f"API call successful Usage: {response.usage}")
                return response
            
            
            except APIStatusError as e:
                if e.status_code in [429,500,502,503,504]:
                    if attempt < self.config.max_reties - 1:
                        delay = self.config.retry_delay * (2 ** attempt)
                        logger.warning(f"API error {e.status_code}, retrying in {delay}s ....")
                        time.sleep(delay)
                        continue
                    
                    
                
                logger.error(f"API status error: {e}")
                raise APICallError(f"API call failed: {e}") from e
            
            except APIError as e:
                logger.error(f"API error:{e}")
                raise APICallError(f"API call failed: {e}") from e
            
            
        raise APICallError(f"API call failed after {self.config.max_retires} retries")
    
    
    def _execute_tools(self,tool_calls:List[Dict[str,Any]]) ->List[Dict[str,Any]]:
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_input = tool_call["input"]
            tool_id = tool_call["id"]
            
            logger.info(f"Executing tool: {tool_name}")
            logger.debug(f"Tool input: {tool_input}")
            
            
            try:
                result = self.tool_executor.execute(tool_name,tool_input)
                
                
                self.tools_called.append(tool_name)
                
                if "files_modified" in result:
                    
                    self.files_modified.extend(result["files_modified"])
                    
                tool_result = {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": self._format_tool_result(result)
                }
                
                logger.info(f"Tool {tool_name} Executed successfully")
                
            except Exception as e:
                
                logger.error(f"TOol {tool_name} failed: {e}")
                self.errors.append(f"{tool_name}: {str(e)}")
                
                tool_result = {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": f"Error: {str(e)}",
                    "is_error":True
                }
                
            results.append(tool_result)
            
        return results
    
                    
                    
        
                    
                
    
        
    

