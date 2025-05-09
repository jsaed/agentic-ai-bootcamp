import logging
import json
import uuid
import time
import os
from typing import Optional, Dict, Any, List, AsyncGenerator
from fastapi import FastAPI, Header, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from ag11_json import analyze_shelf

# Load environment variables
load_dotenv()

# Fetch Watsonx credentials
WATSONX_URL = os.getenv("WATSONX_URL")
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = FastAPI()

# Define model classes to match app(1)
class Message(BaseModel):
    role: str
    content: str

class MessageResponse(BaseModel):
    role: str
    content: str

class Choice(BaseModel):
    index: int
    message: MessageResponse
    finish_reason: str

class ExtraBody(BaseModel):
    thread_id: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "watsonx"
    messages: List[Message]
    stream: Optional[bool] = False
    extra_body: Optional[ExtraBody] = None

    def json(self):
        return self.dict()

class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]

# Define default model
DEFAULT_MODEL = "watsonx"

async def stream_analyze_shelf(user_prompt: str, model: str) -> AsyncGenerator[str, None]:
    """
    Stream the response from analyze_shelf to mimic the streaming behavior in app(1)
    """
    # Get full response from analyze_shelf
    full_response = analyze_shelf(user_prompt)
    
    # Parse the JSON string back to a dictionary
    try:
        response_dict = json.loads(full_response)
    except json.JSONDecodeError:
        response_dict = {"error": "Failed to parse response as JSON"}
    
    # Create a streaming response structure
    id = str(uuid.uuid4())
    created = int(time.time())
    
    # Stream the market trends part
    if "market_trends" in response_dict and response_dict["market_trends"]:
        market_content = response_dict["market_trends"]
        chunk = {
            "id": id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"role": "assistant", "content": "Market Trends:\n\n" + market_content},
                    "finish_reason": None
                }
            ]
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.1)
    
    # Stream the recommendations part
    if "recommendations" in response_dict and response_dict["recommendations"]:
        recommendations_content = response_dict["recommendations"]
        chunk = {
            "id": id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": "\n\nRecommendations:\n\n" + recommendations_content},
                    "finish_reason": None
                }
            ]
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        await asyncio.sleep(0.1)
    
    # Stream the action plan part
    if "action_plan" in response_dict and response_dict["action_plan"]:
        action_plan_content = response_dict["action_plan"]
        chunk = {
            "id": id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": "\n\nAction Plan:\n\n" + action_plan_content},
                    "finish_reason": None
                }
            ]
        }
        yield f"data: {json.dumps(chunk)}\n\n"
    
    # Send the final [DONE] marker
    yield "data: [DONE]\n\n"

@app.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    X_IBM_THREAD_ID: Optional[str] = Header(None, alias="X-IBM-THREAD-ID", description="Optional header to specify the thread ID"),
):
    logger.info(f"Received POST /chat/completions ChatCompletionRequest: {request.json()}")
    
    # Handle thread_id in the same way as app(1)
    thread_id = ''
    if X_IBM_THREAD_ID:
        thread_id = X_IBM_THREAD_ID
    if request.extra_body and request.extra_body.thread_id:
        thread_id = request.extra_body.thread_id
    logger.info("thread_id: " + thread_id)
    
    # Use the model from the request or default
    model = DEFAULT_MODEL
    if request.model:
        model = request.model
    
    # Extract the user message content from the messages list
    user_prompt = ""
    for message in request.messages:
        if message.role == "user":
            user_prompt = message.content
            break
    
    # Handle streaming vs. non-streaming responses like in app(1)
    if request.stream:
        # Need to import asyncio for streaming
        import asyncio
        return StreamingResponse(stream_analyze_shelf(user_prompt, model), media_type="text/event-stream")
    else:
        # Get response from analyze_shelf
        response_json = analyze_shelf(user_prompt)
        
        # Parse the JSON response to extract all information
        try:
            response_dict = json.loads(response_json)
            
            # Combine all parts into a single response
            combined_response = ""
            if "market_trends" in response_dict and response_dict["market_trends"]:
                combined_response += f"Market Trends:\n\n{response_dict['market_trends']}\n\n"
            if "recommendations" in response_dict and response_dict["recommendations"]:
                combined_response += f"Recommendations:\n\n{response_dict['recommendations']}\n\n"
            if "action_plan" in response_dict and response_dict["action_plan"]:
                combined_response += f"Action Plan:\n\n{response_dict['action_plan']}"
                
            if not combined_response and "error" in response_dict:
                combined_response = f"Error: {response_dict['error']}"
                
        except json.JSONDecodeError:
            combined_response = "Failed to parse response as JSON: " + response_json
        
        # Create response in the same format as app(1)
        id = str(uuid.uuid4())
        response = ChatCompletionResponse(
            id=id,
            object="chat.completion",
            created=int(time.time()),
            model=model,
            choices=[
                Choice(
                    index=0,
                    message=MessageResponse(
                        role="assistant",
                        content=combined_response
                    ),
                    finish_reason="stop"
                )
            ]
        )
        
        return JSONResponse(content=response.dict())

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)