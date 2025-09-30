import os
import json
from datetime import datetime
from openai import OpenAI
import gradio as gr
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.graph.message import add_messages
from langgraph.errors import GraphRecursionError

from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_core.messages import ToolMessage

# Your datamodels
from datamodels import TravelPlan, Activity, WeatherForecast, VisitInformationSchedule, Interest, ItineraryAgentResponse,ModificationRequests

load_dotenv()

from tools import (
    bulletin_meteo, 
    get_activities_by_date_tool, 
    rag_tool
    )


PROMPT =f"""
You are a travel itinerary planner for Versailles, France. 
today is {datetime.now().strftime("%d-%m-%Y")}.
Activities start from 01-10-2025 and end on 14-10-2025.

STEPS:
1. first call the bulletin_meteo tool to get the weather forecast for the next 14 days.
2. then call the get_activities_by_date_tool to get the activities available for the selected date. If no date is provided use 01-10-2025.
   2.1 You can call the RAG tool with a query to collect usefull information about Chateau de Versailles (opening hours, useful tips, etc.)
3. use the weather forecast to plan the itinerary based on activities setting (indoor, outdoor, mixed) and additional information collected.
4. repeat steps 2 and 3 for each day of the itinerary.
5. call the final_answer_tool to submit your itinerary proposal.

GUIDELINES:
- your intitial message should be in french with its english counter part.
- then always respond in the language of the user.
"""

tools = [get_activities_by_date_tool, rag_tool, bulletin_meteo]


    
# -------------------------------------------------------
# 1. Shared State
# -------------------------------------------------------
class AgentState(TypedDict):
    
    itinerary_proposal: Optional[TravelPlan]
    itinerary_presentation: Optional[str]
    itinerary_to_present: Optional[TravelPlan]
    validation_stage: Optional[str]  # present | collect | revise | None
    is_itinerary_validated: bool
    approved_itinerary: Optional[TravelPlan]
    available_activities: List[Activity]
    weather_forecast: Optional[WeatherForecast]
    # tell langgraph to add messages to the state not replace it in State["messages"]
    messages: Annotated[List[BaseMessage], add_messages]  # conversation history


# -------------------------------------------------------
# 2. Initialize model + memory
# -------------------------------------------------------
model = init_chat_model("openai:gpt-4o-mini")
#model = init_chat_model("mistral-large-2411", api_key=os.getenv("MISTRAL_API_KEY"))  #mistral-medium-2508
checkpointer = InMemorySaver()


# -------------------------------------------------------
# 3. Agents as Nodes
# -------------------------------------------------------

def visit_information_agent(state: AgentState) -> AgentState:
    """
    Collect structured visit info until VisitInformationSchedule is complete.
    """

    # CRITICAL: if visit information is complete, early exit to leave state flags unchanged
    if state.get("is_visit_information_complete", False):
        return {"messages": []}


    # initialize defaults - Ensure defaults exist
    # fills in a key if missing
    state.setdefault("visit_information", None)
    state.setdefault("is_visit_information_complete", False)
    state.setdefault("itinerary_proposal", None)
    state.setdefault("itinerary_presentation", None)
    state.setdefault("itinerary_to_present", None)
    state.setdefault("validation_stage", None)
    state.setdefault("change_request", [])
    state.setdefault("is_itinerary_validated", False)
    state.setdefault("approved_itinerary", None)
    state.setdefault("last_processed_human_index", -1)
    state.setdefault("available_activities", [])
    state.setdefault("weather_forecast", None)
    state.setdefault("revision_number", 0)
    state.setdefault("max_revisions", 2)
    state.setdefault("messages", [])

    updates = {"messages": []}

    history = state.get("messages", [])
    # Last user message (assume it's a change request or confirmation)
    user_input = None
    if state.get("messages"):
        user_input = state["messages"][-1].content

    # build system prompt
    sys_prompt = ITINERARY_AGENT_SYSTEM_PROMPT.format(
                tools=get_tool_descriptions_string(tools),  # error using itinerary_agent.tools
                weather_forecast=state["weather_forecast"] if state["weather_forecast"] else "unknown",  #.model_dump()
                visit_information_schedule=state["visit_information"].model_dump_json(indent=2) if state["visit_information"] else {},
                itinerary_schedule_output_format=TravelPlan.model_json_schema()
            )

    try:
            # Feed into the ReAct agent - multiturn - thread maintains memory
            result = itinerary_agent.invoke(
                {"messages": [
                    SystemMessage(content=sys_prompt),
                    HumanMessage(content="Prepare the itinerary")
                ]},
                config={"configurable": {"thread_id": THREAD_ID},"recursion_limit": 25}
                #config={"configurable": {"thread_id": "first_itinerary"}}   # New separate thread
            )

    except GraphRecursionError:
        console.print("Agent reached max recursion limit. Stopping.", style="bold red")
        console.print("WARNING: GRAPH will automatically retry a new construction cycle.", style="bold magenta")
        return updates.update({"validation_stage": "retry"})

    # Expect the agent's final message to be matching TravelPlan datamodel (structured_response)
    proposed_itinerary = result["structured_response"]
    
    print("***** Response itinerary agent: ******", proposed_itinerary.model_dump_json(indent=2))

    updates = {
        "messages": [],
        "itinerary_proposal": proposed_itinerary,
        "itinerary_to_present": proposed_itinerary,
        # set flag indicating next agent should first present itinerary
        "validation_stage": "present",
        }
        
    return updates


def itinerary_presentation_agent(state: AgentState) -> AgentState:
    
    itinerary = state["itinerary_to_present"]

    if state.get("is_itinerary_validated", False):
        # Already completed, skip
        requested_changes = None
        initial_itinerary = None

    elif state.get("change_request"):
        requested_changes = state.get("change_request", [])
        initial_itinerary = state["itinerary_proposal"].model_dump_json(indent=2)

    else:
        requested_changes = None
        initial_itinerary = state["itinerary_proposal"].model_dump_json(indent=2)

    system_prompt = ITINERARY_PRESENTATION_PROMPT.format(
        initial_itinerary=initial_itinerary,
        requested_changes=requested_changes,
        weather_forecast=state["weather_forecast"] if state["weather_forecast"] else "unknown",
        visit_information_schedule=state["visit_information"].model_dump_json(indent=2) if state["visit_information"] else {},
    )

    # get the itinerary presentation
    response = model.invoke([
        SystemMessage(content=system_prompt), 
        HumanMessage(content=f"Please present this itinerary: {itinerary.model_dump_json(indent=2)}")])


    #last_human_idx = max((i for i,m in enumerate(state.get("messages", [])) if isinstance(m, HumanMessage)), default=-1)
    
    updates = {
        "messages": [AIMessage(content=response.content)],
        "validation_stage": "ask_user",
        #"last_processed_human_index": last_human_idx
    }

    return updates
