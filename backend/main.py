"""
FastAPI backend for Versailles Chatbot
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import sys
from pathlib import Path
from io import BytesIO
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Initialize ElevenLabs client for Speech-to-Text
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key) if elevenlabs_api_key else None

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

class InteractiveChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ToolUsage(BaseModel):
    name: str
    args: Dict[str, Any]
    execution_time_ms: Optional[int] = None

class InteractiveChatResponse(BaseModel):
    reponse: str  # Using French format
    conversation_id: Optional[str] = None
    status: str = "success"
    tools_used: Optional[List[ToolUsage]] = None

class TranscriptionResponse(BaseModel):
    transcript: str
    status: str = "success"

# Store conversations in memory (in production, use a database)
conversations: Dict[str, List[Dict[str, str]]] = {}

@app.get("/")
async def root():
    return {"message": "Versailles Chatbot API", "version": "1.0.0"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for evaluation
    Accepts: {"question": "requête du visiteur"}
    Returns: {"answer": "réponse complète du chatbot"}
    """
    try:
        # Process the question through the agent
        result = agent.process_query(request.question)

        if result["status"] == "error":
            # Return a graceful error message instead of raising exception
            return ChatResponse(
                answer="Je m'excuse, mais je rencontre des difficultés techniques. Pourriez-vous reformuler votre question?"
            )

        return ChatResponse(answer=result["response"])

    except Exception:
        # Return a graceful error response for evaluation
        return ChatResponse(
            answer="Je m'excuse, mais je ne peux pas traiter votre demande en ce moment. Veuillez réessayer plus tard."
        )

@app.post("/api/chat", response_model=InteractiveChatResponse)
async def interactive_chat(request: InteractiveChatRequest):
    """
    Interactive chat endpoint for frontend with conversation history and tool tracking
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

        # Extract tool usage information
        tools_used = None
        if result.get("tools_used"):
            tools_used = [
                ToolUsage(
                    name=tool_call.get("name", "unknown_tool"),
                    args=tool_call.get("args", {})
                )
                for tool_call in result["tools_used"]
            ]

        return InteractiveChatResponse(
            reponse=result["response"],
            conversation_id=conv_id,
            status="success",
            tools_used=tools_used
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


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
    Clear conversation history (both backend storage and agent memory)
    """
    # Clear backend conversation storage
    if conversation_id in conversations:
        del conversations[conversation_id]

    # Clear agent's internal conversation history
    try:
        agent.clear_conversation_history()
        return {
            "message": "Conversation deleted and agent history cleared",
            "conversation_id": conversation_id,
            "status": "success"
        }
    except Exception as e:
        return {
            "message": "Backend conversation deleted, but failed to clear agent history",
            "conversation_id": conversation_id,
            "error": str(e),
            "status": "partial_success"
        }

@app.post("/api/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe audio file using ElevenLabs Speech-to-Text
    Accepts: audio file (webm, mp3, wav, m4a, etc.)
    Returns: {"transcript": "text", "status": "success"}
    """
    if not elevenlabs_client:
        raise HTTPException(
            status_code=503,
            detail="ElevenLabs API not configured. Please set ELEVENLABS_API_KEY in environment variables."
        )

    try:
        # Read audio file content
        audio_content = await audio.read()

        print(f"📝 Transcribing audio: {len(audio_content)} bytes, type: {audio.content_type}")

        # Wrap audio content in BytesIO for ElevenLabs API
        audio_file = BytesIO(audio_content)
        audio_file.name = audio.filename or "recording.webm"

        # Call ElevenLabs Speech-to-Text API
        # Using the correct parameter name: file (not audio)
        transcript_response = elevenlabs_client.speech_to_text.convert(
            file=audio_file,
            model_id="scribe_v1"  # Current speech-to-text model
        )

        # Extract transcript text from response object
        # Response has attributes: text, language_code, language_probability, words
        transcript_text = transcript_response.text if hasattr(transcript_response, 'text') else str(transcript_response.get("text", ""))

        print(f"✅ Transcription result: '{transcript_text}' (language: {getattr(transcript_response, 'language_code', 'unknown')})")

        if not transcript_text or not transcript_text.strip():
            raise HTTPException(status_code=400, detail="No speech detected in audio")

        return TranscriptionResponse(
            transcript=transcript_text,
            status="success"
        )

    except Exception as e:
        print(f"❌ Transcription error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error transcribing audio: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "weather_available": hasattr(agent, 'tools') and len(agent.tools) > 0,
        "elevenlabs_available": elevenlabs_client is not None
    }

# Serve static files (for frontend)
if Path("frontend/dist").exists():
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)