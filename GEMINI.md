# AEO Monitor

**Answer Engine Optimization (AEO) Monitoring Tool**

This project is a Streamlit-based application designed to track brand visibility across various AI models (like GPT-4, Claude, Perplexity) by querying them via OpenRouter. It monitors keyword mentions and domain citations in AI responses.

## Project Structure

*   **`app.py`**: The main entry point for the Streamlit application. Contains the UI logic, async query handling, and results processing.
*   **`manage_app.sh`**: A shell script for managing the application process (start, stop, status, logs), useful for production-like deployments.
*   **`requirements.txt`**: Python dependencies.
*   **`aeo_monitor.py`**: A reference script (likely exported from Google Colab) that served as the prototype for `app.py`.
*   **`INSTRUCTIONS.md`**: User guide content displayed within the app.
*   **`MANAGEMENT_GUIDE.md`**: Documentation for using `manage_app.sh`.

## Setup & Usage

### 1. Installation

Ensure you have Python installed, then install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configuration

The app supports two modes:
*   **Password-protected (Shared Keys):** Create a `.env` file with `APP_PASSWORD`, `OPENROUTER_API_KEY`, and optional `POSTHOG_API_KEY`.
*   **Bring Your Own Keys (BYOK):** Users provide their OpenRouter key in the UI.

### 3. Running the App

**Directly with Streamlit:**

```bash
streamlit run app.py
```

**Using the Management Script (Background Process):**

```bash
./manage_app.sh start   # Start in background
./manage_app.sh status  # Check status
./manage_app.sh logs    # View logs
./manage_app.sh stop    # Stop the app
```

## Architecture & Development

*   **Frontend:** Built with [Streamlit](https://streamlit.io/).
*   **API Interaction:** Uses `AsyncOpenAI` client to communicate with [OpenRouter](https://openrouter.ai/).
*   **Concurrency:** Leverages Python's `asyncio` to query multiple models in parallel.
*   **Analytics:** Optional integration with [PostHog](https://posthog.com/) for tracking query stats.
*   **State Management:** Heavy use of `st.session_state` for managing authentication, query progress, and results.

### Key Conventions

*   **Async/Await:** All model queries are performed asynchronously to ensure UI responsiveness.
*   **Environment Variables:** Sensitive data (API keys, passwords) should be loaded from `.env` or provided via UI inputs.
*   **Logging:** Comprehensive logging is set up in `app.py` and can be viewed via stdout or `manage_app.sh logs`.
*   **Styling:** Custom CSS is injected in `app.py` to enforce specific theme colors.

## Testing

*   **`test_app.py`**: Contains tests for the application logic.
*   **`test_shutdown.py`**: Tests the graceful shutdown mechanism.
*   Run tests using `pytest`:
    ```bash
    pytest
    ```
