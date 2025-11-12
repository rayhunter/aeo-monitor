# AEO Monitor - Streamlit App

Answer Engine Optimization (AEO) monitoring tool for tracking brand visibility in AI model responses.

## Features

- **Dual authentication modes**: Password-protected shared keys or bring-your-own-keys
- Query multiple AI models simultaneously via OpenRouter
- **Smart keyword matching**: Word-boundary aware with automatic plural detection (e.g., "strategy" matches "strategies")
- Track domain citations across different models
- Real-time progress tracking with async execution
- Export results to CSV
- Optional PostHog analytics integration
- Interactive web interface built with Streamlit
- **Comprehensive observability**: Python logging, debug tools, session state inspection
- **Granular progress updates**: Live updates as each query completes with match details
- **Graceful shutdown**: Proper cleanup of async tasks and connections on Ctrl+C
- **Process management**: Shell script for easy start/stop/restart operations

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Choose your authentication mode and configure accordingly (see Configuration section below)

## Usage

### Quick Start

Run the Streamlit app directly:

```bash
streamlit run app.py
```

The app will open in your browser at <http://localhost:8501>

### Process Management (Recommended)

Use the management script for better control:

```bash
# Start the app in background
./manage_app.sh start

# Check status
./manage_app.sh status

# Stop gracefully
./manage_app.sh stop

# View logs
./manage_app.sh logs

# Force cleanup if needed
./manage_app.sh cleanup
```

See [MANAGEMENT_GUIDE.md](MANAGEMENT_GUIDE.md) for complete documentation on process management and graceful shutdown features.

## Configuration

The app supports **two authentication modes**:

### Option 1: Password-Protected Deployment (Shared API Keys)

For deploying the app with your own API keys that users access via password:

1. Create a `.env` file in the project root:

   ```bash
   APP_PASSWORD=your_secure_password
   OPENROUTER_API_KEY=your_openrouter_key_from_openrouter.ai
   POSTHOG_API_KEY=your_posthog_key_optional
   ```

2. Run the app - users will see a login screen with two options

3. Users select "Login with Password" and enter the password

4. They can then use the app with your pre-configured OpenRouter key

### Option 2: Bring Your Own Keys (BYOK)

For allowing users to use their own OpenRouter API keys:

1. No `.env` file needed (or only set `POSTHOG_API_KEY` if desired)

2. Run the app - users will see a login screen

3. Users select "Use My Own API Keys"

4. They enter their own OpenRouter API key in the sidebar

### Using the App

Once authenticated, configure in the **Sidebar**:

1. **API Keys** (if using BYOK): Enter your OpenRouter API key
2. **Keywords**: Add keywords to monitor (one per line) - supports plural matching
3. **Domains**: Add domains to track in citations (one per line)
4. **Models**: Select which AI models to query

In the **Main Area**:

1. **Prompts**: Enter test questions (one per line)
2. Click "Run AEO Monitor" to execute queries

## Results

The app provides three views:

- **Detailed Results**: Full responses with match highlights
- **Summary Table**: Quick overview with downloadable CSV
- **Errors**: Any failed queries with error messages

## Observability & Debugging

The app includes comprehensive monitoring tools to help you understand data flow and troubleshoot issues:

### 1. Terminal Logging

When running the app, detailed logs appear in your terminal showing:

- Query start/completion with duration for each model
- Keyword and domain matches as they're detected
- PostHog event tracking confirmations
- Progress updates and batch statistics
- Error details with full stack traces

### 2. Debug Tools in UI

**Raw Results Data** (in Results section):

- Expandable "🔍 Debug: Raw Results Data" panel
- View complete JSON structure of all query results
- Inspect response content, matches, citations, and timestamps

**Session State Inspector** (in Sidebar):

- Expandable "🐛 Debug: Session State" panel
- Monitor authentication status, running state, and result counts
- View all session state keys

### 3. Live Progress Tracking

During query execution, you'll see:

- Real-time progress bar with completion percentage
- Individual model completion status (✅/❌)
- Immediate match notifications when keywords/domains are found
- Total execution time upon completion

### 4. PostHog Analytics

If enabled, all queries send detailed events to PostHog including:

- Model and prompt information
- Match counts (keywords and domains)
- Citation counts
- Query duration metrics
- Access your PostHog dashboard for historical trends and visualizations

## Tips

- Use consistent keywords/prompts over time to track changes
- Run queries regularly (daily/weekly) to monitor trends
- Combine with marketing campaigns to measure impact
- Enable PostHog for historical tracking and dashboards

## Original Source

This is a derivative application based off of the following Google Colab notebook: <https://colab.research.google.com/drive/1OdD8YKJpm8YK4NUsIGG8M_w1YFz4nJQO>
