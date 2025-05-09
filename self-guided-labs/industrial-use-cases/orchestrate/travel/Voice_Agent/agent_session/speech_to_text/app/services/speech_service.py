from ibm_watson import SpeechToTextV1, TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import logging
from typing import BinaryIO, Dict, Any
import subprocess
import io
import os


def convert_to_valid_wav(input_file: BinaryIO) -> BinaryIO:
    output_file = "output.wav"
    command = [
        "ffmpeg", "-i", "pipe:0",
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        output_file
    ]

    try:
        os.remove(output_file)
        process = subprocess.run(
            command,
            input=input_file.read(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        with open(output_file, "rb") as f:
            return io.BytesIO(f.read())
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to convert audio: {str(e)}")


# Configure logger
logger = logging.getLogger(__name__)


class SpeechToTextService:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.authenticator = IAMAuthenticator(config['api_key'])
        self.speech_to_text = SpeechToTextV1(authenticator=self.authenticator)
        self.speech_to_text.set_service_url(config['url'])
        logger.info("Speech to text service initialized")

    async def process_audio(self, audio_file: BinaryIO) -> dict:
        try:
            audio_file = convert_to_valid_wav(audio_file)
            speech_recognition_results = self.speech_to_text.recognize(
                audio=audio_file,
                content_type="audio/l16; rate=16000",
                model="en-US_BroadbandModel",
                smart_formatting=self.config['smart_formatting'],
                word_confidence=self.config['word_confidence'],
                timestamps=self.config['timestamps'],
                profanity_filter=self.config['profanity_filter'],
                speech_detector_sensitivity=self.config['speech_detector_sensitivity'],
                background_audio_suppression=self.config['background_audio_suppression']
            ).get_result()
            logger.info("Successfully processed audio file")
            return speech_recognition_results
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            raise


class TextToSpeechService:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.authenticator = IAMAuthenticator(config['api_key'])
        self.text_to_speech = TextToSpeechV1(authenticator=self.authenticator)
        self.text_to_speech.set_service_url(config['url'])
        logger.info("Text to speech service initialized")

    async def synthesize_speech(self, text: str) -> bytes:
        try:
            result = self.text_to_speech.synthesize(
                text=text,
                voice=self.config['voice'],
                accept=self.config['accept']
            ).get_result().content
            
            logger.info("Successfully synthesized text to speech")
            return result
        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}")
            raise