"""Google Gemini API client for natural language processing."""

import time
import aiohttp
import asyncio
from google import genai
from voice_assistant.utils.logging_config import logger
from voice_assistant.utils.constants import SYSTEM_PROMPT, MAX_RETRIES, ERROR_RETRY_DELAY

class GeminiClient:
    """Enhanced Google Gemini API client with error recovery."""
    
    def __init__(self, api_key: str):
        """Initialize the Gemini client."""
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
        self.weather_api_key = None  # Will be set from environment
        
        # Initialize model with safety settings
        self.model = 'gemini-2.0-flash'
        
        # Configure safety settings
        safety_settings = {
            genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Start chat session
        self.chat = self.client.chats.create(
            model=self.model
        )
    
    async def get_weather(self, city: str) -> str:
        """Get weather information for a city."""
        if not self.weather_api_key:
            return "Weather API key not configured. Please set OPENWEATHER_API_KEY in your environment."
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://api.openweathermap.org/data/2.5/weather"
                params = {
                    "q": city,
                    "appid": self.weather_api_key,
                    "units": "metric"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        temp = data["main"]["temp"]
                        description = data["weather"][0]["description"]
                        humidity = data["main"]["humidity"]
                        return f"The current weather in {city} is {description} with a temperature of {temp}°C and humidity of {humidity}%."
                    else:
                        return f"Sorry, I couldn't get the weather for {city} right now."
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return f"Sorry, I had trouble getting the weather for {city}."
    
    async def generate_response(self, message: str, context: str = None) -> str:
        """Generate response with error handling and retry logic."""
        max_retries = MAX_RETRIES
        retry_delay = ERROR_RETRY_DELAY
        
        # Check for weather/temperature query
        message_lower = message.lower()
        weather_keywords = ['weather', 'temperature', 'temp', 'how hot', 'how cold']
        if any(keyword in message_lower for keyword in weather_keywords):
            # Extract city name (improved implementation)
            words = message_lower.split()
            try:
                # Look for "in" followed by city name
                if "in" in words:
                    city_index = words.index("in") + 1
                    if city_index < len(words):
                        city = words[city_index].capitalize()
                        return await self.get_weather(city)
            except ValueError:
                pass
        
        full_message = f"{context}\n\nUser: {message}" if context else message
        
        for attempt in range(max_retries):
            try:
                # Send message and get response
                response = self.chat.send_message(full_message)
                return response.text
                
            except Exception as e:
                logger.error(f"Gemini API error (attempt {attempt + 1}): {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    # Reset chat session on error
                    self.chat = self.client.chats.create(
                        model=self.model,
                        safety_settings=self.chat.safety_settings
                    )
                    continue
                else:
                    return self._get_fallback_response(message)
    
    def _get_fallback_response(self, message: str) -> str:
        """Provide fallback response when API fails."""
        fallback_responses = [
            "I'm having trouble connecting to my AI service right now. Could you please try again?",
            "I'm experiencing some technical difficulties. Let me try to help you in a moment.",
            "Sorry, I'm having connection issues. Please repeat your request."
        ]
        return fallback_responses[hash(message) % len(fallback_responses)] 