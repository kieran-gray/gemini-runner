# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-genai",
#     "typer",
#     "python-dotenv"
# ]
# ///

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv
from google.genai import Client, types
from rich.progress import Progress, SpinnerColumn, TextColumn

env_path = Path.home() / ".config" / "gemini" / ".env"
load_dotenv(env_path)

GOOGLE_GEMINI_API_TOKEN = os.getenv("GOOGLE_GEMINI_API_TOKEN", "")
INPUT_MAX_LENGTH = 2000


class InputValidationException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Exception: {message}")


class GeminiCommandNotFoundException(Exception):
    def __init__(self, command: str) -> None:
        super().__init__(f"Exception: Command '{command}' not found.")


class GeminiModelNotFoundException(Exception):
    def __init__(self, model: str) -> None:
        super().__init__(
            f"Exception: Model '{model}' not found."
            "Use command `list-models` for supported models."
        )


@dataclass
class GeminiCommand:
    command: str
    model: str
    system_instructions: str

    def to_dict(self) -> dict[str, str]:
        return {
            "command": self.command,
            "model": self.model,
            "system_instructions": self.system_instructions,
        }


class GeminiClient:
    def __init__(self, api_key: str, client: Client | None = None) -> None:
        self._api_key: str = api_key
        self._client: Client | None = client
        self._commands: dict[str, GeminiCommand] = {}
        self._config_path = Path(__file__).parent / "commands.json"
        self._default_model: str = "gemini-2.0-flash"

    def _get_client(self) -> Client:
        """Lazy load client."""
        if not self._client:
            self._client = Client(api_key=self._api_key)
        return self._client

    def list_supported_models(self) -> list[str]:
        client = self._get_client()
        model_names = [
            getattr(model, "name", "").lstrip("models/")
            for model in client.models.list()
            if model.supported_actions
            and "generateContent" in model.supported_actions
        ]
        return model_names

    def _validate_model(self, model: str) -> None:
        if model not in self.list_supported_models():
            raise GeminiModelNotFoundException(model=model)

    def load_commands(self) -> None:
        if not self._config_path.is_file():
            return

        with open(self._config_path) as f:
            config = json.load(f)
        for gemini_command in config:
            self.register_command(
                command=gemini_command["command"],
                model=gemini_command.get("model"),
                system_instructions=gemini_command.get("system_instructions"),
            )

    def save_commands(self) -> None:
        with open(self._config_path, "w") as f:
            json.dump(self.list_commands(), f)

    def register_command(
        self, command: str, model: str | None, system_instructions: str | None
    ) -> None:
        if model:
            self._validate_model(model)

        self._commands[command] = GeminiCommand(
            command=command,
            model=model or self._default_model,
            system_instructions=system_instructions or "",
        )

    def list_commands(self) -> list[dict[str, str]]:
        return [command.to_dict() for command in self._commands.values()]

    def generate(self, command: str, content: str) -> str | None:
        gemini_command = self._commands.get(command)
        if not gemini_command:
            raise GeminiCommandNotFoundException(command=command)

        client = self._get_client()

        response = client.models.generate_content(
            model=gemini_command.model,
            config=types.GenerateContentConfig(
                system_instruction=gemini_command.system_instructions
            ),
            contents=content,
        )
        return response.text


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


app = typer.Typer()


def get_client() -> GeminiClient:
    client = GeminiClient(api_key=GOOGLE_GEMINI_API_TOKEN)
    client.load_commands()
    return client


@app.command()
def run(command: str, content: str = typer.Argument(default=None)) -> None:
    if content is None:
        content = read_input()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Thinking...", total=None)
        client = get_client()
        result = client.generate(command=command, content=content)
    print(result)


@app.command()
def register(
    command: str,
    model: str | None = None,
    instructions: str | None = None,
) -> None:
    client = get_client()
    client.register_command(
        command=command, model=model, system_instructions=instructions
    )
    client.save_commands()


@app.command()
def list_commands(verbose: Annotated[bool, typer.Option()] = False) -> None:
    client = get_client()
    commands = client.list_commands()
    if verbose:
        print(json.dumps(commands, indent=4))
    else:
        command_names = [command["command"] for command in commands]
        print(json.dumps(command_names, indent=4))


@app.command()
def list_models() -> None:
    client = get_client()
    print(json.dumps(client.list_supported_models(), indent=4))


if __name__ == "__main__":
    app()
