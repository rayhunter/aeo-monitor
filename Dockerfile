# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for numpy/pandas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY suppress_warnings.py .
COPY aeo_monitor.py .

# Create .streamlit directory for config
RUN mkdir -p .streamlit
COPY .streamlit/config.toml .streamlit/

# Expose the port Streamlit runs on (Railway will override with $PORT)
EXPOSE 8501

# Run the application
# Note: Environment variables (API keys, PORT) are injected at runtime by Railway
# Use exec form with sh to properly expand PORT variable
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true"]

