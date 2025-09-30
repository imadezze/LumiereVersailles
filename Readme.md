# Les Clefs de Versailles

**Team Lumière** - An intelligent agentic solution for personalized visitor itineraries at the Palace of Versailles.

## 🎯 The Challenge

Visiting Versailles can be overwhelming:
- Complex palace structure with interconnected gardens and hundreds of rooms
- Information overload and difficulty planning for time constraints
- Weather conditions, crowd management, and diverse personal interests

**Our Solution**: An AI-powered system that plans custom itineraries through simple natural language conversation, eliminating complexity.

## 🏗️ Architecture Overview

### Frontend
**Modern Chat Interface** built with **React, TypeScript, Vite, and Axios**

- 💬 **Intuitive & Responsive Design**: Clean interface that works on any device
- ⚡ **Real-Time Feedback**: Live connection status and animated typing indicators
- 🔍 **Agent Transparency**: Visual badges showing which tools were used (RAG, Weather, Travel, Web Search)
- 🎙️ **Voice Support**: Natural speech input in French/English for hands-free interaction
- 💾 **Persistent Conversations**: Unique conversation IDs for resuming sessions
- 🎯 **Easy Onboarding**: Pre-defined query buttons to discover capabilities

### Backend
**Modular Agentic Architecture** with specialized tools for clean separation of concerns

#### 1. **Agent** - LLM with Tool Calling
- **Tech**: OpenAI GPT-4.1 / Mistral Medium 3.1 / LangChain
- **Two Modes**:
  - **One-Shot**: Plans complete visits without additional questions (API test mode)
  - **Conversational**: Asks 2-3 questions to infer user intent and preferences
- Grounded in Versailles knowledge base for factual accuracy

#### 2. **RAG Tool** - Knowledge Base Search
- **Tech**: Mistral Embeddings / ChromaDB / LangChain
- **5,799 searchable chunks** from 343 official documents
- Sub-second response times with source attribution
- Factual questions about locations, schedules, tickets, and services

#### 3. **Weather Tool** - Forecast Integration
- **Tech**: OpenWeather API
- Weather-dependent itinerary planning and recommendations
- Invoked when visit dates are mentioned

#### 4. **Travel Tool** - Transportation Planner
- **Tech**: Google Maps API
- Detailed directions with public transit, driving, walking, and parking options
- Multi-modal transport comparisons

#### 5. **Web Search Tool** - Current Information
- **Tech**: Linkup API
- Up-to-date information complementing the knowledge base
- Uses keywords from user messages

## 📊 Data Processing Pipeline

### JSONL Refinement (4,700+ entries)
1. **Recursive Text Extraction**: Traversed nested JSON structures
2. **Content Filtering**: Removed fragments under 7 words, preserved headings
3. **Text Cleaning**: Stripped URLs, normalized whitespace
4. **Smart List Handling**: Joined items with semicolons to preserve context
5. **Deduplication**: Eliminated duplicates while maintaining order
6. **Final Formatting**: Created `{"url": "text"}` structure optimized for embeddings

### PDF Processing with Docling
- **Layout Detection**: ML models identify structure, headers, paragraphs
- **Table Extraction**: Specialized model preserves data relationships
- **Structure Preservation**: Maintained folder hierarchy for navigation
- **Result**: All PDFs converted to clean Markdown for RAG chunking

### RAG Knowledge Indexing
1. **Raw Data Processing**: 343 documents from chateauversailles.fr
2. **Intelligent Chunking**: 2000-6000 character semantic chunks with 200-char overlap
3. **Vector Embedding**: Mistral AI converts chunks to numerical vectors
4. **Persistent Storage**: ChromaDB stores 5,799 chunks with metadata and URLs

### RAG Query Processing
1. User question → 2. Vector embedding → 3. Similarity search (top 5 from 5,799) → 4. Context assembly → 5. LLM generates answer with citations

**Performance**: Sub-second responses with comprehensive source attribution

## 🚀 Getting Started

### Installation
```bash
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file with:
```
OPENAI_API_KEY=your_key
MISTRAL_API_KEY=your_key
OPENWEATHER_API_KEY=your_key
GOOGLE_MAPS_API_KEY=your_key
GEMINI_API_KEY=your_key
```

### Running the Backend
```bash
python main.py
```

The backend server will start and listen for requests from the frontend.

### Running the Frontend
```bash
cd frontend
npm install
npm run dev
```

### Testing the Agent (CLI)
For command-line testing:
```bash
python agents/core/simple_agent.py
```

## 📁 Project Structure

```
LumiereVersailles/
├── agents/
│   ├── core/           # Agent implementation
│   ├── prompts/        # Modular prompt files
│   ├── tools/          # RAG, Weather, Travel, Web Search tools
│   └── config/         # Settings and configuration
├── data/
│   ├── rag_data/       # Processed Markdown files
│   └── other/          # Original PDFs and JSONL
├── frontend/           # React + TypeScript chat interface
├── chroma_db/          # Vector database storage
├── fill_db.py          # Build RAG embeddings index
└── ask.py              # Test RAG queries
```

## 🎯 Key Features

- **5,799 Knowledge Chunks**: Comprehensive official Versailles information
- **Sub-second Responses**: Real-time personalized planning
- **Source Attribution**: Verified, trustworthy answers with URLs
- **Bilingual Support**: French and English interface
- **Voice Input**: Hands-free interaction while exploring
- **Two Operating Modes**: API test (one-shot) and conversational

## 🏆 Team Lumière

**Versailles Hackathon 2025**

Transforming visitor experiences through intelligent, personalized itinerary planning.


