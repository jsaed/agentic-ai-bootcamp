# Use an official Python runtime as a parent image
FROM python:3.9-slim

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

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Run uvicorn server on container start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

