import uuid
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from ..config.config import ForgeConfig
from .workflow import create_graph # Adjusted import for clarity

def pause(msg="Press Enter to continue..."):
    """Pauses the script and waits for user input."""
    input(f"\n🔹 {msg}")

def main():
    """Runs a single, five-turn chat session with the agent."""
    print("=== 1. Initializing config ===")
    provider = input("Enter provider (openai/gemini/anthropic): ").strip()
    api_key = input("Enter API key (fake ok for test): ").strip()
    model = input("Enter model (press Enter for default): ").strip() or None

    # Load config data.
    cfg = ForgeConfig(provider=provider, api_key=api_key, model=model)
    cfg.save()
    
    # We will use ONE thread_id for the entire test.
    thread_id = str(uuid.uuid4())
    print(f"\n✅ Config saved. Starting chat with Thread ID: {thread_id}")

    pause("Config initialized. Press Enter to start the 5-turn chat session.")

    # --- Main Chat Session ---
    print("\n=== 2. Starting 5-Turn Chat Session ===")
    # The 'with' block ensures the database connection is managed safely.
    with SqliteSaver.from_conn_string(str(ForgeConfig.CONFIG_DB)) as checkpointer:
        graph = create_graph(cfg.llm, checkpointer)
        
        # Loop for a 5-turn conversation.
        for i in range(5):
            print(f"\n--- Turn {i+1}/5 ---")
            msg = input("You: ").strip()
            
            if msg.lower() in ["exit", "quit"]:
                print("Exiting chat early.")
                break
            
            result = graph.invoke(
                {"messages": [HumanMessage(content=msg)]},
                config={"configurable": {"thread_id": thread_id}}
            )
            agent_response = result['messages'][-1]
            print(f"Agent: {agent_response.content}")

    print("\n✅ Chat session is OVER. The database connection has been closed.")
    pause("Press Enter to clean up and delete the configuration.")

    # --- CLEANUP ---
    print("\n=== 3. Deleting config + DB ===")
    ForgeConfig.delete()
    print("✅ Entire .forge folder removed.")
    print("\n🎉 Demo complete.")


if __name__ == "__main__":
    main()
