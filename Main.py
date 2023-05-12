from Agent import Agent
from Prompt import construct_prompt
from Memory import get_memory
import os

def check_openai_api_key() -> None:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Please set your OpenAI API key as an environment variable.")
        print("You can get your key from https://beta.openai.com/account/api-keys")
        exit(1)

def main():
    check_openai_api_key()
    full_message_history = []
    triggering_prompt = ("Determine which next command to use, and respond using the format specified above:")
    memory = get_memory()
    next_action_count = 0
    ai_name = ""
    system_prompt = construct_prompt()
    agent = Agent(ai_name=ai_name,
        memory=memory,
        full_message_history=full_message_history,
        next_action_count=next_action_count,
        system_prompt=system_prompt,
        triggering_prompt=triggering_prompt,)
    
    agent.start_interaction_loop()

if __name__ == "__main__":
    main()