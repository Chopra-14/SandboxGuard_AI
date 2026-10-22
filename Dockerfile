FROM python:3.11-slim

WORKDIR /app

# Upgrade pip to ensure the latest package index
RUN python -m pip install --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY api ./api
COPY agent ./agent

EXPOSE 8080

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
