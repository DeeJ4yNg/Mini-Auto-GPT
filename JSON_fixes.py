from regex import regex
import contextlib
import json
import re
from Chat import call_ai_function

JSON_SCHEMA = """
{
    "command": {
        "name": "command name",
        "args": {
            "arg name": "value"
        }
    },
    "thoughts":
    {
        "text": "thought",
        "reasoning": "reasoning",
        "plan": "- short bulleted\n- list that conveys\n- long-term plan",
        "criticism": "constructive self-criticism",
    }
}
"""

#################JSON Fix for special errors######################
def extract_char_position(error_message: str) -> int:
    char_pattern = re.compile(r"\(char (\d+)\)")
    if match := char_pattern.search(error_message):
        return int(match[1])
    else:
        raise ValueError("Character position not found in the error message.")

def fix_invalid_escape(json_to_load: str, error_message: str) -> str:
    while error_message.startswith("Invalid \\escape"):
        bad_escape_location = extract_char_position(error_message)
        json_to_load = (
            json_to_load[:bad_escape_location] + json_to_load[bad_escape_location + 1 :]
        )
        try:
            json.loads(json_to_load)
            return json_to_load
        except json.JSONDecodeError as e:
            error_message = str(e)
    return json_to_load

def add_quotes_to_property_names(json_string: str) -> str:

    def replace_func(match: re.Match) -> str:
        return f'"{match[1]}":'

    property_name_pattern = re.compile(r"(\w+):")
    corrected_json_string = property_name_pattern.sub(replace_func, json_string)

    try:
        json.loads(corrected_json_string)
        return corrected_json_string
    except json.JSONDecodeError as e:
        raise e

def balance_braces(json_string: str):

    open_braces_count = json_string.count("{")
    close_braces_count = json_string.count("}")

    while open_braces_count > close_braces_count:
        json_string += "}"
        close_braces_count += 1

    while close_braces_count > open_braces_count:
        json_string = json_string.rstrip("}")
        close_braces_count -= 1

    with contextlib.suppress(json.JSONDecodeError):
        json.loads(json_string)
        return json_string


#↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑JSON Fix for special errors↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑


def correct_json(json_to_load: str) -> str:
    try:
        json.loads(json_to_load)
        return json_to_load
    except json.JSONDecodeError as e:
        error_message = str(e)
        if error_message.startswith("Invalid \\escape"):
            json_to_load = fix_invalid_escape(json_to_load, error_message)
        if error_message.startswith(
            "Expecting property name enclosed in double quotes"
        ):
            json_to_load = add_quotes_to_property_names(json_to_load)
            try:
                json.loads(json_to_load)
                return json_to_load
            except json.JSONDecodeError as e:
                error_message = str(e)
        if balanced_str := balance_braces(json_to_load):
            return balanced_str
    return json_to_load

def fix_json(json_string: str, schema: str) -> str:
    # Try to fix the JSON using GPT:
    function_string = "def fix_json(json_string: str, schema:str=None) -> str:"
    args = [f"'''{json_string}'''", f"'''{schema}'''"]
    description_string = (
        "This function takes a JSON string and ensures that it"
        " is parseable and fully compliant with the provided schema. If an object"
        " or field specified in the schema isn't contained within the correct JSON,"
        " it is omitted. The function also escapes any double quotes within JSON"
        " string values to ensure that they are valid. If the JSON string contains"
        " any None or NaN values, they are replaced with null before being parsed."
    )

    if not json_string.startswith("`"):
        json_string = "```json\n" + json_string + "\n```"
    result_string = call_ai_function(
        function_string, args, description_string, model="gpt-3.5-turbo"
    )
    print("------------ JSON FIX ATTEMPT ---------------")
    print(f"Original JSON: {json_string}")
    print("-----------")
    print(f"Fixed JSON: {result_string}")
    print("----------- END OF FIX ATTEMPT ----------------")

    try:
        json.loads(result_string) 
        return result_string
    except json.JSONDecodeError:  
        return "failed"

def fix_and_parse_json(
    json_to_load: str, try_to_fix_with_gpt: bool = True
):

    with contextlib.suppress(json.JSONDecodeError):
        json_to_load = json_to_load.replace("\t", "")
        return json.loads(json_to_load)

    with contextlib.suppress(json.JSONDecodeError):
        json_to_load = correct_json(json_to_load)
        return json.loads(json_to_load)

###New added
    with contextlib.suppress(json.JSONDecodeError):
        return json.loads(json_to_load,strict = False)
    with contextlib.suppress(json.JSONDecodeError):
        return json.loads(json_to_load.replace('\\','\\\\'),strict = False)
    with contextlib.suppress(json.JSONDecodeError):
        return json.loads(json_to_load,strict = False)

    try:
        brace_index = json_to_load.index("{")
        maybe_fixed_json = json_to_load[brace_index:]
        last_brace_index = maybe_fixed_json.rindex("}")
        maybe_fixed_json = maybe_fixed_json[: last_brace_index + 1]
        return json.loads(maybe_fixed_json)
    except (json.JSONDecodeError, ValueError) as e:
        return try_ai_fix(try_to_fix_with_gpt, e, json_to_load)


def try_ai_fix(
    try_to_fix_with_gpt: bool, exception: Exception, json_to_load: str
):

    if not try_to_fix_with_gpt:
        raise exception
    ai_fixed_json = fix_json(json_to_load, JSON_SCHEMA)

    if ai_fixed_json != "failed":
        return json.loads(ai_fixed_json)
    return {}

def attempt_to_fix_json_by_finding_outermost_brackets(json_string: str):
    try:
        json_pattern = regex.compile(r"\{(?:[^{}]|(?R))*\}")
        json_match = json_pattern.search(json_string)
        if json_match:
            # Extract the valid JSON object from the string
            json_string = json_match.group(0)
            print("Apparently json was fixed.")
        else:
            return {}
    except (json.JSONDecodeError, ValueError):
        json_string = {}
    return fix_and_parse_json(json_string)



def fix_json_using_multiple_techniques(assistant_reply: str):
    assistant_reply_json = fix_and_parse_json(assistant_reply)
    if assistant_reply_json == {}:
        assistant_reply_json = attempt_to_fix_json_by_finding_outermost_brackets(
            assistant_reply
        )
    if assistant_reply_json != {}:
        return assistant_reply_json
    print("Error: The following AI output couldn't be converted to a JSON:\n", assistant_reply)
    return {}
