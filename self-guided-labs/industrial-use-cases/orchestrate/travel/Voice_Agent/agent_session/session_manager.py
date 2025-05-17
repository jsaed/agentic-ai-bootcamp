from typing import Dict, Optional
import uuid
import logging
import re
from llm import init_watsonx_llm
from prompts import system_prompt
from utils import search_places, get_booking_date

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)


class Agent:
    def __init__(self, llm, system: str = "") -> None:
        self.llm = llm
        self.system = system
        self.messages: list = []
        if self.system:
            self.messages.append({"role": "system", "content": system})
        logging.info("Agent initialized with system prompt.")

    def __call__(self, message=""):
        try:
            if message:
                self.messages.append({"role": "user", "content": message})
                logging.info(f"User message added: {message}")
            result = self.execute()
            self.messages.append({"role": "assistant", "content": result})
            logging.info(f"Assistant response added: {result}")
            return result
        except Exception as e:
            logging.error(f"Error during agent call: {e}")
            raise

    def execute(self):
        try:
            # Format messages into a single string
            formatted_prompt = self.format_messages()
            logging.debug(f"Formatted prompt: {formatted_prompt}")
            completion = self.llm.generate_text(formatted_prompt)
            return completion
        except Exception as e:
            logging.error(f"Error during execution: {e}")
            raise

    def format_messages(self) -> str:
        formatted_text = ""
        for msg in self.messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                formatted_text += f"System: {content}\n\n"
            elif role == "user":
                formatted_text += f"Human: {content}\n\n"
            elif role == "assistant":
                formatted_text += f"Assistant: {content}\n\n"

        # Add the role prefix for the expected assistant response
        formatted_text += "Assistant: "
        return formatted_text


class SessionManager:
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance.sessions = {}
            cls._instance.watsonx_llm = init_watsonx_llm()
            logging.info("SessionManager instance created.")
        return cls._instance

    def get_or_create_session(self, session_id: Optional[str] = None, system_prompt="") -> tuple[str, Agent]:
        try:
            if session_id and session_id in self.sessions:
                logging.info(f"Returning existing session: {session_id}")
                return session_id, self.sessions[session_id]

            new_session_id = session_id or str(uuid.uuid4())
            self.sessions[new_session_id] = Agent(llm=self.watsonx_llm, system=system_prompt)
            logging.info(f"Created new session: {new_session_id}")
            return new_session_id, self.sessions[new_session_id]
        except Exception as e:
            logging.error(f"Error in get_or_create_session: {e}")
            raise

    def end_session(self, session_id: str) -> bool:
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logging.info(f"Ended session: {session_id}")
                return True
            logging.warning(f"Session not found: {session_id}")
            return False
        except Exception as e:
            logging.error(f"Error ending session: {e}")
            raise
