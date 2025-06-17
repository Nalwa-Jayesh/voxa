"""Text-to-speech management for voice output."""

import pyttsx3
import threading
from voice_assistant.utils.logging_config import logger

class TTSManager:
    """Text-to-speech manager using pyttsx3."""
    
    def __init__(self):
        """Initialize the TTS engine."""
        self.engine = None
        self._lock = threading.Lock()
        self._setup_tts()
    
    def _setup_tts(self):
        """Configure text-to-speech settings."""
        try:
            with self._lock:
                if self.engine is None:
                    self.engine = pyttsx3.init()
                    voices = self.engine.getProperty('voices')
                    if voices:
                        # Prefer female voice
                        for voice in voices:
                            if any(term in voice.name.lower() for term in ['female', 'zira', 'hazel']):
                                self.engine.setProperty('voice', voice.id)
                                break
                    
                    self.engine.setProperty('rate', 175)  # Speaking rate
                    self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
        except Exception as e:
            logger.error(f"TTS setup error: {e}")
    
    def speak(self, text: str):
        """Convert text to speech."""
        try:
            logger.info(f"Assistant: {text}")
            with self._lock:
                # Ensure engine is initialized
                if self.engine is None:
                    self._setup_tts()
                
                # Stop any existing loop before starting a new one
                try:
                    self.engine.stop()
                except:
                    pass
                
                self.engine.say(text)
                self.engine.runAndWait()
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            # Try to recover by reinitializing the engine
            try:
                with self._lock:
                    self.engine = None  # Force reinitialization
                    self._setup_tts()
                    self.engine.say(text)
                    self.engine.runAndWait()
            except Exception as e2:
                logger.error(f"TTS recovery error: {e2}")
    
    def cleanup(self):
        """Cleanup TTS resources."""
        try:
            with self._lock:
                if self.engine is not None:
                    self.engine.stop()
                    self.engine = None
        except Exception as e:
            logger.error(f"TTS cleanup error: {e}") 