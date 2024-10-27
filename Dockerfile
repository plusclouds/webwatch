# Start with an official Python 3 image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Set up argument for environment
ARG ENVIRONMENT=development
ENV ENVIRONMENT=${ENVIRONMENT}

# Install dependencies and download Nikto manually
RUN apt-get update && \
    apt-get install -y wget perl libtime-hires-perl && \
    wget https://github.com/sullo/nikto/archive/refs/heads/master.zip && \
    apt-get install -y unzip && \
    unzip master.zip && \
    mv nikto-master /opt/nikto && \
    ln -s /opt/nikto/program/nikto.pl /usr/local/bin/nikto && \
    apt-get remove -y unzip wget && \
    rm -rf /var/lib/apt/lists/* master.zip

# Ensure nikto is executable
RUN chmod +x /usr/local/bin/nikto

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app files
COPY . .

# Create the directory for scan results
RUN mkdir -p scan_results

# Expose ports for development and production
EXPOSE 5000 8000

# Set environment variable for Flask
ENV FLASK_APP=app.py

# Entry point based on environment
CMD if [ "$ENVIRONMENT" = "production" ]; then \
      gunicorn -w 4 -b 0.0.0.0:8000 --timeout 300 app:app; \
    else \
      flask run --host=0.0.0.0 --port=5000; \
    fi
