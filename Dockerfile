# Stage 1: Runtime
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy source code and default data into container
COPY src/ ./src/
COPY data/ ./data/
COPY main.py .

# Create output directory for volume mounting
RUN mkdir -p output

# Run the ETL script by default
ENTRYPOINT ["python", "main.py"]
