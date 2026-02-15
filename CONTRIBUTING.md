
```markdown
# Contributing to AI Log Analyzer

First, thanks for taking the time to contribute. This project aims to make debugging easier by connecting local log monitoring with AI analysis. Contributions of all sizes are welcome.

## Project Architecture

To help you find your way around the codebase, here is how the system is structured:

* **`main.py`**: The entry point. It loads the config, initializes the monitor, and acts as the central coordinator.
* **`src/monitor.py`**: Handles file system watching. Uses debouncing and buffering to group multi-line stack traces into a single payload.
* **`src/parser.py`**: Uses regex to extract file paths and line numbers from various languages' error logs.
* **`src/analyzer.py`**: Acts as the middleware. It opens the local files referenced in the logs, extracts the surrounding code context, and formats the prompt for the LLM (via LiteLLM).
* **`src/notifier.py`**: Handles sending the final AI analysis to external services.

## What to Work On

If you are looking for something to work on, here are our current priorities:

1. **New Notification Integrations:** We are actively looking to add support for Discord Webhooks and Google Groups. All notification logic should be added to `src/notifier.py`.
2. **Additional Language Parsers:** If you use a language or framework whose stack traces aren't caught by the current regex patterns, please add a new pattern to the `PATTERNS` list in `src/parser.py`.
3. **Bug Fixes & Optimizations:** Feel free to open a PR for any general improvements or bug fixes.

## Local Setup

1. Fork the repository and clone your fork locally:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/ai-log-analyzer.git](https://github.com/YOUR_USERNAME/ai-log-analyzer.git)
   cd ai-log-analyzer

```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```


3. Install the dependencies:
```bash
pip install -r requirements.txt

```


4. Set up your `.env` and `config.yaml` files as outlined in the `README.md`.

## Pull Request Process

1. Create a new branch for your feature or bugfix (`git checkout -b feature/discord-integration`).
2. Keep your code clean and document any new functions.
3. If you add a new parser or notification type, test it locally using a sample log file to ensure it works end-to-end.
4. Commit your changes and push to your fork.
5. Open a Pull Request against the `master` branch of this repository. Include a brief description of what your PR solves.

## Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub. Include as much context as possible, such as sample log outputs and your `config.yaml` setup (with sensitive keys removed).
