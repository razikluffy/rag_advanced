"""Relevance Checker Agent - Evaluates if retrieved documents are relevant to the query."""

from typing import Any, Dict, List
import json

# Import the proper LangChain agent
from .langchain_agents import create_relevance_check_agent


def relevance_checker_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Relevance Checker Agent: Uses LangChain agent to evaluate if retrieved documents are relevant to the query.
    Returns relevance score (0-10) and determines if web search is needed.
    """
    # Create the agent instance
    agent = create_relevance_check_agent()
    
    # Execute the agent
    return agent.invoke(state)
