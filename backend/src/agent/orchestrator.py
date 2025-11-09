
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
            
                    
                
    
        
    

