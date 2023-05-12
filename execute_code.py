import os
import subprocess
import json
from pathlib import Path
from Chat import call_ai_function

WORKSPACE_PATH = Path(os.getcwd()) / "auto_gpt_workspace"

def evaluate_code(code: str) -> list[str]:

    function_string = "def analyze_code(code: str) -> List[str]:"
    args = [code]
    description_string = (
        "Analyzes the given code and returns a list of suggestions" " for improvements."
    )

    return call_ai_function(function_string, args, description_string)

def improve_code(suggestions: list[str], code: str) -> str:

    function_string = (
        "def generate_improved_code(suggestions: List[str], code: str) -> str:"
    )
    args = [json.dumps(suggestions), code]
    description_string = (
        "Improves the provided code based on the suggestions"
        " provided, making no other changes."
    )

    return call_ai_function(function_string, args, description_string)

def execute_shell(command_line: str) -> str:

    current_dir = os.getcwd()
    if str(WORKSPACE_PATH) not in current_dir:
        os.chdir(WORKSPACE_PATH)

    print(f"Executing command '{command_line}' in working directory '{os.getcwd()}'")

    result = subprocess.run(command_line, capture_output=True, shell=True)
    output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    os.chdir(current_dir)

    return output

#execute_shell("taskmgr")