# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AEO Monitor is a Streamlit web application for Answer Engine Optimization (AEO) - essentially SEO for LLMs with web search. It monitors brand visibility in AI model responses by querying multiple AI models simultaneously via OpenRouter, tracking keyword mentions and domain citations across different models.

Originally converted from a Colab notebook to a production Streamlit app with dual authentication options (password or BYOK), async execution, comprehensive logging, and optional analytics.

## Commands

### Running the Application
```bash
streamlit run app.py
```
The app will be available at http://localhost:8501

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Environment Setup

The app supports two authentication modes:

**Option 1: Password-Protected Deployment (shared API keys)**
Create a `.env` file with:
- `APP_PASSWORD` (required) - Password to gate access
- `OPENROUTER_API_KEY` (required) - Your OpenRouter API key from https://openrouter.ai
- `POSTHOG_API_KEY` (optional) - For analytics tracking

**Option 2: Bring Your Own Keys (BYOK only)**
No environment variables required. Users enter their own OpenRouter API key in the UI.

**Optional for both modes:**
- `POSTHOG_API_KEY` - PostHog analytics tracking

## Architecture

### Core Application Flow (app.py)

1. **Dual Authentication System** (lines 44-78):
   - **Option 1**: Password login - uses default API keys from environment variables
   - **Option 2**: Bring Your Own Keys (BYOK) - bypasses password, requires user to enter their own OpenRouter key
   - Uses session state to manage `authenticated` and `using_own_keys` flags

2. **Configuration Sidebar** (lines 84-165):
   - API keys input (with conditional expansion based on auth method)
   - Keywords to monitor (one per line)
   - Domains to track (one per line)
   - Model selection from available OpenRouter models
   - Debug panel showing session state (collapsible)

3. **Enhanced Keyword Matching** (lines 193-219):
   - `_normalize_word()`: Light stemming for plural detection (e.g., "strategies" → "strategy")
   - `count_keyword_occurrences()`: Word-boundary aware matching with plural handling
   - Multi-word phrase support using regex

4. **Async Query Engine** (lines 222-349):
   - `query_model()`: Single async query to OpenRouter using OpenAI Responses API (not Chat Completions API)
   - Conditional reasoning parameter: only added for models with "thinking", "reasoning", or "o1" in name (line 241-243)
   - `run_all_queries()`: Orchestrates parallel execution with live progress tracking
   - Uses `asyncio.as_completed()` for real-time updates as queries finish

5. **Results Processing** (lines 418-501): Three-tab interface for detailed results, summary table, and errors

### Key Technical Details

**OpenRouter Integration**:
- Uses OpenAI client library pointed at OpenRouter's base URL
- Models are called with `:online` suffix to enable web search (e.g., `openai/gpt-4o:online`)
- Uses the newer `responses.create()` API instead of `chat.completions.create()`
- Response structure: `response.output[0].content[0].text` for content
- Citations extracted from `annotations` attribute containing URL citations

**Matching Logic** (lines 193-276):
- Keyword matches: Word-boundary aware with plural handling (e.g., "strategy" matches "strategies")
- Multi-word phrase support using regex for exact phrase matching
- Domain matches: Extracted from annotation URLs in citations
- All searches performed on lowercased content

**Session State Management**:
- `authenticated`: Boolean for password gate
- `using_own_keys`: Boolean flag for BYOK vs password auth mode
- `results`: List of result dictionaries from queries
- `running`: Boolean flag for execution state

**Logging** (lines 12-22):
- Python logging module configured at INFO level
- Logs query start/completion, match detection, PostHog events, and errors
- All logs output to terminal for debugging

**PostHog Analytics** (lines 291-305):
- Optional telemetry sent per successful query
- Tracks model, prompt, match counts, citation counts, and query duration
- Uses distinct_id format: `aeo_monitor_{model}`
- Event name: `aeo_query_completed`

### Helper Modules

**suppress_warnings.py**: Injects JavaScript to suppress Popper.js console warnings in Streamlit UI using `streamlit.components.v1`

**aeo_monitor.py**: Original Colab notebook code kept for reference - not used in production app

## Data Flow

```
User Input (Sidebar) → Query Configuration → Async Execution → OpenRouter API (multiple models)
                                                                         ↓
Results Storage ← Match Detection ← Response Parsing ← API Response
       ↓
Three-tab Display (Detailed/Summary/Errors) + CSV Export + Optional PostHog Events
```

## Important Implementation Notes

- When modifying API calls, remember the app uses the **Responses API** (`responses.create()`), not the Chat Completions API
- Model identifiers must include `:online` suffix for web search to enable citations
- The `reasoning={"effort": "medium"}` parameter is **conditionally added** only for models containing "thinking", "reasoning", or "o1" in their name (app.py:241-243)
- Keyword matching uses word-boundary detection and light stemming for plural handling
- All matching is case-insensitive - content and URLs are lowercased before comparison
- Error handling stores failed queries separately with `success: False` flag
- Results include full response content but UI truncates to 500 chars in detailed view
- Progress tracking uses `asyncio.as_completed()` for real-time updates as each query finishes
- Debug panels available in both sidebar (session state) and results section (raw JSON)
