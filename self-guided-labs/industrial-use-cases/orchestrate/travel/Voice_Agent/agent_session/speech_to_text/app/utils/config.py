import os
from pathlib import Path
from typing import Dict, Any
import yaml
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Load config file
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yml"
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        # Validate required environment variables
        self._validate_env_vars()

    def _validate_env_vars(self):
        required_vars = [
            'IBM_STT_API_KEY', 'IBM_STT_URL',
            'IBM_TTS_API_KEY', 'IBM_TTS_URL'
        ]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    @property
    def speech_to_text_config(self) -> Dict[str, Any]:
        return {
            'api_key': os.getenv('IBM_STT_API_KEY'),
            'url': os.getenv('IBM_STT_URL'),
            **self.config['speech_to_text']
        }

    @property
    def text_to_speech_config(self) -> Dict[str, Any]:
        return {
            'api_key': os.getenv('IBM_TTS_API_KEY'),
            'url': os.getenv('IBM_TTS_URL'),
            **self.config['text_to_speech']
        }
    
    @property
    def app_config(self) -> Dict[str, Any]:
        return self.config['app']