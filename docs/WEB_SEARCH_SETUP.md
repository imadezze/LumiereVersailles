# Web Search Setup Guide (LinkUp Integration)

This guide explains how to set up and use web search functionality in the Versailles chatbot using LinkUp Search.

## What is LinkUp Search?

LinkUp is an AI-powered search API specifically designed for LLMs. It provides:
- Deep search capabilities with comprehensive coverage
- AI-synthesized answers (not just raw search results)
- Source citations for verification
- LangChain integration
- Access to premium partner sources

**Website:** https://linkup.so/
**Dashboard:** https://app.linkup.so/
**Sign Up:** https://app.linkup.so/sign-up

## Installation

### 1. Install Required Package

```bash
pip install langchain-linkup
```

### 2. Get Your API Key

1. Go to https://app.linkup.so/sign-up
2. Sign up for a LinkUp account
3. Navigate to API Keys section in dashboard
4. Copy your API key

### 3. Configure Environment

Add your LinkUp API key to your `.env` file:

```bash
# LinkUp Search API Configuration (for web search)
LINKUP_API_KEY=your_linkup_api_key_here
```

## How It Works

### Tool: `search_web_for_versailles_info`

The agent now has access to a web search tool that provides AI-synthesized answers about current Versailles information from the internet.

**Function signature:**
```python
search_web_for_versailles_info(
    query: str  # Natural language search query
) -> str
```

**Key Features:**
- Returns an AI-synthesized answer (not raw search results)
- Includes source citations for verification
- Uses "deep" search mode for comprehensive coverage
- Automatically formats information for the LLM

### When the Agent Uses Web Search

The agent will automatically use web search when users ask about:

1. **Current Events**
   - "What events are happening at Versailles this weekend?"
   - "Are there any special exhibitions right now?"

2. **Time-Sensitive Information**
   - "Is Versailles open today?"
   - "What's the latest news about Versailles?"

3. **Recent Updates**
   - "What exhibitions are currently at Versailles?"
   - "Are there any closures this week?"

### When the Agent Won't Use Web Search

For standard information, the agent uses the knowledge base instead:
- General history
- Regular opening hours
- Standard ticket prices
- Well-established facts

## Testing Web Search

### Quick Test

Start the backend and ask:

```bash
"What special events are happening at Versailles this month?"
```

The agent should use the `search_web_for_versailles_info` tool.

### Example Interaction

**User:** "Y a-t-il des événements spéciaux ce weekend à Versailles?"

**Agent Process:**
1. Detects this is a current/time-sensitive question
2. Calls `search_web_for_versailles_info("événements spéciaux Versailles ce week-end")`
3. Receives AI-synthesized answer with source citations
4. Presents information naturally in French

**Response:**
"D'après les informations récentes en ligne, voici les événements prévus ce week-end à Versailles : [AI-synthesized answer from LinkUp]..."

## Verification

Check if web search is working:

1. **Start the backend:**
   ```bash
   cd backend
   python main.py
   ```

2. **Look for initialization message:**
   ```
   🔧 Initializing web search...
   ✅ Web search ready with 1 tools
   ```

3. **If you see:**
   ```
   ⚠️ Web search not available: langchain-linkup not installed
   ```
   → Run `pip install langchain-linkup`

4. **If you see:**
   ```
   ⚠️ Web search not available: LINKUP_API_KEY not set
   ```
   → Add `LINKUP_API_KEY` to your `.env` file

## Tool Priority

The agent follows this priority order:

1. **FIRST**: Knowledge base (for standard information)
2. **SECOND**: Web search (for current/time-sensitive queries)
3. **THIRD**: Weather tool (for météo forecasts)
4. **FOURTH**: Travel tool (for transportation)

## Cost Considerations

LinkUp has usage limits based on your plan:
- **Free tier**: Limited searches per month
- **Paid plans**: Higher limits and features

Check your usage at: https://app.linkup.so/

## Troubleshooting

### Web search not initializing

**Problem:** Agent shows "⚠️ Web search not available"

**Solutions:**
1. Install package: `pip install langchain-linkup`
2. Set API key in `.env`: `LINKUP_API_KEY=your_key`
3. Restart the backend

### Web search returns no answer

**Possible causes:**
- Query is too specific or unclear
- No recent information available on the topic
- API rate limit reached

**Solution:** Check LinkUp dashboard for API usage and errors

### Agent not using web search

**Check:**
- Is the question time-sensitive? (Standard info uses knowledge base)
- Is web search initialized? (Check backend logs)
- Try more explicit queries like "latest news about Versailles"

## Example Queries

**Good queries for web search:**
- "What exhibitions are currently at Versailles?"
- "Special events this weekend at Versailles"
- "Latest news about Palace of Versailles"
- "Is Versailles open today?"

**Queries that use knowledge base instead:**
- "What is the history of Versailles?"
- "What are the opening hours?" (standard)
- "How much does a ticket cost?" (standard)
- "Who was Louis XIV?"

## Advanced Configuration

### Search Depth

In `agents/tools/web_search_tools.py`, you can modify:

```python
depth="deep",                    # "standard" or "deep"
output_type="sourcedAnswer"     # "searchResults", "sourcedAnswer", or "structured"
```

### Search Modes

- `depth="deep"`: More comprehensive search (recommended, currently used)
- `depth="standard"`: Faster but less comprehensive
- `output_type="sourcedAnswer"`: AI-synthesized answer with sources (recommended, currently used)
- `output_type="searchResults"`: Raw search results
- `output_type="structured"`: Structured data format

## Integration with Frontend

The frontend automatically displays when web search is used through the tool usage indicator (similar to RAG and weather tools).

---

## Summary

✅ **Installed:** `langchain-linkup`
✅ **Configured:** `LINKUP_API_KEY` in `.env`
✅ **Integrated:** Tool automatically used for current information
✅ **Priority:** Knowledge base first, web search for current queries
✅ **AI-Powered:** Returns synthesized answers, not raw search results

**Key Advantages of LinkUp:**
- Pre-synthesized AI answers (less processing needed)
- Multiple sources aggregated automatically
- Source citations included
- Deep search mode for comprehensive coverage

For more information: https://python.langchain.com/docs/integrations/providers/linkup/