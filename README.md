# Gemini Runner

Helper for running commonly used gemini commands.

## Setup

Run:

```
echo "GOOGLE_GEMINI_API_TOKEN=your_api_key_here" > ~/.config/gemini/.env
chmod 600 ~/.config/gemini/.env
```


Input api token.

Install uv.

In .zshrc / .bashrc:


```
alias gemclip="xclip -o | uv run {PATH_TO_SCRIPT}/gemini_runner.py translate-code"
alias gemcode='f() {uv run {PATH_TO_SCRIPT}/gemini_runner.py translate-code "$1"};f'
alias gemtext='f() {uv run {PATH_TO_SCRIPT}/gemini_runner.py translate-text "$1"};f'
```

For macos use `pbpaste` instead of `xclip`

