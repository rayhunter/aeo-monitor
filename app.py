import streamlit as st
import asyncio
from openai import AsyncOpenAI
from posthog import Posthog
import time
from datetime import datetime
import pandas as pd
from suppress_warnings import suppress_popper_warnings

st.set_page_config(
    page_title="AEO Monitor",
    page_icon="🔍",
    layout="wide"
)

# Suppress Popper.js console warnings
suppress_popper_warnings()

st.title("🔍 AEO Monitoring Tool")
st.markdown("*Answer Engine Optimization - SEO for LLMs with web search*")
st.markdown("---")

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")

# API Keys
with st.sidebar.expander("🔑 API Keys", expanded=True):
    openrouter_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        help="Get your key from https://openrouter.ai"
    )
    posthog_key = st.text_input(
        "PostHog API Key (Optional)",
        type="password",
        help="Optional: For analytics tracking"
    )
    enable_posthog = st.checkbox("Enable PostHog Analytics", value=False)

st.sidebar.markdown("---")

# Keywords to monitor
st.sidebar.subheader("🎯 Keywords to Monitor")
keywords_input = st.sidebar.text_area(
    "Enter keywords (one per line)",
    value="appsmith\nappsmithai",
    height=100
)
keywords = [k.strip().lower() for k in keywords_input.split("\n") if k.strip()]

# Domains to monitor
st.sidebar.subheader("🌐 Domains to Track")
domains_input = st.sidebar.text_area(
    "Enter domains (one per line)",
    value="appsmith.com\nappsmithai.com",
    height=100
)
domains = [d.strip().lower() for d in domains_input.split("\n") if d.strip()]

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

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Test Prompts")
    prompts_input = st.text_area(
        "Enter prompts (one per line)",
        value="What's the best open source low code tool for building apps in 2025?\nWhat's the best drag and drop app builder with SSO in 2025?",
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

# Async function to query a single model
async def query_model(client, model, prompt, posthog_client=None):
    try:
        response = await client.responses.create(
            model=f"{model}:online",
            input=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=False,
            reasoning={"effort": "medium"}
        )

        content = response.output[0].content[0].text.lower()
        annotations = getattr(response.output[0].content[0], "annotations", [])

        # Check for keyword matches
        keyword_matches = []
        for keyword in keywords:
            if keyword in content:
                count = content.count(keyword)
                keyword_matches.append({
                    "keyword": keyword,
                    "count": count
                })

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
            posthog_client.capture(
                distinct_id=f"aeo_monitor_{model}",
                event="aeo_query_completed",
                properties={
                    "model": model,
                    "prompt": prompt,
                    "keyword_matches": len(keyword_matches),
                    "domain_matches": len(domain_matches),
                    "total_citations": len(annotations)
                }
            )

        return result

    except Exception as e:
        return {
            "model": model,
            "prompt": prompt,
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

# Async function to run all queries
async def run_all_queries(api_key, models, prompts, posthog_client=None):
    config = {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": api_key
    }

    async_client = AsyncOpenAI(**config)

    tasks = []
    for model in models:
        for prompt in prompts:
            tasks.append(query_model(async_client, model, prompt, posthog_client))

    results = await asyncio.gather(*tasks)
    return results

# Run button
st.markdown("---")
run_button = st.button("🚀 Run AEO Monitor", type="primary", use_container_width=True)

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

            start_time = time.time()

            # Run queries
            results = asyncio.run(run_all_queries(
                openrouter_key,
                selected_models,
                prompts,
                posthog_client
            ))

            end_time = time.time()
            duration = end_time - start_time

            st.session_state.results = results
            progress_bar.progress(100)
            status_text.success(f"✅ Completed {total_queries} queries in {duration:.2f} seconds")

        st.session_state.running = False

# Display Results
if st.session_state.results:
    st.markdown("---")
    st.header("📊 Results")

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
            st.dataframe(df, use_container_width=True)

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
