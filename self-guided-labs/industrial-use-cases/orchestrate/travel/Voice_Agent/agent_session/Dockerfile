# Use an official Python runtime as the base image
FROM python:3.11-slim

# Install system dependencies including wget, build-essential, and ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the required packages from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application code to the container
COPY . .

# Expose the port on which the FastAPI application will run
EXPOSE 8000

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
