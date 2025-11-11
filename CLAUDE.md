# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AEO Monitor is a Streamlit web application for Answer Engine Optimization (AEO) - essentially SEO for LLMs with web search. It monitors brand visibility in AI model responses by querying multiple AI models simultaneously via OpenRouter, tracking keyword mentions and domain citations across different models.

Originally converted from a Colab notebook to a production Streamlit app with password protection, async execution, and optional analytics.

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
Create a `.env` file with:
- `OPENROUTER_API_KEY` (required) - API key from https://openrouter.ai
- `POSTHOG_API_KEY` (optional) - For analytics tracking
- `APP_PASSWORD` (optional) - Password protection for the app

## Architecture

### Core Application Flow (app.py)

1. **Password Protection** (lines 24-40): Uses session state to gate access if `APP_PASSWORD` is set
2. **Configuration Sidebar** (lines 46-105): API keys, keywords, domains, and model selection
3. **Async Query Engine** (lines 132-225):
   - `query_model()`: Single async query to OpenRouter using OpenAI Responses API (not Chat Completions API)
   - `run_all_queries()`: Orchestrates parallel execution across all models and prompts
   - Uses `asyncio.gather()` for concurrent API calls
4. **Results Processing** (lines 274-354): Three-tab interface for detailed results, summary table, and errors

### Key Technical Details

**OpenRouter Integration**:
- Uses OpenAI client library pointed at OpenRouter's base URL
- Models are called with `:online` suffix to enable web search (e.g., `openai/gpt-4o:online`)
- Uses the newer `responses.create()` API instead of `chat.completions.create()`
- Response structure: `response.output[0].content[0].text` for content
- Citations extracted from `annotations` attribute containing URL citations

**Matching Logic** (lines 151-172):
- Keyword matches: Case-insensitive substring search with count tracking
- Domain matches: Extracted from annotation URLs in citations
- All searches performed on lowercased content

**Session State Management**:
- `authenticated`: Boolean for password gate
- `results`: List of result dictionaries from queries
- `running`: Boolean flag for execution state

**PostHog Analytics** (lines 185-197):
- Optional telemetry sent per successful query
- Tracks model, prompt, match counts, and citation counts
- Uses distinct_id format: `aeo_monitor_{model}`

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
- All matching is case-insensitive - content and URLs are lowercased before comparison
- Error handling stores failed queries separately with `success: False` flag
- Results include full response content but UI truncates to 500 chars in detailed view
- The `reasoning={"effort": "medium"}` parameter is optional and only works with reasoning models
