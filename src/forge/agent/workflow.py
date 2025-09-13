from langchain_core.messages import SystemMessage, BaseMessage
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages

from typing import TypedDict, Annotated

from .prompt import CODING_AGENT_PROMPT
from ..tools.tools import read_file, propose_changes, read_notebook_cells, summarize_dataset
from ..utils.utils import generate_project_tree

# State definition
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# The agent's tools
TOOLS = [read_file, propose_changes, read_notebook_cells, summarize_dataset]

def create_graph(llm, checkpointer):
    """
    Creates and compiles the LangGraph agent with the provided checkpointer.
    """
    llm_with_tools = llm.bind_tools(TOOLS)
    project_structure = generate_project_tree(".", max_depth=5)
    system_prompt = CODING_AGENT_PROMPT.format(PROJECT_STRUCTURE=project_structure)

    def chat_node(state: ChatState):
        """LLM node that may answer or request a tool call."""
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(TOOLS)

    builder = StateGraph(ChatState)
    builder.add_node("chat_node", chat_node)
    builder.add_node("tools", tool_node)
    builder.add_edge(START, "chat_node")
    builder.add_conditional_edges("chat_node", tools_condition)
    builder.add_edge("tools", "chat_node")
    # builder.add_edge("chat_node", END)

    # Compile the graph with the checkpointer included
    return builder.compile(checkpointer=checkpointer)