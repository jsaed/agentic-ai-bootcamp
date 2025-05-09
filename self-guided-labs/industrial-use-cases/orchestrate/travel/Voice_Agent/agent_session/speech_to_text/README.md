# Speech-to-Text Service

A FastAPI-based service that provides speech-to-text and text-to-speech conversion capabilities using IBM Watson services and local Whisper model.

## Features

- Speech-to-Text conversion using IBM Watson
- Text-to-Speech synthesis using IBM Watson
- Local speech recognition using Whisper model
- Audio file format conversion support
- WebSocket support for real-time processing

## Prerequisites

- Python 3.11+
- Docker (optional)
- FFmpeg (required for audio processing)
- IBM Watson API credentials

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
IBM_STT_API_KEY=your_speech_to_text_api_key
IBM_STT_URL=your_speech_to_text_url
IBM_TTS_API_KEY=your_text_to_speech_api_key
IBM_TTS_URL=your_text_to_speech_url
```

## Installation

### Local Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r app/requirements.txt
   ```

3. Copy the template environment file:
   ```bash
   cp template.env .env
   ```

4. Update the `.env` file with your IBM Watson credentials

### Docker Setup

1. Build the Docker image:
   ```bash
   cd app
   docker build -t speech-to-text-service .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 \
     --env-file ../.env \
     speech-to-text-service
   ```

## API Endpoints

### Speech to Text
- **POST** `/transcribe/`
  - Accepts WAV audio files
  - Returns transcribed text
  ```bash
  curl -X POST "http://localhost:8080/transcribe/" \
    -H "accept: application/json" \
    -H "Content-Type: multipart/form-data" \
    -F "audio=@your_audio.wav"
  ```

### Text to Speech
- **POST** `/synthesize/`
  - Accepts JSON with text field
  - Returns audio file
  ```bash
  curl -X POST "http://localhost:8080/synthesize/" \
    -H "Content-Type: application/json" \
    -d '{"text":"Hello, world!"}'
  ```

### Local Speech Processing
- **POST** `/process-audio/`
  - Uses local Whisper model
  - Accepts WAV audio files
  ```bash
  curl -X POST "http://localhost:8080/process-audio/" \
    -H "accept: application/json" \
    -H "Content-Type: multipart/form-data" \
    -F "file=@your_audio.wav"
  ```

## Configuration

The service configuration is managed through `config/config.yml`. Key configurations include:

- Speech-to-text parameters
- Text-to-speech voice settings
- Logging configurations
- Application settings

## Logging

Logs are stored in the `logs/` directory. The default log file is `app.log`.

## Development

1. Make sure to update `template.env` if you add new environment variables
2. Run tests before submitting changes
3. Follow the existing code style and documentation patterns

## Troubleshooting

1. If you encounter audio processing issues, ensure FFmpeg is properly installed
2. For IBM Watson errors, verify your credentials and network connectivity
3. Check the logs in `logs/app.log` for detailed error messages
