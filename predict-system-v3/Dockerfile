FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and dependencies
COPY pyproject.toml ./

# Install dependencies using pip (since pyproject.toml contains standard project dependencies)
# We can use pip to install the package dependencies directly
RUN pip install --no-cache-dir .

# Copy source tree
COPY . .

# Expose web server ports (8501 for Streamlit, 8000 for FastAPI)
EXPOSE 8501
EXPOSE 8000

ENV PORT=8501

# Start Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
