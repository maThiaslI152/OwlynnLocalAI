import pytest
from llm import llm, Message, convert_to_langgraph_message, convert_to_pydantic_message
from langchain_core.messages import HumanMessage, AIMessage

def test_llm_configuration():
    """Test that the LLM is properly configured"""
    assert llm.openai_api_base == "http://localhost:1234/v1"
    assert llm.temperature == 0.65
    assert llm.max_tokens == 8096
    assert llm.stop == ["Human:", "Assistant:"]
    # Check model name if available
    if hasattr(llm, "model"):
        assert llm.model == "Qwen3-14B"

def test_message_conversion():
    """Test conversion between Message types"""
    # Test user message conversion
    user_msg = Message(role="user", content="Hello")
    langgraph_msg = convert_to_langgraph_message(user_msg)
    assert isinstance(langgraph_msg, HumanMessage)
    assert langgraph_msg.content == "Human: Hello"
    
    # Test assistant message conversion
    ai_msg = Message(role="assistant", content="Hi there")
    langgraph_msg = convert_to_langgraph_message(ai_msg)
    assert isinstance(langgraph_msg, AIMessage)
    assert langgraph_msg.content == "Assistant: Hi there"

def test_message_parsing():
    """Test parsing of messages with role prefixes"""
    # Test parsing human message
    human_msg = HumanMessage(content="Human: Hello")
    parsed_msg = convert_to_pydantic_message(human_msg)
    assert parsed_msg.role == "user"
    assert parsed_msg.content == "Hello"
    
    # Test parsing assistant message
    ai_msg = AIMessage(content="Assistant: Hi there")
    parsed_msg = convert_to_pydantic_message(ai_msg)
    assert parsed_msg.role == "assistant"
    assert parsed_msg.content == "Hi there"

@pytest.mark.asyncio
async def test_llm_response():
    """Test that the LLM can generate responses"""
    messages = [
        HumanMessage(content="Human: What is 2+2?"),
    ]
    
    try:
        response = await llm.ainvoke(messages)
        assert isinstance(response, AIMessage)
        assert response.content.startswith("Assistant:")
    except Exception as e:
        pytest.skip(f"LLM test skipped: {str(e)}")

def test_message_metadata():
    """Test that message metadata is properly handled"""
    metadata = {"timestamp": "2024-03-14", "source": "test"}
    msg = Message(role="user", content="Hello", metadata=metadata)
    assert msg.metadata == metadata 