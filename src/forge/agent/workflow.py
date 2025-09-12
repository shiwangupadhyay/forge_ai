from langchain_core.messages import AnyMessage, SystemMessage
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
from langmem.short_term import SummarizationNode, RunningSummary
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages.utils import count_tokens_approximately

from typing import TypedDict

from .prompt import CODING_AGENT_PROMPT
from config.config import ForgeConfig
from tools.tools import read_file, propose_changes, read_notebook_cells, summarize_dataset
from utils.utils import generate_project_tree

# Load config and setup LLM/db

config = ForgeConfig.load()
conn = config.conn
llm = config.llm

checkpointer = SqliteSaver(conn=conn)

# Tools available to the agent
tools = [read_file, propose_changes, read_notebook_cells, summarize_dataset]
llm_with_tools = llm.bind_tools(tools)

# Project structure injection
PROJECT_STRUCTURE = generate_project_tree(".", max_depth=5)
SYSTEM_PROMPT = CODING_AGENT_PROMPT.format(PROJECT_STRUCTURE=PROJECT_STRUCTURE)

# State definitions
class State(MessagesState):
    context: dict[str, RunningSummary]

class LLMInputState(TypedDict):
    summarized_messages: list[AnyMessage]
    context: dict[str, RunningSummary]

# Summarization
summarization_node = SummarizationNode(
    token_counter=count_tokens_approximately,
    model=llm,
    max_tokens=4096,
    max_tokens_before_summary=4096,
    max_summary_tokens=1024,
)

def chat_node(state: LLMInputState):
    """LLM node that may answer or request a tool call."""
    user_messages = state["summarized_messages"]

    messages = [SystemMessage(content=SYSTEM_PROMPT)] + user_messages

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# Tool node
tool_node = ToolNode(tools)

# Graph builder
builder = StateGraph(State)

builder.add_node("summarize", summarization_node)
builder.add_node("chat_node", chat_node)
builder.add_node("tools", tool_node)

builder.add_edge(START, "summarize")
builder.add_edge("summarize", "chat_node")
builder.add_conditional_edges("chat_node", tools_condition)
builder.add_edge("tools", "chat_node")

graph = builder.compile(checkpointer=checkpointer)