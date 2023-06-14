FROM python:3.10-slim-buster

# Step 1: Setup Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Step 2: Install Utilities
RUN apt-get update && \
    apt-get install -y curl make build-essential

# Step 3: Create Application Directory
WORKDIR /app

# Step 4: Install Python Modules
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy Application
COPY .. /app/server

# Step 6: Set Working Directory
WORKDIR /app/server

# Step 7: Run Application
CMD ["python", "server.py"]
