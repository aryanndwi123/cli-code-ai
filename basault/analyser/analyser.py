# This file basically analyse the whole codebase and then compile
# it so that there is a enough context for the LLM for making the 
# code changes

import tree_sitter_python as tspython
from tree_sitter import Language, Parser
import os
from pathlib import Path


PY_LANGUAGE = Language(tspython.language())

def parse_directory(root_path):
    for file_path in Path(directory).rglob('*'):
        if file_path.is_file():
            file_handler(file_path)
            
            

            