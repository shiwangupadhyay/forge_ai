# Forge: The AI Coding Agent

An intelligent agent designed to inspect, reason about, and safely modify your codebase, Jupyter notebooks, and datasets. Forge empowers developers by automating code understanding, refactoring suggestions, and data insights directly from the command line.

## Project Structure

```
.
├── LICENSE
├── pyproject.toml
├── README.md
└── src/
    └── forge/
        ├── agent/             # Core AI agent logic, workflow, and system prompt
        │   ├── prompt.py      # The detailed system prompt guiding the agent's behavior
        │   ├── test_workflow.py # Example for testing agent persistence
        │   └── workflow.py    # LangGraph definition for the agent's state and transitions
        ├── cli.py             # Typer CLI application entry point for user interaction
        ├── config/            # Configuration management for LLM providers and persistence
        │   ├── config.py      # Handles saving/loading configuration and database operations
        │   └── constants.py   # Maps LLM providers to their LangChain classes and default models
        ├── tools/             # Custom tools the AI agent can use to interact with the environment
        │   ├── tools.py       # Definitions of `read_file`, `propose_changes`, etc.
        │   └── tool_utils.py  # Helper functions for tools (e.g., diff generation, data parsing)
        └── utils/
            └── utils.py       # General utility functions, e.g., project tree generation
```

## Key Features

*   **Intelligent Code Inspection**: Read and understand source code files.
*   **Controlled Code Modification**: Propose and apply changes to files with user approval via unified diffs.
*   **Jupyter Notebook Analysis**: Extract and summarize content from `.ipynb` files.
*   **Dataset Summarization**: Analyze and provide schema/sample rows for CSV, TSV, JSON, and NDJSON files.
*   **Interactive Chat REPL**: Engage with the agent in a conversational command-line interface.
*   **Persistent Conversation Memory**: Continue sessions across restarts using SQLite-backed memory.
*   **Configurable LLM Providers**: Support for OpenAI, Google Gemini, and Anthropic models.
*   **Clear & Concise Output**: Utilizes `rich` for enhanced terminal experience.

## Technologies Used

*   **Python 3.9+**
*   **LangChain**: For LLM integration and message handling.
*   **LangGraph**: To define and manage the agent's stateful, multi-turn workflow.
*   **Typer**: For building a robust and user-friendly command-line interface.
*   **Rich**: For beautiful and informative terminal output.
*   **SQLite**: For persisting conversation memory across sessions.

## Installation & Usage

### Prerequisites

Ensure you have Python 3.9 or higher installed.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/shiwangupadhyay/forge-ai-agent.git
    cd forge-ai-agent
    ```
2.  **Install the package in editable mode:**
    ```bash
    pip install .
    ```
    This makes the `forge` command available in your terminal.

### Configuration (`forge init`)

Before using the agent, you need to configure your LLM provider and API key.

```bash
forge init --provider openai --api-key sk-your-openai-key --model gpt-4o-mini
# OR
forge init --provider gemini --api-key your-gemini-key --model gemini-2.5-flash
# OR
forge init --provider anthropic --api-key sk-your-anthropic-key --model claude-3-haiku-20240307
```

This command creates a `.forge` directory in your current working directory, which stores your `config.json` and `memory.db` files.

### Starting a Chat Session

Run the `forge` command without any subcommands to start an interactive chat REPL:

```bash
forge
```

To continue a previous conversation, use the `--thread-id` option (the ID is provided when a new session starts):

```bash
forge --thread-id <your-session-thread-id>
```

Type `exit` or `quit` to end the session.

## Agent Capabilities

Forge is powered by a LangGraph agent that leverages a set of specialized tools to interact with your local environment, guided by a sophisticated system prompt.

### Core Agent Logic

The agent operates based on a detailed system prompt (`src/forge/agent/prompt.py`) that guides its reasoning, planning, and tool-calling decisions. It adheres to a strict "Plan → Tool Call → Analyze → Next Plan" workflow, ensuring transparent and controlled interactions. The agent's conversational memory is managed by LangGraph's `SqliteSaver`, enabling stateful conversations that persist across sessions.

### Agent Tools

The agent can utilize the following custom tools to fulfill user requests:

*   **`read_file(file_path: str)`**:
    Reads and returns the entire content of a specified text file. Useful for inspecting existing code or documentation.

*   **`propose_changes(file_path: str, new_content: str)`**:
    This is the primary tool for modifying files. It reads the existing content, generates a colorized unified diff, and prompts the user for approval in the terminal before applying any changes. This ensures human oversight for all modifications.

*   **`read_notebook_cells(file_path: str)`**:
    Reads a Jupyter Notebook (`.ipynb`) and extracts all cell source content, providing a consolidated view for analysis.

*   **`summarize_dataset(file_path: str)`**:
    Inspects data files (CSV, TSV, JSON, NDJSON) and provides a summary including schema, inferred types, and a few sample rows. Essential for understanding data before suggesting data-driven code changes.

## CLI Commands

*   **`forge`**: Starts the interactive chat REPL. Use `--thread-id` to resume a session.
*   **`forge init --provider <provider> --api-key <key> [--model <model>]`**: Initializes the agent's configuration.
*   **`forge clear_memory`**: Deletes all conversation history from the local SQLite database.
*   **`forge stop`**: Deletes the entire `.forge` directory, including configuration and all conversation memory. This is irreversible and requires confirmation.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.