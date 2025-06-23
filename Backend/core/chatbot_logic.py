# backend/core/chatbot_logic.py

import os
from typing import List, Dict, Any

# LangChain components
# Using OpenAI compatible classes for LM Studio
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage, AIMessage

# LangGraph components
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

# LangGraph Redis Checkpoint Saver for STM
from langgraph_checkpoint_redis import RedisSaver

# For Chroma Vector Store
from langchain_community.vectorstores import Chroma

# --- Configuration & Initialization ---

# Environment variables for service connections
# REDIS_URL from the blog post is 'redis://localhost:6379'
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379") # Ensure this matches your Docker Redis service
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db") # Path for Chroma persistence

# LM Studio configuration (Assuming it mimics OpenAI API)
# LM Studio typically runs on localhost:1234 by default for its OpenAI API
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
# For local models, API key might not be strictly needed, but some clients require a placeholder
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "not-needed") # Placeholder or actual key if set in LM Studio

# Initialize LLM (Qwen3-14b via LM Studio as OpenAI API)
llm = ChatOpenAI(
    base_url=LM_STUDIO_BASE_URL,
    api_key=LM_STUDIO_API_KEY,
    model_name="qwen3-14b-4bit", # Model name as listed in LM Studio
    temperature=0.7
)

# Initialize Embedding Model (for Chroma)
# Also assuming LM Studio can serve embeddings via OpenAI API compatible endpoint
embeddings = OpenAIEmbeddings(
    base_url=LM_STUDIO_BASE_URL,
    api_key=LM_STUDIO_API_KEY,
    model="nomic-embed-text", # Or whatever embedding model LM Studio exposes
)

# Initialize Chroma Vector Store
# In a real application, you'd load from persistence if it exists
vectorstore = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)

# --- RAG Document Loading and Indexing (Moved to a separate function/script for production) ---
def initialize_chroma_db(docs_path: str = "data/raw_documents/"):
    """
    Initializes or updates the Chroma DB with documents from the specified path.
    This should ideally be run as a separate script or on startup once.
    """
    if not os.path.exists(docs_path) or not os.listdir(docs_path):
        print("No raw documents found, using dummy data for Chroma DB.")
        docs = [
            Document(page_content="The project Owlynn aims to develop a local, high-performance LLM chatbot."),
            Document(page_content="It will integrate retrieval-augmented generation (RAG) capabilities for research tasks."),
            Document(page_content="Owlynn supports PDF and screenshot reading, and file comprehension."),
            Document(page_content="It features efficient memory management and secure data handling."),
            Document(page_content="The architecture is flexible, suitable for diverse document types."),
            Document(page_content="Qwen3-14b 4bit MLX is used as the local large language model."),
            Document(page_content="The chatbot will use LangChain for orchestration and FastAPI for the backend API."),
            Document(page_content="Vue.js is chosen as the frontend framework for the user interface."),
            Document(page_content="Local LLM hosting is managed via LM Studio."),
            Document(page_content="Data privacy and security are paramount for Owlynn.")
        ]
    else:
        # In a real application: Load documents from docs_path using LangChain DocumentLoaders
        # Example: from langchain_community.document_loaders import PyPDFLoader
        # loader = PyPDFLoader(f"{docs_path}/your_document.pdf")
        # docs = loader.load()
        print(f"Loading documents from {docs_path} and updating Chroma DB (Placeholder).")
        docs = [Document(page_content="Placeholder for documents from disk.")] # Replace with actual loading

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(docs)

    # Add or update documents in Chroma
    # Make sure your ChromaDB service is running and accessible if you are not using an in-memory client
    vectorstore.add_documents(split_docs)
    vectorstore.persist()
    print("Chroma DB initialized/updated.")

# Call this once during application startup or via a separate script
initialize_chroma_db()

# --- LangGraph State Definition ---
class GraphState(TypedDict):
    question: str
    chat_history: List[Any]
    generation: str | None
    documents: List[Document]

# --- LangGraph Nodes ---

def retrieve_node(state: GraphState) -> GraphState:
    print("---RETRIEVE NODE---")
    question = state["question"]
    chat_history = state["chat_history"]

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """Given a chat history and the latest user question \
            which might reference context in the chat history, formulate a standalone question \
            which can be understood without the chat history. Do NOT answer the question, \
            just rephrase it if necessary and otherwise return it as is."""),
            ("placeholder", "{chat_history}"),
            ("human", "{question}"),
        ]
    )

    if chat_history:
        context_chain = contextualize_q_prompt | llm
        standalone_question = context_chain.invoke({"chat_history": chat_history, "question": question}).content
        print(f"Standalone question: {standalone_question}")
    else:
        standalone_question = question

    documents = vectorstore.as_retriever().invoke(standalone_question)
    return {"documents": documents, "question": question, "chat_history": chat_history}

def generate_node(state: GraphState) -> GraphState:
    print("---GENERATE NODE---")
    question = state["question"]
    documents = state["documents"]
    chat_history = state["chat_history"]

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """You are an assistant for question-answering tasks. \
            Use the following retrieved context to answer the question. \
            If you don't know the answer, just say that you don't know. \
            Keep the answer concise and accurate.

            Context: {context}"""),
            ("placeholder", "{chat_history}"),
            ("human", "{question}"),
        ]
    )

    context = "\n\n".join([doc.page_content for doc in documents])

    generation_chain = qa_prompt | llm

    # Pass chat_history to the generation chain
    generation = generation_chain.invoke({
        "question": question,
        "context": context,
        "chat_history": chat_history
    }).content # Access .content for ChatModel output

    return {"question": question, "documents": documents, "generation": generation, "chat_history": chat_history}

# --- Build the LangGraph Workflow ---

workflow = StateGraph(GraphState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app_graph = workflow.compile()

# --- LangGraph Redis Checkpoint Saver for STM ---
# As per the Redis blog post <sup data-citation=""><a href="#" title="Invalid citation format">[citation:redis]</a></sup>
memory = RedisSaver(redis_url=REDIS_URL)

# --- PostgreSQL LTM (Conceptual Integration) ---
# For LTM beyond chat history (e.g., user profiles, facts):
# You would interact with PostgreSQL using a separate client library (e.g., psycopg2, SQLAlchemy)
# either directly in nodes or in utility functions.
#
# For chat history as LTM:
# You could still use `PostgresChatMessageHistory` and load/save to it.
# However, LangGraph's checkpointing with RedisSaver already handles conversation
# persistence effectively for the agent's internal state.
# You might use Postgres for archiving full conversation transcripts
# after a session concludes, or for user-specific long-term knowledge.


# --- The Main Processing Function for FastAPI ---

async def process_chat_query(user_query: str, session_id: str = "default_session") -> str:
    """
    Processes a user's chat query using the LangGraph RAG pipeline with Redis STM.
    """
    # The 'thread_id' for RedisSaver acts as the session_id
    thread_id = {"configurable": {"thread_id": session_id}}

    # The LangGraph `stream` method will automatically handle loading/saving
    # state to Redis when a `checkpoint` (memory) is passed.
    # The 'inputs' are for the current turn.
    inputs = {"question": user_query, "chat_history": []} # chat_history is loaded by RedisSaver

    # We need to manually load chat history from the memory for the contextualization prompt
    # LangGraph's memory handles checkpoints; for prompt input, we retrieve explicitly.
    # This ensures the LLM sees the full history for rephrasing.
    loaded_state = await memory.aget_state(thread_id)
    if loaded_state and loaded_state.values.get("chat_history"):
        inputs["chat_history"] = loaded_state.values["chat_history"]


    # Execute the graph with checkpointing enabled
    final_state = None
    async for state in app_graph.astream(inputs, config=thread_id, checkpoint=memory):
        final_state = state
        print(f"Current state: {state}") # For debugging purposes

    if final_state and final_state["generation"]:
        ai_response = final_state["generation"]
    else:
        ai_response = "I'm sorry, I couldn't generate a response."

    # The memory `checkpoint` handles saving the state including updated chat_history.
    # We might manually add the latest human/AI message to the history if needed for external use,
    # but the LangGraph state already includes it after `generate_node`.

    return ai_response