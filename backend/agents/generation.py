"""Generation Agent - Uses LLM (Gemini/Ollama) to generate answer from context."""

from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Import centralized LLM provider with fallback
from llm_provider import get_llm


def _format_context(chunks: list) -> str:
    out = []
    for i, c in enumerate(chunks, 1):
        content = c.get("content", "") if isinstance(c, dict) else str(c)
        meta = c.get("metadata", {}) if isinstance(c, dict) else {}
        src = meta.get("source", "unknown")
        page = meta.get("page", "?")
        out.append(f"[{i}] (Source: {src}, Page {page})\n{content}")
    return "\n\n---\n\n".join(out)


def generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generation Agent: Uses Gemini to generate answer from reranked chunks and conversation history.
    """
    query = state.get("query", "")
    history = state.get("conversation_history", [])
    
    # Check if web search was used
    used_web_search = state.get("needs_web_search", False) and state.get("relevance_score", 10) < 5
    
    # If web search was triggered, use retrieved_chunks (which contain web results)
    # Otherwise use reranked_chunks (which are reranked document chunks)
    if used_web_search:
        chunks = state.get("retrieved_chunks", [])
        print(f"[Generation] Using web search results ({len(chunks)} chunks)")
    else:
        chunks = state.get("reranked_chunks", [])
        print(f"[Generation] Using knowledge base documents ({len(chunks)} chunks)")

    context = _format_context(chunks) if chunks else "No relevant information found."

    # Update system prompt based on source
    # Define prompt template
    if used_web_search:
        system = (
            "You are an expert assistant. Provide clear, accurate answers based on the web search results provided.\n\n"
            "Critical rules:\n"
            "1. OUTPUT FORMAT: Write in plain text only. Do NOT use markdown (no #, ##, ###, *, **, bullet points, or headers). Use natural paragraphs and sentences instead.\n"
            "2. ANSWER DIRECTLY: Use the information from the web search results to answer comprehensively.\n"
            "3. TONE: Answer directly and naturally. Don't mention 'the search results' or 'according to'.\n"
            "4. ACCURACY: Provide factual, informative answers based on the search results.\n"
            "5. STRUCTURE: Use clear paragraphs.\n"
            "Provide focused, professional responses in plain text."
        )
    else:
        system = (
            "You are an expert assistant. Provide clear, accurate answers based solely on the provided context.\n\n"
            "Critical rules:\n"
            "1. OUTPUT FORMAT: Write in plain text only. Do NOT use markdown (no #, ##, ###, *, **, bullet points, or headers). Use natural paragraphs and sentences instead.\n"
            "2. CONTEXT RELEVANCE: Use ONLY passages that directly answer the user's question. If a passage is about a different topic or document (e.g., unrelated guides, manuals), IGNORE it completely. Do not mention, footnote, or acknowledge irrelevant passages.\n"
            "3. TONE: Answer directly. Never mention 'the documents', 'the context', or 'the provided information'.\n"
            "4. ACCURACY: Base your answer strictly on the most relevant context. If information is insufficient, state what's missing briefly.\n"
            "5. STRUCTURE: Use clear paragraphs. Avoid lists unless the content is inherently a short enumeration (e.g., line items).\n"
            "Provide focused, professional responses in plain text."
        )

    # Use LCEL with ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

    # Convert history to BaseMessage objects if they aren't already
    chat_history = []
    for h in history[-6:]:
        role = h.get("role", "")
        content = h.get("content", "")
        if role == "user":
            chat_history.append(HumanMessage(content=content))
        elif role == "assistant":
            chat_history.append(AIMessage(content=content))

    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", 
         "Context (each passage is from a document; use only passages relevant to the question):\n\n{context}\n\n"
         "---\n\n"
         "User Question: {query}\n\n"
         "---\n\n"
         "Instructions:\n"
         "- Answer using ONLY context that directly relates to the question. Ignore unrelated passages.\n"
         "- Write in plain text (no markdown: no #, *, **, or bullet formatting).\n"
         "- Be thorough but focused. Do not add notes about irrelevant documents.\n\n"
         "Your answer:")
    ])

    try:
        llm = get_llm(temperature=0.4, max_tokens=2048)
        chain = prompt_template | llm | StrOutputParser()
        
        answer = chain.invoke({
            "chat_history": chat_history,
            "context": context,
            "query": query
        })
            
        return {**state, "generated_answer": answer}
    except Exception as e:
        return {
            **state,
            "generated_answer": f"Error generating answer: {e}",
            "error": str(e),
        }

