# AEO Monitor - Streamlit App

Answer Engine Optimization (AEO) monitoring tool for tracking brand visibility in AI model responses.

## Features

- Query multiple AI models simultaneously via OpenRouter
- Monitor keyword mentions in responses
- Track domain citations across different models
- Real-time progress tracking with async execution
- Export results to CSV
- Optional PostHog analytics integration
- Interactive web interface built with Streamlit

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get your API keys:
   - OpenRouter: https://openrouter.ai (required)
   - PostHog: https://posthog.com (optional, for analytics)

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at http://localhost:8501

## Configuration

### In the Sidebar:
1. **API Keys**: Enter your OpenRouter API key (required) and PostHog key (optional)
2. **Keywords**: Add keywords to monitor (one per line)
3. **Domains**: Add domains to track in citations (one per line)
4. **Models**: Select which AI models to query

### In the Main Area:
1. **Prompts**: Enter test questions (one per line)
2. Click "Run AEO Monitor" to execute queries

## Results

The app provides three views:
- **Detailed Results**: Full responses with match highlights
- **Summary Table**: Quick overview with downloadable CSV
- **Errors**: Any failed queries with error messages

## Tips

- Use consistent keywords/prompts over time to track changes
- Run queries regularly (daily/weekly) to monitor trends
- Combine with marketing campaigns to measure impact
- Enable PostHog for historical tracking and dashboards

## Original Source

Converted from Colab notebook: https://colab.research.google.com/drive/1OdD8YKJpm8YK4NUsIGG8M_w1YFz4nJQO
