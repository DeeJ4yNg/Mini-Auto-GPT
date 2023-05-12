from __future__ import annotations

import os
from typing import Type
import yaml


class AIConfig:

    def __init__(
        self, ai_name: str = "", ai_role: str = "", ai_goals: list | None = None
    ) -> None:

        if ai_goals is None:
            ai_goals = []
        self.ai_name = ai_name
        self.ai_role = ai_role
        self.ai_goals = ai_goals

    SAVE_FILE = os.path.join(os.path.dirname(__file__), "..", "ai_settings.yaml")

    @staticmethod
    def load(config_file: str = SAVE_FILE) -> "AIConfig":

        try:
            with open(config_file, encoding="utf-8") as file:
                config_params = yaml.load(file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            config_params = {}

        ai_name = config_params.get("ai_name", "")
        ai_role = config_params.get("ai_role", "")
        ai_goals = config_params.get("ai_goals", [])
        # type: Type[AIConfig]
        return AIConfig(ai_name, ai_role, ai_goals)

    def save(self, config_file: str = SAVE_FILE) -> None:

        config = {
            "ai_name": self.ai_name,
            "ai_role": self.ai_role,
            "ai_goals": self.ai_goals,
        }
        with open(config_file, "w", encoding="utf-8") as file:
            yaml.dump(config, file, allow_unicode=True)

    def construct_full_prompt(self) -> str:

        prompt_start = (
            "You are an assistant only allowed to use Powershell script to complete your tasks."
            " Your decisions must always be made independently without"
            " seeking user assistance. Play to your strengths as an LLM and pursue"
            " simple strategies with no legal complications."
            " If you are unable to complete the goals below with Powershell script, just reply I can't do it with Powershell."
        )

        from Prompt import get_prompt

        full_prompt = (
            f"You are {self.ai_name}, {self.ai_role}\n{prompt_start}\n\nGOALS:\n\n"
        )
        for i, goal in enumerate(self.ai_goals):
            full_prompt += f"{i+1}. {goal}\n"

        full_prompt += f"\n\n{get_prompt()}"
        print(full_prompt)
        return full_prompt
