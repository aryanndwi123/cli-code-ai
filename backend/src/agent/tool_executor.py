from pathlib import Path
from typing import Dict,Any,List
import logging

from ..tools.base import BaseTool
from ..tools.code_editor import ReadFileTool, WriteFileTool, ListDirectoryTool
from ..tools.shell_executor import ShellExecutorTool


logger = logging.getLogger(__name__)

class ToolExecutor:
    def __init__(self,workspace_path: Path):
        self.workspace_path = workspace_path
        self.tools: Dict[str,BaseTool] = self._register_tools()
        logger.info(f"TOolExecutor initialized with {len(self.tools)} tools")
    
    def _register_tools(self) -> Dict[str,BaseTool]:
        tools={
            "read_file": ReadFileTool(self.workspace_path),
            "write_file": WriteFileTool(self.workspace_path),
            "list_directory": ListDirectoryTool(self.workspace_path),
            "execute_command": ShellExecutorTool(self.workspace_path),
        }
        
        return tools
    
    def get_tool_schema(self) ->List[Dict[str,Any]]:
        return [tool.get_schema() for tool in self.tools.values()]
    
    def execute(self, tool_name:str, parameters: Dict[str,Any])->Dict[str,Any]:
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}. Available: {list(self.tools.keys())}")
        tool = self.tools[tool_name]
        
        try: 
            logger.info(f"Executing tool: {tool_name}")
            result = tool.execute(parameters)
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}", exc_info =True)
            raise
        