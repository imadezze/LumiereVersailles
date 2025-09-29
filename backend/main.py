"""
FastAPI backend for Versailles Chatbot
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import sys
from pathlib import Path

# Add parent directory to path to import agents
sys.path.append(str(Path(__file__).parent.parent))

from agents.core.simple_agent import SimplifiedVersaillesAgent

app = FastAPI(title="Versailles Chatbot API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the simplified agent
agent = SimplifiedVersaillesAgent()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    reponse: str  # Using French format as required by evaluation
    conversation_id: Optional[str] = None
    status: str = "success"

class EvaluationRequest(BaseModel):
    query: str

class EvaluationResponse(BaseModel):
    reponse: str  # Required format for evaluation

# Store conversations in memory (in production, use a database)
conversations: Dict[str, List[Dict[str, str]]] = {}

@app.get("/")
async def root():
    return {"message": "Versailles Chatbot API", "version": "1.0.0"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for interactive conversations
    """
    try:
        # Process the message through the agent
        result = agent.process_query(request.message)

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

        # Store conversation history
        conv_id = request.conversation_id or "default"
        if conv_id not in conversations:
            conversations[conv_id] = []

        conversations[conv_id].extend([
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": result["response"]}
        ])

        return ChatResponse(
            reponse=result["response"],
            conversation_id=conv_id,
            status="success"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.post("/api/evaluate", response_model=EvaluationResponse)
async def evaluate(request: EvaluationRequest):
    """
    Evaluation endpoint for hackathon - expects queries and returns responses
    This endpoint is designed to work with Ngrok for evaluation
    """
    try:
        # Process the query through the agent
        result = agent.process_query(request.query)

        if result["status"] == "error":
            # Return a fallback response instead of error for evaluation
            response_text = "Je m'excuse, mais je rencontre des difficultés techniques. Pourriez-vous reformuler votre question?"
        else:
            response_text = result["response"]

        return EvaluationResponse(reponse=response_text)

    except Exception as e:
        # Return a graceful error response for evaluation
        return EvaluationResponse(
            reponse="Je m'excuse, mais je ne peux pas traiter votre demande en ce moment. Veuillez réessayer plus tard."
        )

@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get conversation history
    """
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"conversation_id": conversation_id, "messages": conversations[conversation_id]}

@app.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Clear conversation history
    """
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": "Conversation deleted"}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "weather_available": hasattr(agent, 'tools') and len(agent.tools) > 0
    }

# Serve static files (for frontend)
if Path("frontend/dist").exists():
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)