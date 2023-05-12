from __future__ import annotations
from typing import List, NoReturn, Union, Dict
from Chat import create_chat_completion


class AgentManager():

    def __init__(self):
        self.next_key = 0
        self.agents = {} 


    def create_agent(self, task: str, prompt: str, model: str) -> tuple[int, str]:
        messages = [
            {"role": "user", "content": prompt},
        ]

        agent_reply = create_chat_completion(
            model=model,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": agent_reply})
        key = self.next_key
        self.next_key += 1
        self.agents[key] = (task, messages, model)
        return key, agent_reply

    def message_agent(self, key: str | int, message: str) -> str:

        task, messages, model = self.agents[int(key)]

        # Add user message to message history before sending to agent
        messages.append({"role": "user", "content": message})

        # Start GPT instance
        agent_reply = create_chat_completion(
            model=model,
            messages=messages,
        )

        # Update full message history
        messages.append({"role": "assistant", "content": agent_reply})

        return agent_reply

    def list_agents(self) -> list[tuple[str | int, str]]:

        return [(key, task) for key, (task, _, _) in self.agents.items()]

    def delete_agent(self, key: Union[str, int]) -> bool:

        try:
            del self.agents[int(key)]
            return True
        except KeyError:
            return False
