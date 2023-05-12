
from JSON_fixes import fix_json_using_multiple_techniques, fix_and_parse_json, attempt_to_fix_json_by_finding_outermost_brackets
from Chat import create_chat_message, chat_with_ai
from Tools import get_command, execute_command
import json
import traceback

def clean_input(prompt: str = ""):
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("You interrupted Auto-GPT")
        print("Quitting...")
        exit(0)

def print_assistant_thoughts(ai_name, assistant_reply):
    try:
        try:
            # Parse and print Assistant response
            assistant_reply_json = fix_and_parse_json(assistant_reply)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in assistant thoughts\n" + assistant_reply)
            assistant_reply_json = attempt_to_fix_json_by_finding_outermost_brackets(
                assistant_reply
            )
            if isinstance(assistant_reply_json, str):
                assistant_reply_json = fix_and_parse_json(assistant_reply_json)

        # Check if assistant_reply_json is a string and attempt to parse
        # it into a JSON object
        if isinstance(assistant_reply_json, str):
            try:
                assistant_reply_json = json.loads(assistant_reply_json)
            except json.JSONDecodeError:
                print("Error: Invalid JSON\n" + assistant_reply)
                assistant_reply_json = (
                    attempt_to_fix_json_by_finding_outermost_brackets(
                        assistant_reply_json
                    )
                )

        assistant_thoughts_reasoning = None
        assistant_thoughts_plan = None
        assistant_thoughts_criticism = None
        if not isinstance(assistant_reply_json, dict):
            assistant_reply_json = {}
        assistant_thoughts = assistant_reply_json.get("thoughts", {})
        assistant_thoughts_text = assistant_thoughts.get("text")

        if assistant_thoughts:
            assistant_thoughts_reasoning = assistant_thoughts.get("reasoning")
            assistant_thoughts_plan = assistant_thoughts.get("plan")
            assistant_thoughts_criticism = assistant_thoughts.get("criticism")

        print(ai_name + " THOUGHTS: " + assistant_thoughts_text)
        print("REASONING:" + assistant_thoughts_reasoning)

        if assistant_thoughts_plan:
            print("PLAN:")
            # If it's a list, join it into a string
            if isinstance(assistant_thoughts_plan, list):
                assistant_thoughts_plan = "\n".join(assistant_thoughts_plan)
            elif isinstance(assistant_thoughts_plan, dict):
                assistant_thoughts_plan = str(assistant_thoughts_plan)

            # Split the input_string using the newline character and dashes
            lines = assistant_thoughts_plan.split("\n")
            for line in lines:
                line = line.lstrip("- ")
                print("- " + line.strip())

        print("CRITICISM:" + assistant_thoughts_criticism)

        return assistant_reply_json
    except json.decoder.JSONDecodeError:
        print("Error: Invalid JSON\n" + assistant_reply)

    # All other errors, return "Error: + error message"
    except Exception:
        call_stack = traceback.format_exc()
        print("Error: \n" + call_stack)


class Agent:
    def __init__(
        self,
        ai_name,
        memory,
        full_message_history,
        next_action_count,
        system_prompt,
        triggering_prompt,
    ):
        self.ai_name = ai_name
        self.memory = memory
        self.full_message_history = full_message_history
        self.next_action_count = next_action_count
        self.system_prompt = system_prompt
        self.triggering_prompt = triggering_prompt

    def start_interaction_loop(self):
        loop_count = 0
        command_name = None
        arguments = None
        user_input = ""

        while True:
            loop_count += 1
            print( "Start looping... Count: %d" %(loop_count))
            if loop_count > 20:
                print("loop count reached limit, will break.")
                break

            assistant_reply = chat_with_ai(
                self.system_prompt,
                self.triggering_prompt,
                self.full_message_history,
                self.memory,
                4000)

            assistant_reply_json = fix_json_using_multiple_techniques(assistant_reply)
            
            if assistant_reply_json != {}:
                try:
                    print_assistant_thoughts(self.ai_name, assistant_reply)
                    command_name, arguments = get_command(assistant_reply_json)
                except Exception as e:
                    print("error:" + e)

            print("Next Action: " + command_name)
            print("Argument: %s"  %(arguments))
            print(
                    "Enter 'y' to authorise command "
                    "commands, 'n' to exit program, or enter feedback for " + self.ai_name
                )
            
            while True:
                console_input = clean_input("Input:")
                if console_input.lower().rstrip() == "y":
                    user_input = "GENERATE NEXT COMMAND JSON"
                    break
                elif console_input.lower() == "n":
                    user_input = "EXIT"
                    break
                else:
                    user_input = console_input
                    command_name = "human_feedback"
                    break
            
            if user_input == "GENERATE NEXT COMMAND JSON":
                print("-=-=-=-=-=-=-= COMMAND AUTHORISED BY USER -=-=-=-=-=-=-=")
            elif user_input == "EXIT":
                print("Exiting...", flush=True)
                break
            
            #execute command
            if command_name is not None and command_name.lower().startswith("error"):
                result = (
                    f"Command {command_name} threw the following error: {arguments}"
                )
            elif command_name == "human_feedback":
                result = f"Human feedback: {user_input}"
            else:
                result = (
                    f"Command {command_name} returned: "
                    f"{execute_command(command_name, arguments)}"
                )
                if self.next_action_count > 0:
                    self.next_action_count -= 1

            memory_to_add = (
                f"Assistant Reply: {assistant_reply} "
                f"\nResult: {result} "
                f"\nHuman Feedback: {user_input} "
            )

            #self.memory.add(memory_to_add)

            if result is not None:
                self.full_message_history.append(create_chat_message("system", result))
                print("SYSTEM: " + result)
            else:
                self.full_message_history.append(
                    create_chat_message("system", "Unable to execute command")
                )
                print("SYSTEM: " + "Unable to execute command")
