"""Query Analysis Agent - Extracts intent, entities, query type."""

from typing import Any, Dict, List

# Import the proper LangChain agent
from .langchain_agents import create_query_analysis_agent


def query_analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query Analysis Agent: Uses LangChain agent to analyze query intent, entities, and type.
    """
    # Create the agent instance
    agent = create_query_analysis_agent()
    
    # Execute the agent
    return agent.invoke(state)
