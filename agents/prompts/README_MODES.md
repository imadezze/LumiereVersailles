# Agent Operation Modes

The Versailles assistant agent operates in two distinct modes based on prompt configuration:

## 🔬 API Test Mode

**Trigger:** `system_prompt_apitest.md` file exists

**Behavior:**
- **One-shot responses** - Provide complete answers immediately
- **No additional questions** - Agent doesn't ask for clarifications
- **Auto-invoke all tools** - Automatically uses RAG, Weather, Travel, Web Search
- **Make assumptions** - Reasonable defaults for missing information
- **Comprehensive output** - Full itinerary with all details

**Use Case:** API testing, automated benchmarking, quick demos

**To Enable:** Keep `system_prompt_apitest.md` file in prompts directory

---

## 💬 Normal Mode (Interactive)

**Trigger:** `system_prompt_apitest.md` does NOT exist

**Behavior:**
- **Interactive conversation** - Asks 2-3 clarifying questions
- **Personalized approach** - Gathers visitor preferences
- **Adaptive tone** - Adjusts communication style based on age/profile
- **Iterative refinement** - Offers changes and alternatives

**Questions Asked:**
1. **Who Are You?**
   - Visit style (chill vs intense)
   - Objectives (sightseeing, learning, photography)
   - Group composition (solo, family, elderly)
   - Time constraints and breaks
   - Special needs/constraints

2. **Tone Adaptation**
   - Young: Storytelling, adventure-style
   - Adults: Factual, historical context
   - Seniors: Deep history, accessibility focus

**Use Case:** Production chatbot, personalized customer service

**To Enable:** Remove or rename `system_prompt_apitest.md`

---

## Switching Modes

**Enable API Test Mode:**
```bash
# File exists → API test mode
ls agents/prompts/system_prompt_apitest.md
```

**Enable Normal Mode:**
```bash
# Remove or rename the file → Normal mode
mv agents/prompts/system_prompt_apitest.md agents/prompts/system_prompt_apitest.md.disabled
```

The agent automatically detects which mode to use on startup.