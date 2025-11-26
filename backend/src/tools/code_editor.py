from pathlib import Path
from typing import Dict, Any
import logging

from .base import BaseTool

logger = logging.getLogger(__name__)

class ReadFileTool(BaseTool):
    
    def get_schema(self) -> Dict[str,Any]:
        return {
            "name": "read_file",
            "description": "Read the contents of a file in the workspace",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file from workspace root"
                    }
                },
                "required": ["path"]
            }
        }
        
    def execute(self, parameters:Dict[str,Any]) ->Dict[str,Any]:
        path_str = parameters["path"]
        
        try:
            file_path = self.validate_path(path_str)
            
            if not file_path.exists():
                return{
                    "content": f"Error: File not found: {path_str}",
                    "success": False
                }
                
            content = file_path.read_text(encoding='utf-8')
            
            lines = content.split('\n')
            numbered_content = '\n'.join(
                f"{i+1:4d} | {line}"for i, line in enumerate(lines)
            )
            return {
                "content": f"File: {path_str}\n{'='*60}\n{numbered_content}",
                "success": True
            }
            
        except UnicodeDecodeError:
            return{
                "content": f"Error: File {path_str} is not a text file (binary content)",
                "success": False
            }
        except Exception as e:
            logger.error(f"Error reading file {path_str}: {e}")
            return {
                "content": f"Error reading file: {str(e)}",
                "success": False
            }
            
class WriteFileTool(BaseTool):
    
    def get_schema(self) ->Dict[str,Any]:
    
        return {
            "name": "write_file",
            "description": "Write content to a file (creates if doesn't exist, overwrites if exists)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        }
        
    def execute(self, parameters:Dict[str,Any]) -> Dict[str,Any]:
        path_str = parameters["path"]
        content = parameters["content"]
        
        try:
            file_path = self.validate_path(path_str)
            
            file_path.parent.mkdir(parents=True,exist_ok=True)
            
            file_path.write_text(content,encoding='utf-8')
            
            return {
                "content": f"Successfully wrote to {path_str} ({len(content)} bytes)",
                "files_modified": [path_str],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error writing file {path_str}:{e}")
            
            return {
                "content": f"Error writing file: {str(e)}",
                "success": False
            }
            
class ListDirectoryTool(BaseTool):
    def get_schema(self) -> Dict[str,Any]:
        return {
            "name": "list_directory",
            "description": "List files and directories in a path",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to list (use '.' for workspace root)"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to list recursively",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        }
        
    def execute(self, parameters: Dict[str,Any]) -> Dict[str,Any]:
        path_str = parameters["path"]
        recurcive = parameters.get("recurcive",False)
        
        try:
            dir_path = self.validate_path(path_str)
            
            if not dir_path.exists():
                return {
                    "content": f"Error: Directory not found: {path_str}",
                    "success": False
                } 
            if not dir_path.is_dir():
                return {
                    "content": f"Error: Path is not a directory: {path_str}",
                    "success": False
                }
                
            if recurcive:
                items = sorted(dir_path.rglob('*'))
            else: 
                items = sorted(dir_path.iterdir())
            
            
            output_lines = [f"Contents of {path_str}:", "="*60]
            
            for item in items:
                rel_path = item.relative_to(self.workspace_path)
                if items.is_dir():
                    output_lines.append(f"{rel_path}/")
                else:
                    size = item.stat().st_size
                    output_lines.append(f"{rel_path} ({size} bytes)")
                    
            return {
                "content": "\n".join(output_lines),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error listing directory {path_str}: {e}")
            return {
                "content": f"Error listing directory: {str(e)}",
                "success": False
            }
            
class EditFileTool(BaseTool):
    def get_schema(self) -> Dict[str,Any]:
        return {
            "name": "edit_file",
            "description": "Edit a file by searching for text and replacing it",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file"
                    },
                    "search": {
                        "type": "string",
                        "description": "Exact text to search for (must be unique in file)"
                    },
                    "replace": {
                        "type": "string",
                        "description": "Text to replace with"
                    }
                },
                "required": ["path", "search", "replace"]
            }
        }
        
    def execute(self, parameters:Dict[str,Any]) -> Dict[str,Any]:
        path_str = parameters["path"]
        search_text = parameters["search"]
        replace_text = parameters["replace"]
        
        try:
            file_path = self.validate_path(path_str)
            
            if not file_path.exists():
                return{
                    "content": f"Error: File not found: {path_str}",
                    "success": False
                }
                
            content = file_path.read_text(encoding='utf-8')
            
            if search_text not in content:
                return {
                    "content": f"Error: Search text not found in {path_str}",
                    "success": False
                }
                
            count = content.count(search_text)
            if count >1:
                return {
                    "content": f"Error: Search text appears {count} times in file. Must be unique.",
                    "success": False
                }
                
            new_content = content.replace(search_text,replace_text)
            
            file_path.write_text(new_content, encoding='utf-8')
            
            return {
                "content": f"Successfully edited {path_str}",
                "files_modified": [path_str],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error editing file {path_str}: {e}")
            return {
                "content": f"Error editing file: {str(e)}",
                "success": False
            }
            