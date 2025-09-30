# Backend Tests

Tests for the Versailles Chatbot backend, specifically the `/chat` evaluation endpoint.

## Endpoint Specification

**Endpoint:** `POST /chat`

**Request Format:**
```json
{
  "question": "requête du visiteur"
}
```

**Response Format:**
```json
{
  "answer": "réponse complète du chatbot"
}
```

## Running the Tests

### Prerequisites

**IMPORTANT: Backend must be running on http://localhost:8000 before running tests**

1. **Terminal 1** - Start the backend:
```bash
cd backend
python main.py
```

Wait for the message: "✅ Simplified Versailles agent initialized"

2. **Terminal 2** - Install test dependencies (if not already installed):
```bash
pip install pytest requests
```

### Option 1: Run with pytest (Real HTTP calls)

Run all tests with pytest:
```bash
cd backend/tests
pytest test_chat_endpoint.py -v
```

Run a specific test:
```bash
pytest test_chat_endpoint.py::TestChatEndpoint::test_chat_endpoint_format -v
```

**Note:** These tests make **real HTTP requests** to http://localhost:8000. If the backend is not running, tests will fail with a connection error.

### Option 2: Run Manual Test Script

Run the manual test script to see detailed output:
```bash
cd backend/tests
python test_chat_manual.py
```

This will:
- Check if the backend is running
- Test the endpoint with various questions
- Show detailed request/response for each test
- Verify response format

### Option 3: Test with curl

Quick test from command line:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Quels sont les horaires d'\''ouverture?"}'
```

## Test Coverage

The test suite covers:

1. **Endpoint Availability**
   - Endpoint exists and accepts POST requests
   - Returns 200 status code

2. **Request Format**
   - Accepts `{"question": "..."}` format
   - Returns 422 for missing fields
   - Returns 422 for wrong field names

3. **Response Format**
   - Returns `{"answer": "..."}` format
   - Answer is a non-empty string

4. **Functionality**
   - Visit planning questions (should use RAG tool)
   - Ticket price questions
   - Opening hours questions
   - Weather questions (should use weather tool)
   - Transportation questions

5. **Language Support**
   - Responds in French for French questions
   - Responds in English for English questions

6. **Error Handling**
   - Handles empty questions gracefully
   - Handles malformed requests
   - Returns graceful error messages

## Expected Behavior

### Visit Planning Questions
**Question:** "Je veux visiter le 29 août, que me conseilles-tu?"

**Expected:** Should use the RAG knowledge base tool (NOT weather tool) to provide visit advice from the Versailles documentation.

### Weather Questions
**Question:** "Quel temps fera-t-il demain?"

**Expected:** Should use the weather tool to provide weather forecast.

### General Information
**Question:** "Quels sont les horaires d'ouverture?"

**Expected:** Should use RAG knowledge base to provide opening hours from documentation.

## Debugging Failed Tests

If tests fail:

1. **Connection Error / pytest.exit message:**
   ```
   ❌ Cannot connect to backend at http://localhost:8000
   ```
   - Make sure backend is running in another terminal: `cd backend && python main.py`
   - Check port 8000 is not in use: `lsof -i :8000`
   - Verify backend started successfully (look for "✅ Simplified Versailles agent initialized")

2. **Timeout Errors:**
   - Backend may be slow to respond (LLM API calls can take time)
   - Check backend logs for any errors
   - Tests are configured with 120s timeout to accommodate slow responses

3. **422 Status Code:**
   - Check request format matches `{"question": "..."}`
   - Verify Content-Type header is `application/json`

4. **500 Status Code:**
   - Check backend logs for errors
   - Verify agent initialization succeeded
   - Check API keys in `.env` file (OPENAI_API_KEY, MISTRAL_API_KEY, etc.)

5. **Empty or Wrong Response:**
   - Check backend logs for tool usage
   - Verify RAG system is initialized (if testing RAG features)
   - Check system prompt configuration

6. **Tests pass but responses seem wrong:**
   - The tests now use **real HTTP calls** to the live backend
   - Check backend terminal for detailed logs
   - Try the manual test script for more visibility: `python test_chat_manual.py`

## Example Test Run

### Terminal 1: Start Backend
```bash
$ cd backend
$ python main.py

⚠️ RAG system not available: No module named 'chromadb'
🤖 Using OPENAI LLM: gpt-4o-mini
🔧 Initializing RAG knowledge base...
❌ Cannot initialize RAG: RAG system not available
⚠️ RAG knowledge base not available - continuing without it
✅ Simplified Versailles agent initialized
🛠️ Available tools: ['get_versailles_weather_tool', 'get_travel_to_versailles_tool']
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Terminal 2: Run Tests
```bash
$ cd backend/tests
$ pytest test_chat_endpoint.py -v

================================================================================
Test session starts
================================================================================
platform darwin -- Python 3.10.14, pytest-7.4.3
collected 13 items

✅ Backend is running at http://localhost:8000

test_chat_endpoint.py::TestChatEndpoint::test_chat_endpoint_exists PASSED     [ 7%]
test_chat_endpoint.py::TestChatEndpoint::test_chat_endpoint_format PASSED     [15%]
test_chat_endpoint.py::TestChatEndpoint::test_chat_endpoint_response_format PASSED [23%]
test_chat_endpoint.py::TestChatEndpoint::test_chat_endpoint_with_visit_question PASSED [30%]
test_chat_endpoint.py::TestChatEndpoint::test_chat_endpoint_with_ticket_question PASSED [38%]
test_chat_endpoint.py::TestChatEndpoint::test_chat_endpoint_with_hours_question PASSED [46%]
test_chat_endpoint.py::TestChatEndpoint::test_chat_endpoint_with_empty_question PASSED [53%]
test_chat_endpoint.py::TestChatEndpoint::test_chat_endpoint_missing_question_field PASSED [61%]
test_chat_endpoint.py::TestChatEndpoint::test_chat_endpoint_wrong_field_name PASSED [69%]
test_chat_endpoint.py::TestChatEndpoint::test_chat_endpoint_multiple_questions PASSED [76%]
test_chat_endpoint.py::TestChatEndpoint::test_chat_endpoint_french_response PASSED [84%]
test_chat_endpoint.py::TestChatEndpoint::test_chat_endpoint_english_response PASSED [92%]
test_chat_endpoint.py::TestChatEndpoint::test_health_endpoint PASSED         [100%]

================================================================================
13 passed in 45.23s
================================================================================
```