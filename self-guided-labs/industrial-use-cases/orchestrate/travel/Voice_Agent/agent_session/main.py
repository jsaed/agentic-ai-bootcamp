from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, BinaryIO
import uvicorn
import re
import json
import logging
import io
import wave
import os
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import tempfile

# Import session management and services
from session_manager import SessionManager
from prompts import system_prompt
from utils import search_places, get_booking_date, get_user_address
from speech_to_text.app.services.speech_service import SpeechToTextService, TextToSpeechService
from speech_to_text.app.utils.logger import setup_logger
from speech_to_text.app.utils.config import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)

# Initialize FastAPI app
app = FastAPI(
    title="Voice Agent API",
    description="Combined API for Agent Session and Speech Services",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
config_manager = ConfigManager()
logger = setup_logger(
    config_manager.app_config['name'],
    config_manager.app_config['log_file']
)
session_manager = SessionManager()
stt_service = SpeechToTextService(config_manager.speech_to_text_config)
tts_service = TextToSpeechService(config_manager.text_to_speech_config)

# Initialize Whisper model
device = "cpu"
torch_dtype = torch.float32
model_id = "openai/whisper-small.en"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    batch_size=16,
    return_timestamps=False,
    torch_dtype=torch_dtype,
    device=device,
)

# Request/Response Models
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    query: str

class ChatResponse(BaseModel):
    session_id: str
    query: Optional[str]
    error: Optional[str] = None
    final_response: dict
    status_code: str

class TextToSpeechRequest(BaseModel):
    text: str

# Helper Functions
def validate_wav(file: BinaryIO):
    try:
        with wave.open(file, 'rb') as wav_file:
            wav_file.getparams()
    except wave.Error as e:
        raise ValueError(f"Invalid WAV file: {str(e)}")

def extract_action_input(text):
    action_input_pattern = r'Action Input:\s*(?:"([^"]+)"|\(([^)]+)\))'
    match = re.search(action_input_pattern, text)
    if match:
        return match.group(1) if match.group(1) else f"({match.group(2)})"
    return None

# Agent Session Endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        result, session_id = loop(
            session_id=request.session_id,
            query=request.query,
            user_id=request.user_id
        )
        try:
            return ChatResponse(
                status_code="200",
                session_id=session_id,
                query="",
                final_response=json.loads(result)
            )
        except:
            return ChatResponse(
                status_code="201",
                session_id=session_id,
                query=result,
                final_response={},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/session/{session_id}")
async def end_session(session_id: str):
    success = session_manager.end_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return {"message": f"Session {session_id} ended successfully"}

# Speech Service Endpoints
@app.post("/transcribe/")
async def transcribe_audio(audio: UploadFile = File(...)):
    if not audio.filename.endswith('.wav'):
        raise HTTPException(400, "Only WAV files are supported")
    
    try:
        contents = await audio.read()
        audio_bytes = io.BytesIO(contents)
        logger.info("Starting audio transcription")
        result = await stt_service.process_audio(audio_bytes)
        logger.info("Transcription complete")
        return {'text': result["results"][0]["alternatives"][0]["transcript"]}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(500, "Internal server error")

@app.post("/process-audio/")
async def process_audio(file: UploadFile = File(...)):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            try:
                content = await file.read()
                if not content:
                    raise HTTPException(status_code=400, detail="Empty file provided")
                
                temp_file.write(content)
                temp_file_path = temp_file.name
                
                try:
                    result = pipe(temp_file_path)
                    if not result or 'text' not in result:
                        raise HTTPException(status_code=500, detail="Processing failed to return valid result")
                    
                    return {
                        "status": "success",
                        "text": result['text'],
                        "message": "Audio processed successfully"
                    }
                except Exception as e:
                    logger.error(f"Error processing audio: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
            finally:
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.error(f"Error deleting temporary file: {str(e)}")
    except Exception as e:
        logger.error(f"Error in process_audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize/")
async def synthesize_text(request: TextToSpeechRequest):
    try:
        audio_content = await tts_service.synthesize_speech(request.text)
        return StreamingResponse(
            io.BytesIO(audio_content),
            media_type="audio/webm",
            headers={
                "Content-Disposition": "attachment; filename=synthesized_speech.webm"
            }
        )
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(500, "Error synthesizing speech")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def loop(session_id: Optional[str] = None, max_iterations=10, query: str = "", user_id: Optional[str] = None):
    try:
        session_id, agent = session_manager.get_or_create_session(
            session_id=session_id,
            system_prompt=system_prompt
        )

        action_functions = {
            "search_places": search_places,
            "get_booking_date": get_booking_date,
            "get_user_address": get_user_address
        }

        action_pattern = r"Action:\s*(.+)"
        next_prompt = query + f'and my user id is {user_id}' if len(agent.messages) <= 1 else query
        i = 0

        while i < max_iterations:
            i += 1
            try:
                result = agent(next_prompt)
                logging.info(f"Iteration {i}, Session {session_id}: {result}")

                if "PAUSE" in result and "Action" in result and "Input" in result:
                    action_match = re.search(action_pattern, result)
                    action = action_match.group(1) if action_match else None
                    action_input = extract_action_input(result)
                    
                    if action in action_functions:
                        try:
                            if isinstance(action_input, str) and action_input.startswith("(") and action_input.endswith(")"):
                                parsed_input = eval(action_input)
                                if isinstance(parsed_input, tuple):
                                    tool_result = action_functions[action](*parsed_input)
                                else:
                                    raise ValueError("Parsed action_input is not a tuple.")
                            else:
                                tool_result = action_functions[action](action_input)
                            
                            logging.info(f"Tool executed: {action} with input: {action_input}. Result: {tool_result}")
                            next_prompt = f"Observation: {tool_result}"
                            print(next_prompt)

                        except Exception as e:
                            logging.error(f"Error executing tool {action}: {e}")
                            next_prompt = "Observation: Error executing the requested action."
                            print(next_prompt)
                    else:
                        logging.warning(f"Unknown action: {action}")
                        return action_input, session_id
                    continue

                if "Answer" in result:
                    final_json_match = re.search(r'```json(.*?)```', result, re.DOTALL)
                    if final_json_match:
                        final_json = final_json_match.group(1)
                        logging.info(f"Final JSON extracted: {final_json}")
                        return final_json, session_id
                    else:
                        logging.warning("Could not extract final JSON from result.")
                        return None, session_id
            except Exception as e:
                logging.error(f"Error during loop iteration {i}: {e}")
                break

        logging.warning(f"Max iterations reached for session {session_id}.")
        return None, session_id

    except Exception as e:
        logging.error(f"Error in loop function: {e}")
        raise

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1
    )