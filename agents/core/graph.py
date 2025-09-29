"""
LangGraph workflow definition for Versailles Weather Agent
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from .state import AgentState
from .agent import VersaillesWeatherAgent


def create_weather_agent_graph() -> StateGraph:
    """
    Create the LangGraph workflow for the Versailles Weather Agent
    """

    # Initialize the agent
    agent = VersaillesWeatherAgent()

    def parse_input_node(state: AgentState) -> AgentState:
        """
        Parse user input and extract relevant information
        """
        if not state.get("messages"):
            return state

        # Get the latest user message
        user_message = state["messages"][-1]
        if hasattr(user_message, 'content'):
            user_query = user_message.content
        else:
            user_query = str(user_message)

        # Analyze the input
        analysis = agent.process_user_input(user_query)

        # Update state
        state["user_query"] = user_query
        state["visit_date"] = analysis["visit_date"]
        state["iteration_count"] = state.get("iteration_count", 0) + 1

        return state

    def weather_tool_node(state: AgentState) -> AgentState:
        """
        Call weather tool if needed
        """
        if state.get("visit_date"):
            weather_data = agent.call_weather_tool(state["visit_date"])
            state["weather_data"] = weather_data

            # Handle errors
            if weather_data.get("status") == "error":
                state["error"] = weather_data.get("error")

        return state

    def response_node(state: AgentState) -> AgentState:
        """
        Generate final response
        """
        try:
            user_query = state.get("user_query", "")
            weather_data = state.get("weather_data")

            response = agent.generate_response(user_query, weather_data)
            state["response"] = response

            # Add AI message to conversation history
            if "messages" not in state:
                state["messages"] = []

            state["messages"].append(AIMessage(content=response))

        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            state["response"] = error_msg
            state["error"] = str(e)
            state["messages"].append(AIMessage(content=error_msg))

        return state

    def should_call_weather_tool(state: AgentState) -> str:
        """
        Determine if weather tool should be called
        """
        # Check if we need weather data and have a date
        if state.get("visit_date") and not state.get("weather_data"):
            user_query = state.get("user_query", "").lower()
            weather_keywords = ['weather', 'forecast', 'temperature', 'visit', 'plan']

            if any(keyword in user_query for keyword in weather_keywords):
                return "weather_tool"

        return "response"

    def should_end(state: AgentState) -> str:
        """
        Determine if the workflow should end
        """
        # End if we have a response or hit max iterations
        max_iterations = 5
        current_iterations = state.get("iteration_count", 0)

        if state.get("response") or current_iterations >= max_iterations:
            return END
        else:
            return "parse_input"

    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("parse_input", parse_input_node)
    workflow.add_node("weather_tool", weather_tool_node)
    workflow.add_node("response", response_node)

    # Define edges
    workflow.set_entry_point("parse_input")

    # Conditional routing from parse_input
    workflow.add_conditional_edges(
        "parse_input",
        should_call_weather_tool,
        {
            "weather_tool": "weather_tool",
            "response": "response"
        }
    )

    # From weather_tool to response
    workflow.add_edge("weather_tool", "response")

    # From response to end
    workflow.add_conditional_edges(
        "response",
        should_end,
        {
            END: END,
            "parse_input": "parse_input"
        }
    )

    return workflow


def create_compiled_agent():
    """
    Create and compile the complete agent graph
    """
    graph = create_weather_agent_graph()
    return graph.compile()