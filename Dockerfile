# Use official Python image
FROM python:3.11-slim

# Install supervisor
RUN apt-get update && apt-get install -y supervisor && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Configure supervisor
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create volume for logs
VOLUME /var/log/supervisor

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=api.py
ENV FLASK_ENV=production

# Run supervisor
CMD ["/usr/bin/supervisord"]

# Set container name
LABEL name="apievolutionbet"

# Set restart policy
LABEL restart="always"