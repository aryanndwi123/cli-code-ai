from typing import List,Dict,Any
import logging

from anthropic import Anthropic
from anthropic.types import TextBlock, ToolUseBlock


from .base import BaseLLMClient,LLMResponse

logger = logging.getLogger(__name__)


class AnthropicClient(BaseLLMClient):
    def __init__(self, api_key:str, model:str = "claude-sonnet-4-20250514"):
        super().__init__(api_key, model)
        self.client = Anthropic(api_key=api_key)
        logger.info(f"Anthropic client initialized with model: {model}")
        
    def create_message(
        self, 
        message: List[Dict[str,Any]], 
        system:str, 
        tools: List[Dict[str,Any]], 
        max_token: int = 4096, 
        temperature:float=0.7
        ) -> LLMResponse:
        
        try:
            response =self.client.message.create(
                model = self.model,
                max_token =max_token,
                temperature=temperature,
                system=system,
                message = message,
                tools = tools if tools else None
            )
            
            content_blocks = []
            
            for block in response.content:
                if isinstance(block,TextBlock):
                    content_blocks.append({
                        "type":"text",
                        "text":block.text
                    })
                    
                elif isinstance(block,ToolUseBlock):
                    content_blocks.append({
                        "type":"tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })
                    
            return LLMResponse(
                content=content_blocks,
                stop_reason=response.stop_reason,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
                model=response.model
            )
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}", exc_info = True)
            raise
    
    def convert_tools_to_provider_format(self, tools: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
        return tools