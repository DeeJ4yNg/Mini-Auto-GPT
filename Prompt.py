import os
from pathlib import Path
from ai_config import AIConfig
from Agent import clean_input
import json
from typing import Any

#Setup original prompt
def prompt_user() -> AIConfig:
    ai_name = ""
    # Construct the prompt
    print("Welcome to Auto-GPT! ")
    print("Enter the name of your AI and its role below. Entering nothing will load defaults.")

    # Get AI Name from User
    print("Name your AI:  ")
    print("For example, 'Entrepreneur-GPT'")
    ai_name = clean_input("AI Name: ")
    if ai_name == "":
        ai_name = "Entrepreneur-GPT"

    print(ai_name + "here! I am at your service.")

    # Get AI Role from User
    print("Describe your AI's role: ")
    print("For example, 'an AI designed to autonomously develop and run businesses with the sole goal of increasing your net worth.'")
    ai_role = clean_input(f"{ai_name} is: ")
    if ai_role == "":
        ai_role = "an AI designed to autonomously develop and run businesses with the"
        " sole goal of increasing your net worth."

    # Enter up to 5 goals for the AI
    print("Enter up to 5 goals for your AI: ")
    print("For example: \nIncrease net worth, Grow Twitter Account, Develop and manage multiple businesses autonomously'")
    print("Enter nothing to load defaults, enter nothing when finished.", flush=True)
    ai_goals = []
    for i in range(5):
        ai_goal = clean_input("Goal:")
        if ai_goal == "":
            break
        ai_goals.append(ai_goal)
    if not ai_goals:
        ai_goals = [
            "Increase net worth",
            "Grow Twitter Account",
            "Develop and manage multiple businesses autonomously",
        ]

    return AIConfig(ai_name, ai_role, ai_goals)


class PromptGenerator:
    """
    A class for generating custom prompt strings based on constraints, commands,
        resources, and performance evaluations.
    """

    def __init__(self) -> None:
        """
        Initialize the PromptGenerator object with empty lists of constraints,
            commands, resources, and performance evaluations.
        """
        self.constraints = []
        self.commands = []
        self.resources = []
        self.performance_evaluation = []
        self.response_format = {
            "thoughts": {
                "text": "thought",
                "reasoning": "reasoning",
                "plan": "- short bulleted\n- list that conveys\n- long-term plan",
                "criticism": "constructive self-criticism",
            },
            "command": {"name": "command name", "args": {"arg name": "value"}},
        }

    def add_constraint(self, constraint: str) -> None:
        self.constraints.append(constraint)

    def add_command(self, command_label: str, command_name: str, args=None) -> None:
        if args is None:
            args = {}
        command_args = {arg_key: arg_value for arg_key, arg_value in args.items()}
        command = {
            "label": command_label,
            "name": command_name,
            "args": command_args,
        }
        self.commands.append(command)

    def _generate_command_string(self, command: dict[str, Any]) -> str:
        args_string = ", ".join(
            f'"{key}": "{value}"' for key, value in command["args"].items()
        )
        return f'{command["label"]}: "{command["name"]}", args: {args_string}'

    def add_resource(self, resource: str) -> None:
        self.resources.append(resource)

    def add_performance_evaluation(self, evaluation: str) -> None:
        self.performance_evaluation.append(evaluation)

    def _generate_numbered_list(self, items: list[Any], item_type="list") -> str:
        if item_type == "command":
            return "\n".join(
                f"{i+1}. {self._generate_command_string(item)}"
                for i, item in enumerate(items)
            )
        else:
            return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))

    def generate_prompt_string(self) -> str:
        formatted_response_format = json.dumps(self.response_format, indent=4)
        return (
            f"Constraints:\n{self._generate_numbered_list(self.constraints)}\n\n"
            "Commands:\n"
            f"{self._generate_numbered_list(self.commands, item_type='command')}\n\n"
            f"Resources:\n{self._generate_numbered_list(self.resources)}\n\n"
            "Performance Evaluation:\n"
            f"{self._generate_numbered_list(self.performance_evaluation)}\n\n"
            "You should only respond in JSON format as described below \nResponse"
            f" Format: \n{formatted_response_format} \nEnsure the response can be"
            " parsed by Python json.loads"
        )


#↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓Get all details of prompts↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
def get_prompt() -> str:
    prompt_generator = PromptGenerator()
    prompt_generator.add_constraint(
        "~4000 word limit for short term memory. Your short term memory is short, so"
        " immediately save important information to files."
    )
    prompt_generator.add_constraint(
        "If you are unsure how you previously did something or want to recall past"
        " events, thinking about similar events will help you remember."
    )
    prompt_generator.add_constraint("No user assistance")
    prompt_generator.add_constraint(
        'Exclusively use the commands listed in double quotes e.g. "command name"'
    )

    # Define the command list
    commands = [
        (
            "Start GPT Agent",
            "start_agent",
            {"name": "<name>", "task": "<short_task_desc>", "prompt": "<prompt>"},
        ),
        (
            "Message GPT Agent",
            "message_agent",
            {"key": "<key>", "message": "<message>"},
        ),
        ("List GPT Agents", "list_agents", {}),
        ("Delete GPT Agent", "delete_agent", {"key": "<key>"}),

        ("Write to file", "write_to_file", {"file": "<file>", "text": "<text>"}),
        ("Read file", "read_file", {"file": "<file>"}),
        ("Append to file", "append_to_file", {"file": "<file>", "text": "<text>"}),
        ("Delete file", "delete_file", {"file": "<file>"}),
        ("Search Files", "search_files", {"directory": "<directory>"}),
        ("Evaluate Code", "evaluate_code", {"code": "<full_code_string>"}),
        (
            "Get Improved Code",
            "improve_code",
            {"suggestions": "<list_of_suggestions>", "code": "<full_code_string>"},
        ),
        ("Execute PowerShell", "execute_powershell", {"commandline": "<full_code_string>"})
    ]


    # Only add shell command to the prompt if the AI is allowed to execute it

#    commands.append(
#        (
#            "Execute PowerShell Command, non-interactive commands only",
#            "execute_Powershell",
#            {"command_line": "<command_line>"},
#        ),
#    )

    commands.append(
        ("Do Nothing", "do_nothing", {}),
    )
    commands.append(
        ("Task Complete (Shutdown)", "task_complete", {"reason": "<reason>"}),
    )

    for command_label, command_name, args in commands:
        prompt_generator.add_command(command_label, command_name, args)

    prompt_generator.add_resource(
        "Internet access for searches and information gathering."
    )
    prompt_generator.add_resource("Long Term memory management.")
    prompt_generator.add_resource(
        "GPT-3.5 powered Agents for delegation of simple tasks."
    )
    prompt_generator.add_resource("File output.")

    prompt_generator.add_performance_evaluation(
        "Continuously review and analyze your actions to ensure you are performing to"
        " the best of your abilities."
    )
    prompt_generator.add_performance_evaluation(
        "Constructively self-criticize your big-picture behavior constantly."
    )
    prompt_generator.add_performance_evaluation(
        "Reflect on past decisions and strategies to refine your approach."
    )
    prompt_generator.add_performance_evaluation(
        "Every command has a cost, so be smart and efficient. Aim to complete tasks in"
        " the least number of steps."
    )

    return prompt_generator.generate_prompt_string()


def construct_prompt() -> str:
    PATH = Path(os.getcwd()) / "ai_settings.yaml"
    config = AIConfig.load(PATH)
    if config.ai_name:
        print("Welcome back! Would you like me to return to being" + config.ai_name + "?")
        should_continue = clean_input(
            f"""Continue with the last settings?
Name:  {config.ai_name}
Role:  {config.ai_role}
Goals: {config.ai_goals}
Continue (y/n): """
        )
        if should_continue.lower() == "n":
            config = AIConfig()
    if not config.ai_name:
        config = prompt_user()
        config.save(PATH)
    global ai_name
    ai_name = config.ai_name
    print("returning construct_full_prompt()")
    return config.construct_full_prompt()