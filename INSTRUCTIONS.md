## 🔍 What is AEO Monitor?

**AEO** stands for **Answer Engine Optimization** - it's like SEO (Search Engine Optimization) but for AI chatbots and language models.

### The Problem It Solves
When people ask questions to AI chatbots (like ChatGPT, Claude, Perplexity, etc.), they get answers that often cite sources. If you're a company or brand, you want to know:
- **Does my brand get mentioned?**
- **Do my websites get cited?**
- **Which AI models mention me?**
- **How often does it happen?**

This app helps you track and measure your visibility across different AI models.

---

## 🎯 How To Use It

### Step 1: Start the App
```bash
streamlit run app.py
```
This opens it in your browser at http://localhost:8501

### Step 2: Login
You'll see two options:
- **Login with Password** - Uses pre-configured API keys (if you have the password)
- **Use My Own API Keys** - Enter your own OpenRouter API key (get one at https://openrouter.ai)

### Step 3: Configure in the Sidebar

**🔑 API Keys** (if using your own):
- Enter your OpenRouter API key
- Optional: PostHog key for analytics

**🎯 Keywords to Monitor**:
- Enter words/phrases you want to track (one per line)
- Example: "Tesla", "electric vehicle", "autonomous driving"
- Smart matching: "strategy" also matches "strategies"

**🌐 Domains to Track**:
- Enter your website domains (one per line)
- Example: "tesla.com", "tesla.ai"
- The app checks if these appear in AI citations

**🤖 Models**:
- Select which AI models to test (GPT-4, Claude, Perplexity, etc.)
- You can test multiple at once

### Step 4: Enter Test Prompts

In the main area:
- **📝 Test Prompts**: Enter questions you want to ask the AI models
- One question per line
- Example: "What are the best electric car companies?"

### Step 5: Run the Monitor

Click **🚀 Run AEO Monitor**

The app will:
1. Send your prompts to all selected AI models
2. Check each response for your keywords
3. Check if your domains are cited
4. Show real-time progress

### Step 6: View Results

Three tabs show different views:

**📋 Detailed Results**:
- Full responses from each model
- Highlights which keywords were found
- Shows domain citations

**📈 Summary Table**:
- Quick overview of all results
- Download as CSV for analysis

**❌ Errors**:
- Any failed queries

---

## 💡 Real-World Example

Let's say you work for **Acme Analytics**:

**Configure:**
- Keywords: `analytics`, `data insights`, `business intelligence`
- Domains: `acme.com`, `acme.ai`
- Models: GPT-4, Claude, Perplexity

**Test Prompts:**
```
What are the best analytics tools for businesses?
How can I analyze customer data?
Which companies offer business intelligence solutions?
```

**Results:**
- See which models mention "analytics" and how often
- Track if acme.com appears in citations
- Compare visibility across different AI models

---

## 🎓 Why This Matters

- **Track brand awareness** in AI responses
- **Measure content strategy** effectiveness
- **Monitor competitors** (track their mentions too)
- **Optimize for AI** - understand what gets cited
- **Regular monitoring** - run weekly/monthly to track trends

---

## 🔧 Pro Tips

1. **Use realistic prompts** - questions real users might ask
2. **Track over time** - run the same prompts weekly to see trends
3. **Test variations** - try different ways people might ask questions
4. **Export data** - download CSV for deeper analysis
5. **Use multiple models** - different AIs behave differently

---

## ⚙️ Advanced Features

- **Theme toggle**: Switch between dark/light themes in sidebar
- **Debug tools**: Expand "Debug: Session State" to see internal data
- **Process management**: Use `./manage_app.sh` for production deployments
- **Analytics**: Enable PostHog to track historical data

---

**Need help?** The app has built-in debug tools - check the sidebar expandable sections to see what's being tracked!

