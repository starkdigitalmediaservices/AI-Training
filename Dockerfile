# Calculator Agent Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements_calculator.txt .
RUN pip install --no-cache-dir -r requirements_calculator.txt

# Copy application code
COPY calculator_agent_network.py .
COPY network_config.py .
COPY .env .

# Expose port
EXPOSE 5001

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Run the application
CMD ["python", "calculator_agent_network.py"]
