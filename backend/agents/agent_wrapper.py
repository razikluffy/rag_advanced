"""Wrapper for integrating LangChain agents with LangGraph."""

from typing import Any, Dict, Callable, Optional
from langchain_core.runnables import Runnable

from .langchain_agents import (
    create_query_analysis_agent,
    create_relevance_check_agent,
    create_tool_using_chain,
    create_rag_agent
)


class LangChainAgentWrapper:
    """Wrapper to make LangChain agents compatible with LangGraph nodes."""
    
    def __init__(self, agent_factory: Callable, **agent_kwargs):
        """
        Initialize the wrapper with an agent factory function.
        
        Args:
            agent_factory: Function that creates the LangChain agent
            **agent_kwargs: Additional arguments to pass to the agent factory
        """
        self.agent_factory = agent_factory
        self.agent_kwargs = agent_kwargs
        self._agent = None
    
    @property
    def agent(self):
        """Lazy initialization of the agent."""
        if self._agent is None:
            self._agent = self.agent_factory(**self.agent_kwargs)
        return self._agent
    
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent and return updated state."""
        return self.agent.invoke(state)


def create_query_analysis_wrapper(**kwargs) -> LangChainAgentWrapper:
    """Create a wrapper for the query analysis agent."""
    return LangChainAgentWrapper(create_query_analysis_agent, **kwargs)


def create_relevance_check_wrapper(**kwargs) -> LangChainAgentWrapper:
    """Create a wrapper for the relevance check agent."""
    return LangChainAgentWrapper(create_relevance_check_agent, **kwargs)


def create_tool_using_wrapper(tools, system_prompt: str, **kwargs) -> LangChainAgentWrapper:
    """Create a wrapper for a tool-using chain."""
    def factory(**factory_kwargs):
        return create_tool_using_chain(tools, system_prompt, **factory_kwargs)
    
    return LangChainAgentWrapper(factory, **kwargs)


def create_rag_wrapper(retriever: Runnable, **kwargs) -> LangChainAgentWrapper:
    """Create a wrapper for a RAG agent."""
    def factory(**factory_kwargs):
        return create_rag_agent(retriever, **factory_kwargs)
    
    return LangChainAgentWrapper(factory, **kwargs)


# Node functions for LangGraph integration
def query_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node for query analysis using LangChain agent."""
    wrapper = create_query_analysis_wrapper()
    return wrapper.invoke(state)


def relevance_check_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node for relevance checking using LangChain agent."""
    wrapper = create_relevance_check_wrapper()
    return wrapper.invoke(state)


def tool_using_node(state: Dict[str, Any], tools, system_prompt: str) -> Dict[str, Any]:
    """LangGraph node for tool-using agent."""
    query = state.get("query", "")
    chat_history = state.get("chat_history", [])
    
    wrapper = create_tool_using_wrapper(tools, system_prompt)
    response = wrapper.agent.invoke(query, chat_history)
    
    return {
        **state,
        "generated_answer": response,
        "final_response": response
    }


def rag_node(state: Dict[str, Any], retriever: Runnable) -> Dict[str, Any]:
    """LangGraph node for RAG agent."""
    query = state.get("query", "")
    chat_history = state.get("chat_history", [])
    
    wrapper = create_rag_wrapper(retriever)
    response = wrapper.agent.invoke(query, chat_history)
    
    return {
        **state,
        "generated_answer": response,
        "final_response": response
    }


# Utility function to convert LangChain agents to LangGraph-compatible nodes
def agent_to_node(agent: Runnable, state_key: str = "query") -> Callable:
    """
    Convert any LangChain agent to a LangGraph-compatible node.
    
    Args:
        agent: The LangChain agent/chain to convert
        state_key: The key in the state to use as input to the agent
        
    Returns:
        A function compatible with LangGraph nodes
    """
    def node(state: Dict[str, Any]) -> Dict[str, Any]:
        input_value = state.get(state_key, "")
        
        if isinstance(input_value, str):
            # Simple string input
            response = agent.invoke(input_value)
        else:
            # Pass the whole state or specific keys
            response = agent.invoke(state)
        
        # Handle different response types
        if isinstance(response, dict):
            return {**state, **response}
        else:
            return {**state, "response": response}
    
    return node


# Factory for creating custom agent nodes
def create_agent_node(agent_factory: Callable, state_key: str = "query", **factory_kwargs) -> Callable:
    """
    Create a custom agent node for LangGraph.
    
    Args:
        agent_factory: Function that creates the agent
        state_key: The key in the state to use as input
        **factory_kwargs: Additional arguments for the agent factory
        
    Returns:
        A function compatible with LangGraph nodes
    """
    def node(state: Dict[str, Any]) -> Dict[str, Any]:
        agent = agent_factory(**factory_kwargs)
        input_value = state.get(state_key, "")
        
        if isinstance(input_value, str):
            response = agent.invoke(input_value)
        else:
            response = agent.invoke(state)
        
        if isinstance(response, dict):
            return {**state, **response}
        else:
            return {**state, "response": response}
    
    return node
