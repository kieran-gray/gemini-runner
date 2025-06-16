# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-genai",
#     "typer",
#     "python-dotenv"
# ]
# ///

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from enum import StrEnum
import typer
from google.genai import types

INPUT_MAX_LENGTH = 512

env_path = Path.home() / ".config" / "gemini" / ".env"
load_dotenv(env_path)

GOOGLE_GEMINI_API_TOKEN = os.getenv("GOOGLE_GEMINI_API_TOKEN", "")


class InputValidationException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Exception: {message}")


class Commands(StrEnum):
    CODE = "translate_code"
    TEXT = "translate_text"


TRANSLATE_TEXT_SYSTEM_INSTRUCTION = """
    You are a translation assistant. I will paste text related to an Italian
    car insurance company.
    Your job is to translate it into clear, natural English suitable for 
    professional or customer-facing contexts.

    Preserve the original tone and intent (e.g., legal, commercial, or 
    customer support)

    Use fluent, idiomatic English

    Assume all content is within the context of car insurance in Italy

    Output only the translated version — no explanations unless I ask
"""

TRANSLATE_CODE_SYSTEM_INSTRUCTION = """
    You are a translation assistant. 
    I will paste code related to an Italian car insurance system.
    Your job is to translate it into clear, natural English.

    Only translate human-readable elements: comments, string literals,
    and (if appropriate) variable names

    Preserve code formatting, syntax, and structure exactly

    Assume all content is within the context of car insurance in Italy

    Output only the translated version — no explanations unless I ask
"""


class GeminiClient:
    def __init__(
        self, api_key: str, model: str, client: genai.Client | None = None
    ) -> None:
        self._api_key: str = api_key
        self._model: str = model
        self._client = client or genai.Client(api_key=self._api_key)
        self._command_instructions: dict[str, str] = {}

    def register_command(self, command: str, instructions: str) -> None:
        self._command_instructions[command] = instructions

    def generate(self, command: str, content: str) -> str | None:
        response = self._client.models.generate_content(
            model=self._model,
            config=types.GenerateContentConfig(
                system_instruction=self._command_instructions.get(command, "")
            ),
            contents=content,
        )
        return response.text


app = typer.Typer()
client = GeminiClient(
    api_key=GOOGLE_GEMINI_API_TOKEN, model="gemini-2.0-flash"
)
client.register_command(Commands.CODE, TRANSLATE_CODE_SYSTEM_INSTRUCTION)
client.register_command(Commands.TEXT, TRANSLATE_TEXT_SYSTEM_INSTRUCTION)


def read_input() -> str:
    """Read input from stdin or command line argument."""
    if not sys.stdin.isatty():
        clip_input = sys.stdin.read().strip()
        if not clip_input:
            raise InputValidationException("No clipboard input provided.")
        if len(clip_input) > INPUT_MAX_LENGTH:
            raise InputValidationException(
                f"Input string too long. Input: {len(clip_input)} chars. "
                f"Max: {INPUT_MAX_LENGTH}"
            )
        return clip_input
    raise InputValidationException("No input provided.")


@app.command()
def translate_code(
    content: str = typer.Argument(
        None,
        help="Content to translate. If not provided, will read from stdin.",
    ),
) -> None:
    if content is None:
        content = read_input()

    result = client.generate(command=Commands.CODE, content=content)
    print(result)


@app.command()
def translate_text(
    content: str = typer.Argument(
        None,
        help="Content to translate. If not provided, will read from stdin.",
    ),
) -> None:
    if content is None:
        content = read_input()

    result = client.generate(command=Commands.TEXT, content=content)
    print(result)


if __name__ == "__main__":
    app()
