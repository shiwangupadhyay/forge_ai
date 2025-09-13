import uuid
import gc
import typer
from rich.console import Console
from rich.markdown import Markdown

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from .config.config import ForgeConfig
from .agent.workflow import create_graph


# Create a Typer app for a clean CLI experience
app = typer.Typer(
    name="forge",
    help="An AI coding agent that can inspect, reason about, and modify your codebase.",
    add_completion=False,
    invoke_without_command=True,  # Allows 'forge' to run the chat REPL by default
)

# Use rich for better terminal output
console = Console()


@app.command()
def init(
    provider: str = typer.Option(
        ..., "--provider", "-p", help="LLM provider (e.g., 'openai', 'gemini')"
    ),
    api_key: str = typer.Option(
        ..., "--api-key", "-k", help="Your API key for the provider"
    ),
    model: str = typer.Option(
        None, "--model", "-m", help="The specific model to use (optional)"
    ),
):
    """
    Initialize the Forge agent with your LLM provider and API key.
    """
    if ForgeConfig.CONFIG_FILE.exists():
        console.print(
            "[yellow]Configuration already exists. To re-initialize, please run 'forge stop' first.[/yellow]"
        )
        raise typer.Exit()

    try:
        cfg = ForgeConfig(provider=provider, api_key=api_key, model=model)
        cfg.save()
        console.print(f"[bold green]Configuration saved successfully!, Run `forge` to ignite 🔥[/bold green]")
        console.print(f"Provider: {cfg.provider}, Model: {cfg.model}")
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(1)


def _run_chat_repl(thread_id: str | None):
    """Helper function to contain the main chat loop."""
    try:
        cfg = ForgeConfig.load()
    except FileNotFoundError:
        console.print(
            "[bold red]Configuration not found. Please run 'forge init' first.[/bold red]"
        )
        raise typer.Exit(1)

    if not thread_id:
        thread_id = str(uuid.uuid4())
        forge_ascii = r"""
         _______  _____   ______  ______ _______
        |______ |     | |_____/ |  ____ |______
        |       |_____| |    \_ |_____| |______
                                                
        """

        # Gradient colors
        colors = ["#FFFF33", "#FFD700", "#FFA500", "#FF4500", "#FF0000", "#8B0000"]

        for i, line in enumerate(forge_ascii.splitlines()):
            color = colors[i % len(colors)]
            styled_line = f"[bold {color}]{line}[/bold {color}]"
            console.print(styled_line)

        console.print(
            Markdown(f"**New chat session started. Your Thread ID is:** `{thread_id}`")
        )
        console.print(
            "You can use this ID with the main command to continue this conversation later."
        )

    console.print("[cyan]Type 'exit' or 'quit' to end.[/cyan]")

    with SqliteSaver.from_conn_string(str(ForgeConfig.CONFIG_DB)) as checkpointer:
        graph = create_graph(cfg.llm, checkpointer)

        while True:
            try:
                user_input = console.input("[bold yellow]You: [/bold yellow]")
                if user_input.lower() in ["exit", "quit"]:
                    break

                result = graph.invoke(
                    {"messages": [HumanMessage(content=user_input)]},
                    config={"configurable": {"thread_id": thread_id}},
                )

                agent_response = result["messages"][-1]

                console.print(f"[bold green]Forge:[/bold green] {agent_response.content}")
                if agent_response.tool_calls:
                    console.print(f"[dim]Tool Calls: {agent_response.tool_calls}[/dim]")

            except KeyboardInterrupt:
                break

    console.print("\n[cyan]Chat session ended.[/cyan]")

    # Post-session cleanup options
    if typer.confirm("Do you want to clear all conversation memory?"):
        ForgeConfig.clear_all_memory()
        console.print(
            "[bold green]All conversation memory has been cleared.[/bold green]"
        )

    if typer.confirm(
        "Do you want to delete all Forge data (config and all memory)?"
    ):
        # Explicitly trigger garbage collection to help release the file lock
        # held by the recently closed database connection, which can linger on Windows.
        gc.collect()
        ForgeConfig.delete()
        console.print("[bold green]All Forge data has been deleted.[/bold green]")


@app.callback()
def main(
    ctx: typer.Context,
    thread_id: str = typer.Option(
        None,
        "--thread-id",
        "-t",
        help="Continue a conversation with a specific thread ID.",
    ),
):
    """
    Forge AI Agent CLI.

    Run without a subcommand to start the chat REPL.
    """
    if ctx.invoked_subcommand is None:
        _run_chat_repl(thread_id)


@app.command()
def clear_memory():
    """
    Clear all conversation history from the database.
    """
    ForgeConfig.clear_all_memory()
    console.print('[bold green]🔥 Forge whispers:[/bold green] "All past echoes have been burned away... the slate is clean."')

@app.command()
def stop():
    """
    Delete the entire .forge directory and all its contents.
    """
    if ForgeConfig.CONFIG_DIR.exists():
        if typer.confirm(
            "Are you sure you want to delete the entire .forge directory? This is irreversible."
        ):
            ForgeConfig.delete()
            console.print(
                '[bold green]🌱 Forge breathes anew:[/bold green] "All memory has turned to ash, and a fresh path begins."'
            )
        else:
            console.print("Operation cancelled.")
    else:
        console.print('[italic yellow]⚡ Forge whispers:[/italic yellow] "There\'s nothing here to stop... the fire never even started."')


if __name__ == "__main__":
    app()

