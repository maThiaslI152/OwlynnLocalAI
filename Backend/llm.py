from langchain_openai import ChatOpenAI
from typing import List, Dict, Tuple, Any, Optional, Union
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Base LLM configuration
llm = ChatOpenAI(
    openai_api_base="http://localhost:1234/v1",
    openai_api_key="none",
    temperature=0.65,
    max_tokens=8096,
)

# Pydantic models Types
class Message(BaseModel):
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Content of the message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata of the message")
    

class State(BaseModel):
    messages: List[Message] = Field(default_factory=list, description="List of messages in the conversation")
    next_node: str = Field(..., description="Next node to execute")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata of the state")

# Convert Pydantic models to LangGraph nodes
def convert_to_langgraph_message(message: Message) -> Union[HumanMessage, AIMessage]:
    if message.role == "user":
        return HumanMessage(content=message.content)
    return AIMessage(content=message.content)

def convert_to_pydantic_message(message: Union[HumanMessage, AIMessage]) -> Message:
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    return Message(role=role, content=message.content)

# Chat 