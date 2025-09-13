# Forge AI: Your Coding Agent

An intelligent AI coding agent that can inspect, reason about, and safely modify your codebase. Forge AI provides an interactive command-line interface to empower developers with an AI assistant directly in their projects.

## Key Features

*   **Intelligent Code Inspection**: Utilizes tools to `read_file`, `read_notebook_cells`, and `summarize_dataset` to understand your project context.
*   **Reasoning and Planning**: Employs an advanced LangGraph workflow to formulate plans and execute steps to address your requests.
*   **Safe Code Modification**: Proposes changes via `propose_changes` tool, showing a detailed diff and requiring explicit user approval before any file modifications.
*   **Multi-LLM Support**: Configurable with various LLM providers including OpenAI, Google Gemini, and Anthropic.
*   **Persistent Memory**: Remembers past conversations and context across sessions using SQLite checkpointing.
*   **CLI-First Experience**: Seamless integration into your development workflow via a `typer`-powered command-line interface.

## Project Structure

```
.
├── LICENSE
├── pyproject.toml
├── requirements.txt
└── src/
    └── forge/
        ├── agent/
        │   ├── prompt.py       # Core AI agent's system prompt and instructions
        │   ├── workflow.py     # Defines the LangGraph agent's state and flow
        │   └── test_workflow.py # Example for testing the agent workflow
        ├── cli.py              # Main CLI application (Typer)
        ├── config/
        │   ├── config.py       # Manages LLM configuration and persistence
        │   └── constants.py    # LLM provider details and defaults
        ├── tools/
        │   ├── tools.py        # Definitions of the agent's callable tools
        │   └── tool_utils.py   # Helper functions for tools (e.g., diff, data parsing)
        └── utils/
            └── utils.py        # Utility functions (e.g., project tree generation)
```

## Technologies Used

*   **Python**: Primary development language.
*   **LangChain**: Framework for developing applications powered by language models.
*   **LangGraph**: Library for building stateful, multi-actor applications with LLMs, forming the core of the agent's reasoning.
*   **Typer**: Modern, fast, and easy-to-use library for building CLI applications.
*   **Rich**: For beautiful terminal output (syntax highlighting, diffs, console styling).
*   **SQLite**: Used for persistent conversation memory/checkpoints by `langgraph-checkpoint-sqlite`.
*   **LLM Providers**: OpenAI, Google Gemini, Anthropic (configurable).

## Installation & Usage

### Prerequisites

*   Python 3.8+
*   An API key for one of the supported LLM providers (e.g., OpenAI, Google, Anthropic).

### Installation

It is recommended to install `forge-ai` using `pipx` for a clean CLI experience, isolating it from your other Python projects:

```bash
pip install pipx
pipx install . # If cloned locally, run from root
# Or from PyPI (once available)
# pipx install forge-ai
```

Alternatively, you can install it using `pip`:

```bash
# Clone the repository
git clone https://github.com/shiwangupadhyay/forge_ai.git
cd forge_ai

# Install dependencies
pip install -r requirements.txt
# Or using pyproject.toml
pip install .

# Make the 'forge' command available (if not using pipx)
# This might depend on your system's PATH configuration
```

### Configuration

Before using Forge AI, you need to initialize it with your LLM provider and API key:

```bash
forge init --provider <provider_name> --api-key <your_api_key> [--model <model_name>]
```

**Example:**

```bash
forge init --provider openai --api-key sk-YOUR_OPENAI_KEY
forge init --provider gemini --api-key YOUR_GEMINI_KEY --model gemini-1.5-flash
forge init --provider anthropic --api-key YOUR_ANTHROPIC_KEY
```

Supported providers: `openai`, `gemini`, `anthropic`.

### Starting a Chat Session

Run `forge` without any subcommands to start an interactive chat REPL (Read-Eval-Print Loop) with the AI agent.

```bash
forge
```

To continue a previous conversation, use the `--thread-id` option (the ID will be provided when a new session starts):

```bash
forge --thread-id <your_thread_id>
```

### Agent Interaction Example

When you interact with Forge AI, it follows a structured approach:

1.  **Plan**: The agent formulates a plan (2-4 bullets) for the next step.
2.  **Tool Call**: The agent calls one of its internal tools based on the plan.
3.  **Result Summary**: After the tool executes, the agent summarizes the output.
4.  **Next Plan**: Based on the results, the agent forms a new plan and calls the next tool.

**Example Flow (simplified for clarity):**

```bash
You: Can you check the `src/utils/utils.py` file for any issues?

Forge:
Plan:
- Inspect src/utils/utils.py to understand its purpose.
- Use read_file to fetch the file content.
Tool call:
read_file("src/utils/utils.py")

<Tool Output: Content of utils.py is displayed by the agent or processed internally.>

Forge:
Result summary:
- The `generate_project_tree` function is present.
Next Plan:
- Analyze the function logic for potential improvements.
- Suggest a change using propose_changes.
Tool call:
propose_changes(
  "src/utils/utils.py",
  new_content="<full file text with suggested changes>"
)

<Diff is shown in terminal for user review>
Apply changes to src/utils/utils.py? [y/N]: y

Forge:
Result summary:
- File updated successfully.
Next Plan:
- Suggest running relevant tests or manual verification.
```

### Agent Commands

*   `forge init`: Initialize the agent with your LLM provider and API key.
*   `forge`: Start an interactive chat REPL.
*   `forge --thread-id <ID>`: Continue a conversation.
*   `forge clear-memory`: Deletes all conversation history but keeps your LLM configuration.
*   `forge stop`: Deletes the entire `.forge` directory, including configuration and all conversation memory. This is irreversible.

## Agent Capabilities & Mechanics

Forge AI operates as a LangGraph agent, leveraging a predefined set of tools to achieve its goals.

### Agent Workflow (Simplified)

The agent's core loop involves:

1.  Receiving a user message.
2.  The LLM, guided by a comprehensive system prompt (`src/forge/agent/prompt.py`), generates a plan and decides which tool to use.
3.  The chosen tool (`src/forge/tools/tools.py`) is executed.
4.  The tool's output is fed back to the LLM.
5.  This loop continues until the agent deems the task complete or requires further user input.

### Available Tools

The agent can utilize the following tools:

*   **`read_file(path: str)`**: Reads the content of any text file. Essential for understanding existing code.
*   **`propose_changes(path: str, new_content: str)`**: The primary tool for modifying files. It generates a diff, presents it to the user, and only applies changes upon explicit user approval. This ensures safety and user control.
*   **`read_notebook_cells(path: str)`**: Specifically designed to extract and concatenate cell sources from Jupyter notebooks (`.ipynb`), allowing the agent to analyze notebook content.
*   **`summarize_dataset(path: str)`**: Inspects data files (CSV, TSV, JSON, NDJSON) to provide a summary including schema and sample rows, aiding in data-driven reasoning.

### Supported LLM Providers

Forge AI supports integration with popular LLM APIs:

*   **OpenAI**: `gpt-4o-mini` (default), `gpt-4`, etc.
*   **Google Gemini**: `gemini-2.5-flash` (default), `gemini-1.5-pro`, etc.
*   **Anthropic**: `claude-3-haiku-20240307` (default), `claude-3-opus`, etc.

You specify your preferred provider during the `forge init` step.

### Conversation Memory

The agent maintains conversation memory using `langgraph-checkpoint-sqlite`, storing chat history in a local `.forge/memory.db` file. This allows the agent to recall previous interactions and maintain context across sessions, enabling long-running or multi-step tasks.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.