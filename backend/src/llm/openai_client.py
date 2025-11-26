from typing import List,Dict,Any
import logging
import json

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    
from .base import BaseLLMClient, LLMResponse

logger = logging.getLogger(__name__)

class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key:str, model:str = "gpt-4-turbo-preview"):
        if OpenAI is None:
            raise ImportError("openai package not installed. Install with: pip install openai")
        
        super().__init__(api_key,model)
        self.client = OpenAI(api_key=api_key)
        logger.info(f"OpenAI client initialized with model: {model}")
        
    def create_message(
        self, 
        messages: List[Dict[str,Any]], 
        system: str, 
        tools: List[Dict[str,Any]], 
        max_token: int = 4096, 
        temperature: float = 0.7
        ) -> LLMResponse:
        
        try:
            openai_messages = self._convert_messages(messages,system)
            
            openai_tools = self.convert_tools_to_provider_format(tools) if tools else None
            
            kwargs = {
                "model" : self.model,
                "messages": openai_messages,
                "max_token": max_token,
                "temperature": temperature,
            }
            
            if openai_tools:
                kwargs["tools"] = openai_tools
                kwargs["tool_choice"] = "auto"
                
            response = self.client.chat.completions.create(**kwargs)
            
            message = response.choices[0].message
            
            content_blocks = []
            
            if message.content:
                content_blocks.append({
                    "type":"text",
                    "text":message.content
                })
            
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    content_blocks.append({
                        "type": "tool_use",
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "input": json.loads(tool_call.function.arguments)
                    })
                    
            stop_reason = "end_turn"
            if message.tool_calls:
                stop_reason = "tool_use"
            elif response.choices[0].finish_reason == "length":
                stop_reason = "max_token"
                
            return LLMResponse(
                content=content_blocks,
                stop_reason=stop_reason,
                usage={
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens
                },
                model= response.model
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}",exc_info =True)
            raise
            
        
    def _convert_message(self, messages:List[Dict[str,Any]],system:str)-> List[Dict[str,Any]]:
        openai_messages = []
        
        if system:
            openai_messages.append({
                "role":"system",
                "content":system
            })
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "user":
                if isinstance(content, list) and any(c.get("type") == "tool_result" for c in content):
                    for item in content:
                        if item.get("type") == "tool_result":
                            openai_messages.append({
                                "role":"tool",
                                "tool_call_id":item["tool_use_id"],
                                "content":item["content"]
                            })
                else:
                    openai_messages.append({
                        "role":"user",
                        "content": content if isinstance(content,str) else str(content)
                        
                    })
            elif role == "assistant":
                if isinstance(content,list):
                    text_parts = []
                    tool_calls = []
                    
                    for block in content:
                        if block.get("type") == "text":
                            text_parts.append(block["text"])
                        elif block.get("type") == "tool_use":
                            tool_calls.append({
                                "id":block["id"],
                                "type":"function",
                                "function":{
                                    "name": block["name"],
                                    "arguments": json.dumps(block["input"])
                                }
                            })
                            
                    msg_dict = {
                        "role":"assistant",
                        "content":"\n".join(text_parts) if text_parts else None
                    }
                    
                    if tool_calls:
                        msg_dict["tool_calls"] = tool_calls
                    
                    openai_messages.append(msg_dict)
                    
                else:
                    openai_messages.append({
                        "role":"assistant",
                        "content":content
                    })
                    
        return openai_messages
    
    def convert_tools_to_provider_format(self, tools:List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        openai_tools = []
        
        for tool in tools:
            openai_tools.append({
                "type":"function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            })
        return openai_tools