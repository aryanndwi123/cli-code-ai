from pathlib import Path
from typing import Dict, Any, List
import logging 
import re

from .base import BaseTool

logger = logging.getLogger(__name__)

class CodeAnalyserTool(BaseTool):
    
    def get_schema(self) -> Dict[str,Any]:
        return {
            "name": "search_code",
            "description": "Search for text/patterns in files across the workspace",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text or pattern to search for"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "File pattern to search in (e.g., '*.py', '*.ts')",
                        "default": "*.*"
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Whether search should be case sensitive",
                        "default": False
                    },
                    "regex": {
                        "type": "boolean",
                        "description": "Whether query is a regex pattern",
                        "default": False
                    }
                },
                "required": ["query"]
            }
        }
        
    def execute(self, parameters:Dict[str,Any]) -> Dict[str,Any]:
        query = parameters["query"]
        file_pattern = parameters.get("file_pattern", "*.*")
        case_sensitive = parameters.get("case_sensitive", False)
        use_regex = parameters.get("regex", False)
        
        try: 
            files = list(self.workspace_path.rglob(file_pattern))
            
            ignore_dirs = {'.git','node_modules','__pychache__','.venv','dist','build'}
            files = [f for f in files if not any(d in f.parts for d in ignore_dirs)]
            
            results = []
            
            if use_regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(query,flags)
                
            else:
                pattern = query if case_sensitive else query.lower()
                
            for file_path in files:
                if not file_path.is_file():
                    continue
                
                try:
                    content = file_path.read_text(encoding='utf-8')
                    lines = content.split('\n')
                    
                    matches = []
                    
                    for line_num, line in enumerate(lines,1):
                        if use_regex:
                            if pattern.search(line):
                                matches.append((line_num, line.strip()))
                            else:
                                search_line = line if case_sensitive else line.lower()
                                if pattern in search_line:
                                    matches.append((line_num,line.strip()))
                                    
                    if matches:
                        rel_path = file_path.relative_to(self.workspace_path)
                        results.append({
                            "file": str(rel_path),
                            "matches": matches
                        })
                except (UnicodeDecodeError,PermissionError):
                    continue
                
            
            if not results:
                return{
                    "content": f"No matches found for '{query}' in {file_pattern}",
                    "success": True
                }
            
            output_lines = [
                f"Found {sum(len(r['matches']) for r in results)} match(es) in {len(results)} file(s)",
                "=" * 60
            ]
            
            for result in results[:20]: 
                output_lines.append(f"\n {result['file']}")
                for line_num, line in result['matches'][:10]: 
                    output_lines.append(f"  {line_num:4d} | {line}")
                
                if len(result['matches']) > 10:
                    output_lines.append(f"  ... and {len(result['matches']) - 10} more matches")

            if len(results)>20:
                output_lines.append(f"\n... and {len(results) - 20} more files")
                
            return {
                "content": "\n".join(output_lines),
                "match_count": sum(len(r['matches']) for r in results),
                "file_count": len(results),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error searching code: {e}", exc_info=True)
            return {
                "content": f"Error searching code: {str(e)}",
                "success":False
            }
