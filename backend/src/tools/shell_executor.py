import subprocess
from typing import Dict,Any
import logging
from .base import BaseTool

logger = logging.getLogger(__name__)

class ShellExecutorTool(BaseTool):
    def get_schema(self) -> Dict[str,Any]:
        return {
            "name": "execute_command",
            "description": "Execute a shell command in the workspace directory",
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default 30)",
                        "default": 30
                    }
                },
                "required": ["command"]
            }
        }
        
    def execute(self, parameters:Dict[str,Any]) -> Dict[str,Any]:
        command = parameters["command"]
        timeout = parameters.get("timeout",30)
        
        dangerous_patterns = {
            "rm -rf /",
            "mkfs",
            "dd if=",
            ":(){:|:&};:",  # Fork bomb
            "chmod -R 777 /",
        }
        
        for pattern in dangerous_patterns:
            if pattern in command:
                return {
                    "content": f"Error: Dangerous command blocked: {pattern}",
                    "success": False
                }
        
        try:
            logger.info(f"Executing command: {command}")
            
            result=subprocess.run(
                command,
                shell=True,
                cwd=str(self.workspace_path),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output_parts = [
                f"Command: {command}",
                f"Exit code: {result.returncode}",
                "=" * 60
            ]
            
            if result.stdout:
                output_parts.append("STDOUT:")
                output_parts.append(result.stdout)
            
            return {
                "content": "\n".join(output_parts),
                "exit_code": result.returncode,
                "success": result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return{
                "content": f"Error: Command timed out after {timeout} seconds",
                "success": False
            }
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {
                "content": f"Error executing command: {str(e)}",
                "success": False
            }