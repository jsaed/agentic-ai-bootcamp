# Agent Session Service

## Overview

In this lab, we are going to develop a conversational Taxi booking application designed to make the booking experience exceptionally smooth and user-friendly. This application leverages agents with Watsonx orchestrate & IBM STT/TTS to provide a seamless and efficient taxi booking process.

Below are the key highlights that will be covered in this lab

1. **Voice Command Interaction:**

    Empowering users to interact with the application using intuitive voice commands.

2. **Agent-Controlled Booking Experience:**

    a) Streamlining the entire booking process with intelligent agents.

    b) Ensuring a hassle-free experience by automating complex tasks.

3. **Agent Capabilities:**

    a) **Google Maps Integration:** Simulating internet connectivity to provide accurate location services.

    b) **API Calls:** Connecting to external data sources to fetch real-time User Information.

    c) **Structured Date & Time Inference:** Simulating custom functionalities by managing date and time effectively.

4. **Third-Party Booking Service Interaction:**

    a) Facilitating seamless interaction with third-party booking services like Uber (simulated).

    b) Expanding user options and enhancing the overall booking experience.

## Features

- Session management for conversational agents
- Integration with WatsonX
- Stateful conversation handling
- Action-based conversation processing
- Configurable prompts and behaviors

## Prerequisites

- Python 3.11+
- Docker (optional)
- WatsonX API credentials

## Project Structure

```
agent_session/
├── main.py              # Main FastAPI application and endpoints
├── llm.py              # WatsonX integration
├── session_manager.py   # Session management logic
├── prompts.py          # System prompts and templates
├── utils.py            # Utility functions and action handlers
└── requirements.txt    # Project dependencies
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
WX_API_KEY=your_watsonx_api_key
WX_URL=your_watsonx_url
WX_PROJECT_ID=your_watsonx_project_id
```

## Installation

### Local Setup

1. Create and activate a virtual environment:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create and configure your `.env` file with required credentials

### Docker Setup

### Using Docker

1. Pull the pre-built Docker image:

    ```bash
    docker pull deepak33994/voice-agent-session
    ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 \
     --env-file .env \
     agent-session-service
   ```

3. Access the application at [http://127.0.0.1:8000](http://127.0.0.1:8000).

**Note:** For Taxi api backend repo click here [taxi-backend-service](https://github.ibm.com/emea-ce-watson-core/wx-ag-bootcamp/tree/main/industrial-use-cases/orchestrate/travel/taxi-backend-service)

### IBM Code Engine (Deployed Container)

You can immediately test the already-deployed instance:

**URL**: [https://application-e0.1tgya61cxec2.us-south.codeengine.appdomain.cloud](https://application-e0.1tgya61cxec2.us-south.codeengine.appdomain.cloud)


## API Endpoints

### Chat Endpoint
- **POST** `/chat`
  - Processes a chat message and manages the conversation
  ```bash
  curl -X POST "http://localhost:8000/chat" \
    -H "Content-Type: application/json" \
    -d '{
      "session_id": "optional_session_id",
      "user_id": "user123",
      "query": "Hello, how can you help me?"
    }'
  ```
  - Response format:
    ```json
    {
      "session_id": "session_id",
      "query": "",
      "final_response": {},
      "status_code": "200"
    }
    ```

### **2. Transcribe Audio**

**Endpoint:** `POST /transcribe/`

**Request:** Upload a `.wav` file  

**Response:**
```json
{
  "text": "Hello, how are you?"
}
```

### **3. Process Audio**

**Endpoint:** `POST /process-audio/`

**Request:** Upload a `.wav` file  

**Response:**
```json
{
  "status": "success",
  "text": "Transcribed text here",
  "message": "Audio processed successfully"
}
```

### **4. Synthesize Speech**

**Endpoint:** `POST /synthesize/`

**Request:**
```json
{
  "text": "Hello, how are you?"
}
```

**Response:** Returns an audio file (`.webm` format).

### **5. Health Check**

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy"
}
```

### Session Management
- **DELETE** `/session/{session_id}`
  - Ends a specific session
  ```bash
  curl -X DELETE "http://localhost:8000/session/your_session_id"
  ```

### Health Check
- **GET** `/health`
  - Checks the service health
  ```bash
  curl "http://localhost:8000/health"
  ```

## Configuration

### LLM Configuration (`llm.py`)
- WatsonX model configuration
- API call handling
- Response processing

### Session Management (`session_manager.py`)
- Session creation and management
- Conversation history tracking
- Memory handling

### Prompts (`prompts.py`)
- System prompts for agent behavior
- Conversation context templates
- Response formatting

## Development

1. Follow the existing code structure and patterns
2. Update requirements.txt when adding new dependencies
3. Document any new endpoints or features
4. Test thoroughly before submitting changes

## Error Handling

The service includes robust error handling for:
- Invalid session IDs
- WatsonX API failures
- Malformed requests
- Session timeouts

## Logging

- Application logs are stored in `app.log`
- Console and file logging enabled
- Error tracking and debugging information
- API interaction logs

## Best Practices

1. Keep sessions short-lived and clean up unused sessions
2. Monitor WatsonX API usage and costs
3. Handle rate limiting appropriately
4. Implement proper error handling and recovery
5. Follow security best practices for API keys and sensitive data

## Troubleshooting

1. Check environment variables are properly set
2. Verify WatsonX API credentials and connectivity
3. Monitor app.log for errors
4. Ensure proper session management and cleanup

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contributing

Contributions to improve the tool are welcome. Please fork the repository and submit a pull request with your enhancements.

We welcome all contributions!

## Contact

 Deepak Nayak - Deepak.Nayak2@ibm.com

 Akash Modi - akash.modi@ibm.com

 In case you encounter issues with the LABs please write them [here](https://github.ibm.com/emea-ce-watson-core/wx-ag-bootcamp/issues), we are happy to help.
