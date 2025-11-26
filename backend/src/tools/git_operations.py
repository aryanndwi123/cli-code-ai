import subprocess
from pathlib import Path
from typing import Dict, Any
import logging

from .base import BaseTool

logger = logging.getLogger(__name__)

class GitOperationsTool(BaseTool):
    
    def get_schema(self) -> Dict[str,Any]:
        return {
            "name": "git_operation",
            "description": "Perform git operations (status, diff, log, add, commit)",
            "input_schema": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["status", "diff", "log", "add", "commit", "init"],
                        "description": "Git operation to perform"
                    },
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Files to operate on (for add/commit)"
                    },
                    "message": {
                        "type": "string",
                        "description": "Commit message (for commit operation)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of log entries to show (for log)",
                        "default": 10
                    }
                },
                "required": ["operation"]
            }
        }
    
    def execute(self, parameters:Dict[str,Any]) -> Dict[str,Any]:
        operation = parameters["operation"]
        
        try:
            if operation == "status":
                return self._git_status()
            elif operation=="diff":
                return self._git_diff()
            elif operation=="log":
                limit = parameters.get("limit",10)
                return self._git_log(limit)
            elif operation=="add":
                files = parameters.get("files",[])
                return self._git_add(files)
            elif operation=="commit":
                message = parameters.get("message","")
                return self._get_commit(message)
            elif operation =="init":
                return self._git_init()
            else:
                return{
                    "content": f"Unknown git operation: {operation}",
                    "success": False
                }
                
        except Exception as e:
            logger.error(f"Git operation failed: {e}",exc_info=True)
            return {
                "content": f"Git operation failed: {str(e)}",
                "success": False
            }
            
    def _run_git_command(self,args: list, timeout:int=30) -> subprocess.CompletedProcess:
        cmd = ["git"] + args
        return subprocess.run(
            cmd,
            cwd=str(self.workspace_path),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
    def _git_status(self) ->Dict[str,Any]:
        result = self._run_git_command(["status","--short"])
        
        if result.returncode != 0:
            return{
                "content": f"Error: {result.stderr or 'Not a git repository'}",
                "success": False
            }
        
        output = result.stdout.strip()
        if not output:
            return {
                "content": "Working tree is clean (no changes)",
                "success": True
            }   
        
        return {
            "content": f"Git Status:\n{output}",
            "success": True
        }
        
    def _git_diff(self) -> Dict[str,Any]:
        result = self._run_git_command(["diff"])
        
        if result.returncode != 0:
            return {
                "content": f"Error: {result.stderr}",
                "success": False
            }
        
        output = result.stdout.strip()
        
        if not output:
            return {
                "content": "No changes to show",
                "success": True
            }
        
        if len(output) > 5000:
            output = output[:5000] + "\n\n... (diff truncated)"
            
        return {
            "content": f"Git Diff:\n{output}",
            "success": True
        }
        
    def _git_log(self,limit:int) -> Dict[str,Any]:
        result = self._run_git_command([
            "log",
            f"-{limit}",
            "--oneline",
            "--decorate"
        ])
        
        if result.returncode != 0:
            return {
                "content": f"Error: {result.stderr or 'No commits yet'}",
                "success": False
            }
        
        return {
            "content": f"Recent Commits:\n{result.stdout}",
            "success": True
        }
        
    def _git_add(self,files:list) -> Dict[str,Any]:
        if not files:
            return {
                "content": "Error: No files specified",
                "success": False
            }
            
        result = self._run_git_command(["add"] + files)
        
        if result.returncode != 0:
            return{
                "content": f"Error: {result.stderr}",
                "success": False
            }
            
        return {
            "content": f"Staged files: {', '.join(files)}",
            "files_modified": files,
            "success": True
        }
    
    def _git_commit(self,message:str) -> Dict[str,Any]:
        if not message:
            return{
                "content": "Error: Commit message required",
                "success": False
            }
            
        result = self._run_git_command(["commit","-m",message])
        
        if result.returncode !=0:
            return {
                "content": f"Error: {result.stderr}",
                "success": False
            }
            
        return {
            "content": f"Committed with message: {message}\n{result.stdout}",
            "success": True
        }
        
    def _git_init(self) -> Dict[str,Any]:
        result = self._run_git_command(["init"])
        
        if result.returncode != 0:
            return {
                "content": f"Error: {result.stderr}",
                "success": False
            }
            
        return {
            "content": "Git repository initialized",
            "success": True
        }