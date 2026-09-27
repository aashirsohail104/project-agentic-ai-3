FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY requirements.txt pyproject.toml setup.py ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY api/ ./api/
COPY chainlit.md ./
COPY .python-version ./

# Install the project in editable mode
RUN pip install --no-cache-dir -e . --force-reinstall --no-deps

# Set Chainlit config
ENV CHAINLIT_APP_ROOT=/tmp
ENV CHAINLIT_HOST=0.0.0.0
ENV CHAINLIT_PORT=8000
ENV PYTHONPATH=/app

EXPOSE 8000

# Run Chainlit
CMD ["python", "-m", "chainlit", "run", "api/index.py", "--port", "8000", "--host", "0.0.0.0"]