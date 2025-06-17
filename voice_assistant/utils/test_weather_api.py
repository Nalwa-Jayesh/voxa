"""Test script for OpenWeather API key verification."""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from voice_assistant.utils.logging_config import logger

async def test_weather_api():
    """Test the OpenWeather API key with a sample city."""
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        print("Error: OPENWEATHER_API_KEY not found in .env file")
        return
    
    # Test city
    test_city = "Delhi"
    
    try:
        async with aiohttp.ClientSession() as session:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": test_city,
                "appid": api_key,
                "units": "metric"
            }
            
            print(f"\nTesting OpenWeather API with city: {test_city}")
            print("Making API request...")
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    temp = data["main"]["temp"]
                    description = data["weather"][0]["description"]
                    humidity = data["main"]["humidity"]
                    
                    print("\n✅ API Key is working correctly!")
                    print(f"\nWeather data for {test_city}:")
                    print(f"Temperature: {temp}°C")
                    print(f"Description: {description}")
                    print(f"Humidity: {humidity}%")
                else:
                    error_data = await response.json()
                    print("\n❌ API Key test failed!")
                    print(f"Status code: {response.status}")
                    print(f"Error message: {error_data.get('message', 'Unknown error')}")
                    
    except Exception as e:
        print("\n❌ Error occurred while testing API key:")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Starting OpenWeather API key test...")
    asyncio.run(test_weather_api()) 