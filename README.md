# LLM Voice Agent

An advanced voice-controlled assistant using Google's Gemini API. This project provides a robust voice interface with features like natural language processing, task management, and voice interaction.

## Features

- Voice command recognition and processing
- Natural language understanding using Google Gemini API
- Task management (timers, reminders, notes)
- Text-to-speech capabilities
- Persistent state management
- Robust error handling and recovery
- Voice activity detection
- Weather information lookup

## Requirements

- Python 3.8+
- Google Gemini API key
- OpenWeather API key (for weather queries)
- PyAudio
- SpeechRecognition
- pyttsx3
- webrtcvad (optional, for better voice detection)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llm-voice-agent.git
cd llm-voice-agent
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
export GEMINI_API_KEY='your-api-key-here'  # On Windows: set GEMINI_API_KEY=your-api-key-here
export OPENWEATHER_API_KEY='your-api-key-here'  # On Windows: set OPENWEATHER_API_KEY=your-api-key-here
```

## Usage

Run the assistant:
```bash
python -m voice_assistant.main
```

### Voice Commands

- Wake words: "assistant", "hey assistant", "ok assistant"
- Timer commands: "set a timer for X minutes"
- Reminder commands: "remind me to X at Y time"
- Note commands: "note down X"
- Task management: "list my tasks"
- Weather queries: "what's the weather in [city]"
- Exit: "goodbye", "bye", "stop", "exit"

## Project Structure

```
llm-voice-agent/
├── voice_assistant/
│   ├── audio/         # Audio processing and TTS
│   ├── core/          # Core assistant functionality
│   ├── llm/           # LLM integration
│   └── utils/         # Utilities and helpers
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
