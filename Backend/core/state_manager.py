from typing import List, Dict, Any, Optional, Union, Callable, Annotated
import operator
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from llm import Message, convert_to_langgraph_message, convert_to_pydantic_message

def last_reducer(left, right):
    # Always return the last value provided
    return right[-1] if isinstance(right, list) and right else right

def dict_merge_reducer(left, right):
    if left is None:
        left = {}
    if right is None:
        right = {}
    merged = left.copy()
    merged.update(right)
    return merged

# Define possible states
class ConversationState(BaseModel):
    messages: Annotated[List[Message], operator.add] = Field(default_factory=list, description="List of messages in the conversation")
    current_state: Annotated[str, last_reducer] = Field(default="idle", description="Current state of the conversation")
    metadata: Annotated[Dict[str, Any], dict_merge_reducer] = Field(default_factory=dict, description="Additional state metadata")
    error: Optional[str] = Field(default=None, description="Error message if any")
    context: Annotated[Dict[str, Any], dict_merge_reducer] = Field(default_factory=dict, description="Context for the current state")

# Define state transition functions
def process_user_input(state: ConversationState) -> ConversationState:
    """Process user input and determine next state"""
    try:
        # Get the last user message
        last_message = state.messages[-1]
        content = last_message.content.lower()
        
        # Determine next state based on content
        if "upload" in content or "file" in content:
            state.current_state = "file_upload"
        elif "search" in content or "find" in content:
            state.current_state = "document_search"
        elif "settings" in content or "configure" in content:
            state.current_state = "settings"
        else:
            state.current_state = "chat"
            
        return state
    except Exception as e:
        state.error = str(e)
        state.current_state = "error"
        return state

def handle_chat(state: ConversationState) -> ConversationState:
    """Handle normal chat interaction"""
    try:
        # Process chat messages
        state.current_state = "idle"
        return state
    except Exception as e:
        state.error = str(e)
        state.current_state = "error"
        return state

def handle_file_upload(state: ConversationState) -> ConversationState:
    """Handle file upload state"""
    try:
        # Process file upload
        state.current_state = "idle"
        return state
    except Exception as e:
        state.error = str(e)
        state.current_state = "error"
        return state

def handle_document_search(state: ConversationState) -> ConversationState:
    """Handle document search state"""
    try:
        # Process document search
        state.current_state = "idle"
        return state
    except Exception as e:
        state.error = str(e)
        state.current_state = "error"
        return state

def handle_settings(state: ConversationState) -> ConversationState:
    """Handle settings state"""
    try:
        # Process settings changes
        state.current_state = "idle"
        return state
    except Exception as e:
        state.error = str(e)
        state.current_state = "error"
        return state

def handle_error_state(state: ConversationState) -> ConversationState:
    """Handle error state"""
    # Log error and attempt recovery
    state.current_state = "idle"
    return state

class StateManager:
    def __init__(self):
        # Create the state graph
        self.workflow = StateGraph(ConversationState)
        
        # Add nodes
        self.workflow.add_node("process_input", process_user_input)
        self.workflow.add_node("chat", handle_chat)
        self.workflow.add_node("file_upload", handle_file_upload)
        self.workflow.add_node("document_search", handle_document_search)
        self.workflow.add_node("settings", handle_settings)
        self.workflow.add_node("error_handling", handle_error_state)
        
        # Define edges
        self.workflow.add_edge("process_input", "chat")
        self.workflow.add_edge("process_input", "file_upload")
        self.workflow.add_edge("process_input", "document_search")
        self.workflow.add_edge("process_input", "settings")
        self.workflow.add_edge("process_input", "error_handling")
        
        # Add edges from each state back to process_input
        for state in ["chat", "file_upload", "document_search", "settings", "error_handling"]:
            self.workflow.add_edge(state, "process_input")
        
        # Set entry point
        self.workflow.set_entry_point("process_input")
        
        # Compile the graph with channel configuration
        self.app = self.workflow.compile()
    
    def process_message(self, message: Message, context: Optional[Dict[str, Any]] = None) -> ConversationState:
        """Process a new message and return the updated state"""
        # Create initial state
        state = ConversationState(
            messages=[message],
            context=context or {}
        )
        
        # Run the state machine
        result = self.app.invoke(state)
        return result
    
    def get_current_state(self, state: ConversationState) -> str:
        """Get the current state of the conversation"""
        return state.current_state
    
    def get_error(self, state: ConversationState) -> Optional[str]:
        """Get any error message from the state"""
        return state.error
    
    def get_context(self, state: ConversationState) -> Dict[str, Any]:
        """Get the current context from the state"""
        return state.context 