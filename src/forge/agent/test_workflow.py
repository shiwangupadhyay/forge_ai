import uuid
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from ..config.config import ForgeConfig
from .workflow import create_graph

def pause(msg="Press Enter to continue..."):
    """Pauses the script and waits for user input."""
    input(f"\n🔹 {msg}")

def main():
    """Runs a workflow to demonstrate persistence across sessions."""
    print("=== 1. Initializing config ===")
    provider = input("Enter provider (openai/gemini/anthropic): ").strip()
    api_key = input("Enter API key (fake ok for test): ").strip()
    model = input("Enter model (press Enter for default): ").strip() or None

    # Load config data.
    cfg = ForgeConfig(provider=provider, api_key=api_key, model=model)
    cfg.save()
    
    # We will use ONE thread_id for the entire test to prove memory is tied to it.
    thread_id = str(uuid.uuid4())
    print(f"\n✅ Config saved. We will use Thread ID: {thread_id} for both sessions.")

    pause("Config initialized. Press Enter to start Session 1.")

    # --- SESSION 1 ---
    print("\n=== 2. Starting Session 1 (2 turns) ===")
    with SqliteSaver.from_conn_string(str(ForgeConfig.CONFIG_DB)) as checkpointer:
        graph = create_graph(cfg.llm, checkpointer)
        
        for i in range(2):
            print(f"\n--- Session 1, Turn {i+1}/2 ---")
            msg = input("You: ").strip()
            
            result = graph.invoke(
                {"messages": [HumanMessage(content=msg)]},
                config={"configurable": {"thread_id": thread_id}}
            )
            agent_response = result['messages'][-1]
            print(f"Agent: {agent_response.content}")

    print("\n✅ Session 1 is OVER. The database connection has been closed.")
    pause("The agent's memory is now persisted on disk. Press Enter to start a new session.")

    # --- SESSION 2 ---
    print("\n=== 3. Starting Session 2 (New Connection) ===")
    print("We will now create a NEW connection and see if the agent remembers.")
    
    with SqliteSaver.from_conn_string(str(ForgeConfig.CONFIG_DB)) as checkpointer:
        # Re-create the graph. In a real app, this would be a new process starting.
        graph = create_graph(cfg.llm, checkpointer)
        
        print("\n--- Session 2, Turn 1/1 ---")
        msg = input("You (ask something about Session 1): ").strip()

        result = graph.invoke(
            {"messages": [HumanMessage(content=msg)]},
            config={"configurable": {"thread_id": thread_id}}
        )
        agent_response = result['messages'][-1]
        print(f"Agent: {agent_response.content}")

    print("\n✅ Session 2 complete. The agent remembered the context from Session 1.")
    pause("Press Enter to clean up and delete the configuration.")

    # --- CLEANUP ---
    print("\n=== 4. Deleting config + DB ===")
    ForgeConfig.delete()
    print("✅ Entire .forge folder removed.")
    print("\n🎉 Demo complete.")


if __name__ == "__main__":
    main()
