# Forge AI: Intelligent Coding Agent

An AI coding agent that can inspect, reason about, and modify your codebase through an interactive command-line interface. Forge AI empowers developers by automating code inspection, proposing changes with user approval, and understanding complex project structures.

## How It Works

Forge AI is built around an advanced agentic architecture powered by `LangGraph`. At its core, it leverages Large Language Models (LLMs) to understand user requests, reason about a codebase, and execute specialized tools to achieve its goals.

1.  **Agentic Workflow**: The agent uses a `StateGraph` to manage its conversation state and decide its next action:
    *   It receives a user message (e.g., "Fix a bug," "Add a feature").
    *   It consults its system prompt (defined in `agent/prompt.py`) which includes a dynamic project structure overview.
    *   It uses the LLM to decide whether to respond directly or call one of its available tools.
2.  **Tool-Use**: The agent is equipped with powerful tools that allow it to interact with the project environment. It calls these tools to inspect files, propose changes, and understand data.
3.  **Interactive Changes**: When the agent proposes a code modification, it generates a clear, colorized diff for the user's review and requires explicit approval before applying any changes, ensuring safety and control.
4.  **Conversation Memory**: All interactions are stored in a SQLite database, allowing the agent to maintain context and continue conversations across sessions using a `thread_id`.

## Key Features

*   **Interactive CLI**: Engage with the AI agent directly from your terminal.
*   **Intelligent Code Modification**: Agent can inspect, reason about, and propose code changes.
*   **Human-in-the-Loop**: All code changes are presented as diffs for user review and approval.
*   **Multi-LLM Support**: Configurable to use various LLM providers (OpenAI, Google Gemini, Anthropic).
*   **Conversation Memory**: Persists chat history across sessions using SQLite.
*   **Project Structure Awareness**: Agent builds a dynamic understanding of your project layout.
*   **Data & Notebook Inspection**: Specialized tools for summarizing datasets and reading Jupyter Notebooks.

## Installation & Usage

### Prerequisites

*   Python 3.8+

### Installation

1.  **Install from PyPI**:
    ```bash
    pip install forge-ai
    ```

### Configuration

Before using Forge AI, you need to initialize it with your preferred LLM provider and API key.

```bash
forge init --provider <provider_name> --api-key <YOUR_API_KEY> [--model <model_name>]
```

**Example:**

*   **OpenAI**:
    ```bash
    forge init --provider openai --api-key sk-xxxx --model gpt-4o-mini
    ```
*   **Google Gemini**:
    ```bash
    forge init --provider gemini --api-key your-gemini-api-key --model gemini-2.5-flash
    ```
*   **Anthropic**:
    ```bash
    forge init --provider anthropic --api-key your-anthropic-api-key --model claude-3-haiku-20240307
    ```

Forge AI will store your configuration in a `.forge/config.json` file in your current working directory.

### Running the Agent

Simply run `forge` to start an interactive chat session with the AI agent:

```bash
forge
```

*   **Continue a Session**: To pick up a previous conversation, use the `--thread-id` option (displayed when a new session starts).
    ```bash
    forge --thread-id <your_thread_id>
    ```
*   **Exit**: Type `exit` or `quit` to end the chat session. You'll be prompted to clear memory or delete all Forge data.

### CLI Commands

*   **`forge init`**: Initialize Forge AI with your LLM provider and API key.
    ```bash
    forge init --provider openai --api-key YOUR_KEY
    ```
*   **`forge clear_memory`**: Clears all conversation history from the SQLite database.
    ```bash
    forge clear_memory
    ```
*   **`forge stop`**: Deletes the entire `.forge` directory, including configuration and all conversation memory. This is irreversible.
    ```bash
    forge stop
    ```
