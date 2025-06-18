# Gemini Runner

Helper for running commonly used gemini commands.

## Setup

Only the `gemini_runner.py` script is required. Either download it on its own or clone the repo.

### Prerequisites

uv is required to install the dependencies and run the script.

Install uv with:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
``` 
or check the uv docs for other methods.

### Authenticating

Set up your Gemini auth by creating a `.env` file in the directory `~/.config/gemini`.

Add your token with the following command:

```
echo "GOOGLE_GEMINI_API_TOKEN=<your_api_key_here>" > ~/.config/gemini/.env
chmod 600 ~/.config/gemini/.env
```

## Usage

### Register a command:
* `register`

Arguments (required)
*  `command`

Options (not required)

* `--model`
* `--instructions`

For example:

```
uv run gemini_runner.py register kitty --model gemini-2.5-pro-preview-06-05 --instructions "Pretend that you are a cat. Only answer with 'meow'."
```

### Run a command

* `run`

Arguments (required)
* `content`

For example:

```
uv run gemini_runner.py run kitty "Tell me something profound"
```

### List available commands:

* `list-commands`

Flags

* `--verbose`

For example:

```
uv run gemini_runner.py list-commands
```

### List available models:

* `list-models`

For example:

```
uv run gemini_runner.py list-models
```


## Setting aliases

In .zshrc / .bashrc:

Example
```
alias gemclip="xclip -o | uv run {PATH_TO_SCRIPT}/gemini_runner.py run translate-code"
alias gemcode='f() {uv run {PATH_TO_SCRIPT}/gemini_runner.py run translate-code "$1"};f'
alias gemtext='f() {uv run {PATH_TO_SCRIPT}/gemini_runner.py run translate-text "$1"};f'
```
