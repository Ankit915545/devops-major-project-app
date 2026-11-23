# Use minimal slim Python base image
FROM python:3.11-slim 

# Set environment variables preventing pyc generation and stdout buffering
ENV PYTHONDONTWRITEBYTECODE=1 \ 
      PYTHONUNBUFFERED=1 

# Establish working directory inside container
WORKDIR /app

# Install dependencies first to optimize Docker layer caching

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app.py .

# Create non-root user and set ownership for security hardening
RUN useradd -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose application port
EXPOSE 5000

# Specify container execution entrypoint
CMD ["python", "app.py"]
