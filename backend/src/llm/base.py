from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict,Any, Optional, Literal
from enum import Enum

class LLMProvider(str,Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"
    
@dataclass
class LLMResponse:
    content: List[Dict[str, Any]]
    stop_reason: str
    usage: Dict[str, int]
    model: str
    
    def get_text(self) ->str:
        texts = []
        
        for block in self.content:
            if block.get("type") == "text":
                texts.append(block.get("text",""))
        return "\n\n".join(texts)
    
    def get_tool_calls(self) -> List[Dict[str,Any]]:
        tools = []
        for block in self.content:
            if block.get("type") == "tool_use":
                tools.append(block)
                
        return tools

class BaseLLMClient(ABC):
    def __init__(self,api_key:str,model:str):
        self.api_key = api_key
        self.model = model
        
    @abstractmethod
    def create_message(
        self,
        message:List[Dict[str,Any]],
        system: str,
        tools:List[Dict[str,Any]],
        max_token: int,
        temperature: float
    ) -> LLMResponse:
        
        pass
    
    @abstractmethod
    def convert_tools_to_provider_format(self, tools:List[Dict[str,Any]]) -> Any:
        pass
        