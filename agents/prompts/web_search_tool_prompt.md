# Web Search Tool

## search_web_for_versailles_info

**Real-time web search to complement RAG knowledge** (powered by LinkUp Search)

### When to Use
**Use ALMOST ALWAYS to complement RAG results:**
- Add current context and recent updates
- Enrich RAG information with additional details
- Provide up-to-date information
- Current events, exhibitions, news

### Important Rules
- **Always use WITH RAG** (not instead of)
- **If conflicts with RAG** → Trust RAG
- RAG is primary source, Web Search adds context

### How to Use

**CRITICAL - Convert relative dates to actual dates:**
- Today is **{current_date}**
- This weekend is **{next_weekend_dates}**

**Good queries:**
- "Versailles événements spéciaux 4-5 octobre 2025"
- "Versailles emergency closure 30 septembre 2025"

**Bad queries:**
- "Versailles ce week-end" ❌ (too vague)
- "Versailles today" ❌ (include actual date)

### Usage Tips
- Combine with RAG for complete answers (RAG = background, Web = current updates)
- LinkUp returns AI-synthesized answers with source citations
- Always cite that info comes from recent web sources