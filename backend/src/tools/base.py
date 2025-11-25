from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path

class BaseTool(ABC):
    def __init__(self,workspace_path:Path):
        self.workspace_path = workspace_path
    
    @abstractmethod
    def get_schema(self) -> Dict[str,Any]:
        pass
    
    @abstractmethod
    def execute(self,parameters:Dict[str,Any]) -> Dict[str,Any]:
        pass
    
    def validate_path(self,path:str) -> Path:
        full_path = (self.workspace_path/path).resolve()
        
        if not str(full_path).startswith(str(self.workspace_path)):
            raise ValueError(f"Path {path} is outside workspace")
        
        return full_path
    
    