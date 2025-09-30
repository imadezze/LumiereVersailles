import os
import json
from datetime import datetime
from openai import OpenAI
import gradio as gr
from dotenv import load_dotenv
load_dotenv()

from tools import (
    bulletin_meteo, 
    get_activities_by_date_tool, 
    final_answer_tool, 
    rag_tool,
    build_tools_from_functions
    )

MODEL = "gpt-4o-mini"

# Map function names to actual Python callables
FUNCTIONS = [bulletin_meteo, get_activities_by_date_tool, rag_tool, final_answer_tool]
TOOLS = build_tools_from_functions(FUNCTIONS)

FUNCTION_MAP = {fn.__name__: fn for fn in FUNCTIONS}

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

class ItineraryAgent:
    """
    Agent responsible for producing the itinerary.
    Executes tool calls until the model returns a final assistant message
    (i.e., no more tool_calls). This allows the model to call
    final_answer_tool at the end of the cycle.
    """

    def __init__(self, model, api_key: str = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.name = "itinerary_agent"
        self.model = model

    def _safe_json_loads(self, s: str) -> dict:
        """Parse JSON args defensively; fall back to empty dict on failure."""
        try:
            return json.loads(s) if s else {}
        except Exception:
            return {}

    def get_response(self, ui_history: list[dict]) -> str:
        
        # Build the message list: SYSTEM + UI history
        api_messages: list[dict] = [{"role": "system", "content": PROMPT}]
        api_messages += [m.copy() for m in ui_history]

        # Loop to allow multiple rounds of tool calls
        MAX_TOOL_STEPS = 12  # safety cap to avoid infinite loops

        # Agentic loop - exit using final_response tool
        for _ in range(MAX_TOOL_STEPS):
            
            # Get the model's response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.5,
            )
            msg = response.choices[0].message

            # If the model wants to call tools, execute them and continue
            if getattr(msg, "tool_calls", None):
                # Append the assistant message that requested the tools
                api_messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
                })

                # Execute each requested tool
                for tool_call in msg.tool_calls:
                    func_name = tool_call.function.name
                    args = self._safe_json_loads(tool_call.function.arguments or "{}")

                    # Run the matching Python function
                    result_payload: dict | str
                    if func_name in FUNCTION_MAP:
                        try:
                            result = FUNCTION_MAP[func_name](**args)
                            result_payload = result
                        except Exception as e:
                            # Return the error to the model so it can decide what to do
                            result_payload = {"error": str(e)}
                    else:
                        result_payload = {"error": f"Unknown tool: {func_name}"}

                    # Append the tool result as a tool message
                    api_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result_payload, ensure_ascii=False),
                    })

                # Continue loop: the next iteration will send all accumulated messages
                # so the model can react to tool outputs (e.g., call final_answer_tool).
                continue

            # No tool calls -> this is the final assistant content
            return msg.content or ""

        # If we exit due to hitting MAX_TOOL_STEPS, return a graceful notice
        return (
            "I ran into an unusually long chain of tool calls. "
            "Please try again or narrow the request."
        )

    





    






def chatbot_llm(user_input, chat_history):
    """
    Chatbot LLM interface to gradio.
    Args:    
            user_input (str): The user's input message.
            history (List[Dict]): The conversation history.
    Returns:
            tuple ("", updated_history (List[Dict]): The updated conversation history.)
    """
    agent = ItineraryAgent(MODEL)

    
    chat_history.append(
        {"role": "user", "content": user_input}
        )
    
    bot_message = agent.get_response(chat_history)

    chat_history.append({"role": "assistant", "content": bot_message.strip()})
    return "", chat_history







# ----------------------------
# Gradio UI
# ----------------------------

# Initial greeting message from assistant
initial_greeting = [{
    "role": "assistant", 
    "content": ("Hi! I'm your itinerary assistant. "
    "Let's plan your trip to Versailles. "
    "Tell me about what you are interested in for your visit to Versailles?")
    }
]

with gr.Blocks() as demo:
    # configure chatbot UI to OpenAI format
    chatbot_ui = gr.Chatbot(value=initial_greeting,
                            type="messages",
                            label="Versailles itinerary assistant",
                            height="85vh",
                            elem_id="chatbot",
                            autoscroll=True)
    msg = gr.Textbox(placeholder="Type your message here...")

    msg.submit(fn=chatbot_llm, inputs=[msg, chatbot_ui], outputs=[msg, chatbot_ui])

demo.launch(debug=True)