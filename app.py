import streamlit as st
import asyncio
import re
from openai import AsyncOpenAI
from posthog import Posthog
import time
from datetime import datetime
import pandas as pd
from suppress_warnings import suppress_popper_warnings
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="AEO Monitor",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS to increase sidebar width and force theme colors
st.markdown("""
    <style>
        /* Force theme colors to override browser caching */
        .stApp {
            background-color: #4C1D95;
        }
        /* Make app header black */
        [data-testid="stAppViewContainer"] > header,
        [data-testid="stHeader"],
        header[data-testid="stHeader"] {
            background-color: #000000 !important;
        }
        [data-testid="stSidebar"] {
            background-color: #6B21A8;
            min-width: 25.2rem;
            max-width: 25.2rem;
        }
        /* Ensure text contrast */
        .stApp, .stApp * {
            color: #FAF5FF !important;
        }
        /* Fix input and textarea text color for visibility */
        textarea, 
        textarea *,
        input[type="text"], 
        input[type="password"] {
            color: #1F2937 !important;
            background-color: #F9FAFB !important;
            box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.1) !important;
            border-radius: 0.375rem !important;
        }
        /* Ensure main content textarea text is visible */
        [data-testid="stMain"] textarea,
        [data-testid="stMain"] textarea * {
            color: #1F2937 !important;
        }
        /* Make password visibility toggle button visible - AGGRESSIVE approach */
        /* Target all password input container buttons */
        div[data-baseweb="input"] button,
        div[data-baseweb="input"] button *,
        div[data-baseweb="input"] button svg,
        div[data-baseweb="input"] button svg *,
        button[kind="icon"],
        button[kind="icon"] *,
        button[kind="icon"] svg,
        button[kind="icon"] svg *,
        button[data-testid="baseButton-icon"],
        button[data-testid="baseButton-icon"] *,
        button[data-testid="baseButton-icon"] svg,
        button[data-testid="baseButton-icon"] svg * {
            color: #111827 !important;
            fill: #111827 !important;
            stroke: #111827 !important;
            opacity: 1 !important;
            display: inline-block !important;
            visibility: visible !important;
            background-color: transparent !important;
        }
        div[data-baseweb="input"] button:hover,
        button[kind="icon"]:hover,
        button[kind="icon"]:hover * {
            filter: brightness(0.7) !important;
            background-color: rgba(0, 0, 0, 0.05) !important;
        }
        /* Ensure sidebar password toggle icons are visible - AGGRESSIVE approach */
        [data-testid="stSidebar"] div[data-baseweb="input"] button,
        [data-testid="stSidebar"] div[data-baseweb="input"] button *,
        [data-testid="stSidebar"] div[data-baseweb="input"] button svg,
        [data-testid="stSidebar"] div[data-baseweb="input"] button svg *,
        [data-testid="stSidebar"] button[kind="icon"],
        [data-testid="stSidebar"] button[kind="icon"] *,
        [data-testid="stSidebar"] button[kind="icon"] svg,
        [data-testid="stSidebar"] button[kind="icon"] svg *,
        [data-testid="stSidebar"] button[data-testid="baseButton-icon"],
        [data-testid="stSidebar"] button[data-testid="baseButton-icon"] *,
        [data-testid="stSidebar"] button[data-testid="baseButton-icon"] svg,
        [data-testid="stSidebar"] button[data-testid="baseButton-icon"] svg * {
            color: #111827 !important;
            fill: #111827 !important;
            stroke: #111827 !important;
            opacity: 1 !important;
            display: inline-block !important;
            visibility: visible !important;
            background-color: transparent !important;
        }
        [data-testid="stSidebar"] div[data-baseweb="input"] button:hover,
        [data-testid="stSidebar"] button[kind="icon"]:hover {
            filter: brightness(0.7) !important;
            background-color: rgba(0, 0, 0, 0.05) !important;
        }
        /* Maintain button and accent colors */
        .stButton > button {
            background-color: #D97706;
            color: #FAF5FF;
        }
        /* Sidebar-specific textarea styles */
        [data-testid="stSidebar"] textarea {
            color: #1F2937 !important;
            background-color: #F9FAFB !important;
            box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.1) !important;
            border-radius: 0.375rem !important;
            min-height: 100px !important;
        }
        /* Sidebar-specific text input styles */
        [data-testid="stSidebar"] input[type="text"],
        [data-testid="stSidebar"] input[type="password"] {
            color: #1F2937 !important;
            background-color: #F9FAFB !important;
            box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.1) !important;
            border-radius: 0.375rem !important;
        }
        /* Sidebar expander header - always darker purple */
        [data-testid="stSidebar"] .streamlit-expanderHeader,
        [data-testid="stSidebar"] button[kind="header"],
        [data-testid="stSidebar"] [data-testid="stExpanderToggleIcon"],
        [data-testid="stSidebar"] details summary {
            background-color: #581C87 !important;
            color: #FAF5FF !important;
        }
        [data-testid="stSidebar"] .streamlit-expanderHeader:hover,
        [data-testid="stSidebar"] button[kind="header"]:hover,
        [data-testid="stSidebar"] details summary:hover {
            background-color: #6B21A8 !important;
        }
        /* Force all sidebar expander components to use dark background */
        [data-testid="stSidebar"] [data-testid*="expander"] {
            background-color: transparent !important;
        }
        [data-testid="stSidebar"] [data-testid*="expander"] > div:first-child {
            background-color: #581C87 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Suppress Popper.js console warnings
suppress_popper_warnings()

# Password Protection
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'using_own_keys' not in st.session_state:
    st.session_state.using_own_keys = False

# Initialize instructions panel state (before authentication)
if 'show_instructions' not in st.session_state:
    st.session_state.show_instructions = False
if 'instructions_content' not in st.session_state:
    # Load instructions from markdown file
    # Use absolute path based on the app's location to avoid path issues
    import pathlib
    instructions_path = pathlib.Path(__file__).parent / 'INSTRUCTIONS.md'
    try:
        with open(instructions_path, 'r') as f:
            st.session_state.instructions_content = f.read()
    except FileNotFoundError:
        st.session_state.instructions_content = f"# Instructions\n\nInstructions file not found at: {instructions_path}"

APP_PASSWORD = os.getenv("APP_PASSWORD", "")

if not st.session_state.authenticated:
    st.title("🔒 AEO Monitoring Tool - Login")
    
    # Help button below title
    if st.button("📚 Need Help? View Getting Started Guide", type="secondary", key="help_btn"):
        st.session_state.show_instructions = True
        st.rerun()
    
    st.markdown("---")
    
    # Instructions panel on login page - Pure Streamlit approach
    if st.session_state.show_instructions:
        # Create a full-screen dialog using Streamlit's dialog feature
        @st.dialog("📚 Getting Started Guide", width="large")
        def show_instructions():
            # Display the instructions with native markdown rendering
            st.markdown(st.session_state.instructions_content)
            
            # Close button at the bottom
            if st.button("✕ Close Instructions", type="primary", use_container_width=True):
                st.session_state.show_instructions = False
                st.rerun()
        
        show_instructions()
    
    st.markdown("### Option 1: Login with Password")
    st.markdown("*Use the provided default API keys*")
    password_input = st.text_input("Enter Password", type="password", key="password")

    if st.button("🔐 Login with Password", use_container_width=True):
        if password_input == APP_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.using_own_keys = False
            st.rerun()
        else:
            st.error("❌ Incorrect password")

    st.markdown("---")
    st.markdown("### Option 2: Use Your Own API Keys")
    st.markdown("*Enter and save your own OpenRouter API key*")
    
    if st.button("🔑 Use My Own API Keys", type="primary", use_container_width=True):
        st.session_state.authenticated = True
        st.session_state.using_own_keys = True
        st.rerun()

    st.stop()

st.title("🔍 AEO Monitoring Tool")
st.markdown("*Answer Engine Optimization - SEO for LLMs with web search*")
st.markdown("---")

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")

# Load API keys from environment (only if using password authentication)
if st.session_state.using_own_keys:
    default_openrouter_key = ""
    default_posthog_key = ""
    api_keys_expanded = True
    st.sidebar.info("🔑 You are using your own API keys")
else:
    default_openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    default_posthog_key = os.getenv("POSTHOG_API_KEY", "")
    api_keys_expanded = False
    st.sidebar.success("🔐 Using default API keys")

# API Keys
with st.sidebar.expander("🔑 API Keys", expanded=api_keys_expanded):
    if st.session_state.using_own_keys:
        st.warning("⚠️ Please enter your OpenRouter API key below to use the tool")

    openrouter_key = st.text_input(
        "OpenRouter API Key",
        value=default_openrouter_key,
        type="password",
        help="Get your key from https://openrouter.ai",
        key="sidebar_openrouter_key"
    )
    posthog_key = st.text_input(
        "PostHog API Key (Optional)",
        value=default_posthog_key,
        type="password",
        help="Optional: For analytics tracking",
        key="sidebar_posthog_key"
    )
    enable_posthog = st.checkbox("Enable PostHog Analytics", value=bool(default_posthog_key))

st.sidebar.markdown("---")

# Keywords to monitor
st.sidebar.subheader("🎯 Keywords to Monitor")
keywords_input = st.sidebar.text_area(
    "Enter keywords (one per line)",
    value="measurement\nimpact\nanalysis\nstrategy",
    height=100
)
keywords = [k.strip().lower() for k in keywords_input.split("\n") if k.strip()]

# Domains to monitor
st.sidebar.subheader("🌐 Domains to Track")
domains_input = st.sidebar.text_area(
    "Enter domains (one per line)",
    value="thecompany.ai\nthecompany.com",
    height=100,
    key="domains_textarea"
)
domains = [d.strip().lower() for d in domains_input.split("\n") if d.strip()]

# Debug: Show parsed domains
if domains:
    with st.sidebar.expander("📋 Parsed Domains", expanded=False):
        for i, domain in enumerate(domains, 1):
            st.text(f"{i}. {domain}")

# Model selection
st.sidebar.subheader("🤖 Models")
available_models = [
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "perplexity/sonar-pro",
    "perplexity/sonar",
    "anthropic/claude-sonnet-4",
    "anthropic/claude-3.5-sonnet",
    "google/gemini-2.0-flash-thinking-exp",
    "google/gemini-pro-1.5"
]
selected_models = st.sidebar.multiselect(
    "Select models to query",
    available_models,
    default=["openai/gpt-4o", "perplexity/sonar-pro", "anthropic/claude-sonnet-4"]
)

# Debug: Session State Inspector
st.sidebar.markdown("---")
with st.sidebar.expander("🐛 Debug: Session State", expanded=False):
    st.json({
        "authenticated": st.session_state.get("authenticated", False),
        "using_own_keys": st.session_state.get("using_own_keys", False),
        "running": st.session_state.get("running", False),
        "results_count": len(st.session_state.get("results", [])),
        "session_keys": list(st.session_state.keys())
    })

# Main content area
col1, col2 = st.columns(2, gap="large")  # Equal width columns with large gap

with col1:
    st.subheader("📝 Test Prompts")
    prompts_input = st.text_area(
        "Enter prompts (one per line)",
        value="",
        height=200
    )
    prompts = [p.strip() for p in prompts_input.split("\n") if p.strip()]

with col2:
    st.subheader("📊 Quick Stats")
    st.metric("Keywords", len(keywords))
    st.metric("Domains", len(domains))
    st.metric("Models", len(selected_models))
    st.metric("Prompts", len(prompts))

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = []
if 'running' not in st.session_state:
    st.session_state.running = False


def _normalize_word(word: str) -> str:
    """Apply a tiny stemming heuristic for plural detection."""
    if word.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if word.endswith("es") and len(word) > 2 and (word[:-2].endswith(("s", "x", "z", "ch", "sh"))):
        return word[:-2]
    if word.endswith("s") and len(word) > 1 and not word.endswith(("ss", "is", "us")):
        return word[:-1]
    return word


def count_keyword_occurrences(content: str, keyword: str) -> int:
    """Count keyword occurrences with light plural handling."""
    keyword = keyword.strip().lower()
    if not keyword:
        return 0

    if " " in keyword:
        pattern = re.compile(rf"(?<!\w){re.escape(keyword)}(?!\w)")
        return len(pattern.findall(content))

    words = re.findall(r"[a-z0-9']+", content)
    count = 0
    for word in words:
        if keyword == word or keyword == _normalize_word(word):
            count += 1
    return count

# Async function to query a single model
async def query_model(client, model, prompt, posthog_client=None):
    try:
        logger.info(f"Starting query - Model: {model}, Prompt: {prompt[:60]}...")
        start_time = time.time()

        # Build request parameters
        request_params = {
            "model": f"{model}:online",
            "input": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }
        
        # Only add reasoning parameter for models that support it
        # Reasoning models typically have "thinking" or "reasoning" in their name
        if "thinking" in model.lower() or "reasoning" in model.lower() or "o1" in model.lower():
            request_params["reasoning"] = {"effort": "medium"}
            logger.info(f"Using reasoning parameter for model: {model}")

        response = await client.responses.create(**request_params)

        query_duration = time.time() - start_time
        logger.info(f"Response received - Model: {model}, Duration: {query_duration:.2f}s")

        content = response.output[0].content[0].text.lower()
        annotations = getattr(response.output[0].content[0], "annotations", [])

        # Check for keyword matches
        keyword_matches = []
        for keyword in keywords:
            count = count_keyword_occurrences(content, keyword)
            if count > 0:
                keyword_matches.append({
                    "keyword": keyword,
                    "count": count
                })
                logger.info(f"Keyword match - Model: {model}, Keyword: '{keyword}', Count: {count}")

        # Check for domain matches in citations
        domain_matches = []
        citation_urls = []
        for annotation in annotations:
            url = annotation.url.lower()
            citation_urls.append(url)
            for domain in domains:
                if domain in url:
                    domain_matches.append({
                        "domain": domain,
                        "url": url
                    })
                    logger.info(f"Domain match - Model: {model}, Domain: '{domain}', URL: {url}")

        result = {
            "model": model,
            "prompt": prompt,
            "content": response.output[0].content[0].text,
            "keyword_matches": keyword_matches,
            "domain_matches": domain_matches,
            "citation_urls": citation_urls,
            "total_citations": len(annotations),
            "timestamp": datetime.now().isoformat(),
            "success": True
        }

        # Send to PostHog if enabled
        if posthog_client and enable_posthog:
            event_properties = {
                "model": model,
                "prompt": prompt,
                "keyword_matches": len(keyword_matches),
                "domain_matches": len(domain_matches),
                "total_citations": len(annotations),
                "query_duration": query_duration
            }
            posthog_client.capture(
                distinct_id=f"aeo_monitor_{model}",
                event="aeo_query_completed",
                properties=event_properties
            )
            logger.info(f"PostHog event sent - Model: {model}, Event: aeo_query_completed")

        logger.info(f"Query completed successfully - Model: {model}, Keywords: {len(keyword_matches)}, Domains: {len(domain_matches)}, Citations: {len(annotations)}")
        return result

    except Exception as e:
        logger.error(f"Query failed - Model: {model}, Error: {str(e)}")
        return {
            "model": model,
            "prompt": prompt,
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

# Async function to run all queries with progress tracking
async def run_all_queries(api_key, models, prompts, posthog_client=None, progress_callback=None):
    config = {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": api_key
    }

    logger.info(f"Starting batch queries - Models: {len(models)}, Prompts: {len(prompts)}, Total: {len(models) * len(prompts)}")
    async_client = AsyncOpenAI(**config)

    tasks = []
    for model in models:
        for prompt in prompts:
            tasks.append(query_model(async_client, model, prompt, posthog_client))

    # Track progress as tasks complete
    results = []
    total = len(tasks)
    for i, task in enumerate(asyncio.as_completed(tasks)):
        result = await task
        results.append(result)

        # Call progress callback if provided
        if progress_callback:
            progress_callback(i + 1, total, result)

        logger.info(f"Progress: {i + 1}/{total} queries completed")

    logger.info(f"Batch queries completed - Total: {total}, Successful: {sum(1 for r in results if r.get('success'))}")
    return results

# Run button
st.markdown("---")
run_button = st.button("🚀 Run AEO Monitor", type="primary", width='stretch')

if run_button:
    if not openrouter_key:
        st.error("❌ Please enter your OpenRouter API Key in the sidebar")
    elif not selected_models:
        st.error("❌ Please select at least one model")
    elif not prompts:
        st.error("❌ Please enter at least one prompt")
    else:
        st.session_state.running = True

        # Initialize PostHog if enabled
        posthog_client = None
        if enable_posthog and posthog_key:
            posthog_client = Posthog(
                project_api_key=posthog_key,
                host='https://app.posthog.com'
            )

        total_queries = len(selected_models) * len(prompts)

        with st.spinner(f"Running {total_queries} queries..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            detail_text = st.empty()

            start_time = time.time()

            # Progress callback to update UI
            def update_progress(completed, total, result):
                progress_bar.progress(completed / total)
                model = result.get('model', 'Unknown')
                success = result.get('success', False)
                status_icon = "✅" if success else "❌"
                status_text.write(f"Progress: {completed}/{total} - {status_icon} {model}")

                # Show match details
                if success:
                    kw_matches = len(result.get('keyword_matches', []))
                    dm_matches = len(result.get('domain_matches', []))
                    if kw_matches > 0 or dm_matches > 0:
                        detail_text.success(f"🎯 Found {kw_matches} keyword matches, {dm_matches} domain citations")

            # Run queries
            logger.info(f"User initiated query run - Total queries: {total_queries}")
            results = asyncio.run(run_all_queries(
                openrouter_key,
                selected_models,
                prompts,
                posthog_client,
                update_progress
            ))

            end_time = time.time()
            duration = end_time - start_time

            st.session_state.results = results
            progress_bar.progress(1.0)
            status_text.success(f"✅ Completed {total_queries} queries in {duration:.2f} seconds")
            logger.info(f"Query run completed - Duration: {duration:.2f}s")

        st.session_state.running = False

# Display Results
if st.session_state.results:
    st.markdown("---")
    st.header("📊 Results")

    # Debug: Raw Results JSON viewer
    with st.expander("🔍 Debug: Raw Results Data", expanded=False):
        st.json(st.session_state.results)

    # Summary statistics
    successful_queries = [r for r in st.session_state.results if r.get("success")]
    failed_queries = [r for r in st.session_state.results if not r.get("success")]

    total_keyword_matches = sum(len(r.get("keyword_matches", [])) for r in successful_queries)
    total_domain_matches = sum(len(r.get("domain_matches", [])) for r in successful_queries)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Queries", len(st.session_state.results))
    col2.metric("Successful", len(successful_queries))
    col3.metric("Keyword Matches", total_keyword_matches)
    col4.metric("Domain Citations", total_domain_matches)

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Detailed Results", "📈 Summary Table", "❌ Errors"])

    with tab1:
        for i, result in enumerate(successful_queries):
            with st.expander(f"**{result['model']}** - {result['prompt'][:60]}...", expanded=False):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown("**Response:**")
                    st.write(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])

                with col2:
                    st.markdown("**Matches:**")
                    if result['keyword_matches']:
                        st.success(f"✅ {len(result['keyword_matches'])} keyword match(es)")
                        for match in result['keyword_matches']:
                            st.write(f"- **{match['keyword']}**: {match['count']} mention(s)")
                    else:
                        st.warning("No keyword matches")

                    if result['domain_matches']:
                        st.success(f"✅ {len(result['domain_matches'])} domain citation(s)")
                        for match in result['domain_matches']:
                            st.write(f"- {match['domain']}")
                    else:
                        st.warning("No domain citations")

                    st.info(f"📎 {result['total_citations']} total citations")

    with tab2:
        # Create summary dataframe
        summary_data = []
        for result in successful_queries:
            summary_data.append({
                "Model": result['model'],
                "Prompt": result['prompt'][:50] + "...",
                "Keyword Matches": len(result.get('keyword_matches', [])),
                "Domain Citations": len(result.get('domain_matches', [])),
                "Total Citations": result.get('total_citations', 0)
            })

        if summary_data:
            df = pd.DataFrame(summary_data)
            st.dataframe(df, width='stretch')

            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"aeo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    with tab3:
        if failed_queries:
            st.error(f"Found {len(failed_queries)} failed queries")
            for result in failed_queries:
                st.warning(f"**{result['model']}** - {result['prompt'][:60]}...")
                st.code(result.get('error', 'Unknown error'))
        else:
            st.success("✅ No errors!")

# Footer
st.markdown("---")
st.markdown("""
### 💡 Tips
- Use consistent keywords, domains, and prompts over time to track changes
- Run queries regularly (daily/weekly) to monitor AEO performance
- Combine with content marketing campaigns to measure impact
- Enable PostHog analytics for historical tracking and dashboards
""")

# Copyright footer
st.markdown(
    """
    <div style='text-align: right; color: #666; font-size: 0.9em; margin-top: 2rem;'>
        @2025 LikeSugarAI
    </div>
    """,
    unsafe_allow_html=True
)
