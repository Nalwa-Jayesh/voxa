"""Main entry point for the voice assistant."""

import os
import sys
from dotenv import load_dotenv
from voice_assistant.core.assistant import VoiceAssistant
from voice_assistant.utils.logging_config import logger

def main():
    """Main entry point."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API keys from environment
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
    
    if not gemini_api_key:
        print("Please set GEMINI_API_KEY in your .env file")
        sys.exit(1)
    
    if not openweather_api_key:
        print("Please set OPENWEATHER_API_KEY in your .env file")
        sys.exit(1)
    
    try:
        # Create and run assistant
        assistant = VoiceAssistant(gemini_api_key, openweather_api_key)
        assistant.run()
    except KeyboardInterrupt:
        logger.info("Assistant stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 