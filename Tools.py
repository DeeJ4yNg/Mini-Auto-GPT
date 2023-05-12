import json
from Memory import get_memory
from file_operations import read_file, write_to_file, append_to_file, delete_file, search_files
from typing import List, NoReturn, Union, Dict
from agent_manager import AgentManager
from execute_code import evaluate_code, execute_shell, improve_code
from powershell import PowerShell

AGENT_MANAGER = AgentManager()

def shutdown() -> NoReturn:
    print("Shutting down...")
    quit()

def is_valid_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False

#Agent commands.
def start_agent(name: str, task: str, prompt: str, model="gpt-3.5-turbo") -> str:
    first_message = f"""You are {name}.  Respond with: "Acknowledged"."""
    key, ack = AGENT_MANAGER.create_agent(task, first_message, model)
    agent_response = AGENT_MANAGER.message_agent(key, prompt)
    return f"Agent {name} created with key {key}. First response: {agent_response}"


def message_agent(key: str, message: str) -> str:
    if is_valid_int(key):
        agent_response = AGENT_MANAGER.message_agent(int(key), message)
    else:
        return "Invalid key, must be an integer."
    return agent_response


def list_agents():
    return "List of agents:\n" + "\n".join(
        [str(x[0]) + ": " + x[1] for x in AGENT_MANAGER.list_agents()]
    )


def delete_agent(key: str) -> str:
    result = AGENT_MANAGER.delete_agent(key)
    return f"Agent {key} deleted." if result else f"Agent {key} does not exist."

#Main
def map_command_synonyms(command_name: str):
    synonyms = [
        ("write_file", "write_to_file"),
        ("create_file", "write_to_file"),
        ("search", "google"),
    ]
    for seen_command, actual_command_name in synonyms:
        if command_name == seen_command:
            return actual_command_name
    return command_name

def get_command(response_json: Dict):
    try:
        if "command" not in response_json:
            return "Error:", "Missing 'command' object in JSON"

        if not isinstance(response_json, dict):
            return "Error:", f"'response_json' object is not dictionary {response_json}"

        command = response_json["command"]
        if not isinstance(command, dict):
            return "Error:", "'command' object is not a dictionary"

        if "name" not in command:
            return "Error:", "Missing 'name' field in 'command' object"

        command_name = command["name"]

        # Use an empty dictionary if 'args' field is not present in 'command' object
        arguments = command.get("args", {})

        return command_name, arguments
    except json.decoder.JSONDecodeError:
        return "Error:", "Invalid JSON"
    # All other errors, return "Error: + error message"
    except Exception as e:
        return "Error:", str(e)


def execute_command(command_name: str, arguments):
    memory = get_memory()

    try:
        command_name = map_command_synonyms(command_name)
        
        if command_name == "memory_add":
            return memory.add(arguments["string"])
        elif command_name == "start_agent":
            return start_agent(
                arguments["name"], arguments["task"], arguments["prompt"]
            )
        elif command_name == "message_agent":
            return message_agent(arguments["key"], arguments["message"])
        elif command_name == "list_agents":
            return list_agents()
        elif command_name == "delete_agent":
            return delete_agent(arguments["key"])
        
        elif command_name == "read_file":
            return read_file(arguments["file"])
        elif command_name == "write_to_file":
            return write_to_file(arguments["file"], arguments["text"])
        elif command_name == "append_to_file":
            return append_to_file(arguments["file"], arguments["text"])
        elif command_name == "delete_file":
            return delete_file(arguments["file"])
        elif command_name == "search_files":
            return search_files(arguments["directory"])
        
        elif command_name == "evaluate_code":
            return evaluate_code(arguments["code"])
        elif command_name == "improve_code":
            return improve_code(arguments["suggestions"], arguments["code"])
        #elif command_name == "execute_python_file":  # Add this command
            #return execute_python_file(arguments["file"])
        #elif command_name == "execute_shell":
            #return execute_shell(arguments["command_line"])
        elif command_name == "execute_powershell":
            with PowerShell('GBK') as ps:
                return ps.run("taskmgr")
        
        elif command_name == "do_nothing":
            return "No action performed."
        elif command_name == "task_complete":
            shutdown()
        else:
            return (
                f"Unknown command '{command_name}'. Please refer to the 'COMMANDS'"
                " list for available commands and only respond in the specified JSON"
                " format."
            )
    except Exception as e:
        return f"Error: {str(e)}"