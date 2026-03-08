FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PROJECT_ROOT=/app

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create symlinks or setup paths if necessary
# The app backend is in phase-5-app-backend-frontend/
# We will run uvicorn from the root and specify the module path

EXPOSE 8000

# Default command: start the FastAPI app
CMD ["bash", "-c", "cd phase-5-app-backend-frontend && uvicorn main:app --host 0.0.0.0 --port 8000"]
