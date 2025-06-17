# LLM Voice Agent 🎙️

An advanced voice-controlled assistant using Google's Gemini API. This project provides a robust voice interface with features like natural language processing, task management, and voice interaction.

## Features ✨

- Voice command recognition and processing
- Natural language understanding using Google Gemini API
- Task management (timers, reminders, notes)
- Text-to-speech capabilities
- Persistent state management
- Robust error handling and recovery
- Voice activity detection
- Weather information lookup

## Requirements 📋

- Python 3.8+
- Google Gemini API key
- OpenWeather API key (for weather queries)
- PyAudio
- SpeechRecognition
- pyttsx3
- webrtcvad (for voice activity detection)
- Windows-specific dependencies (pywin32, comtypes)

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/Nalwa-Jayesh/voxa.git
cd voxa
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Set up your environment variables:
```bash
# On Windows PowerShell:
$env:GEMINI_API_KEY='your-api-key-here'
$env:OPENWEATHER_API_KEY='your-api-key-here'

# On Windows Command Prompt:
set GEMINI_API_KEY=your-api-key-here
set OPENWEATHER_API_KEY=your-api-key-here
```

## Usage 💡

Run the assistant using the installed command:
```bash
voice-assistant
```

Or run directly:
```bash
python -m voice_assistant.main
```

### Voice Commands 🗣️

The assistant responds to various voice commands organized by category:

#### Wake Words ⏰
- "assistant"
- "hey assistant"
- "ok assistant"

#### Timer & Reminder Commands ⏱️
- "set a timer for [X] minutes"
- "set a timer for [X] hours and [Y] minutes"
- "remind me to [task] at [time]"
- "remind me to [task] in [X] minutes"
- "remind me to [task] tomorrow at [time]"
- "cancel my [timer/reminder]"
- "list my timers"
- "list my reminders"

#### Note-Taking Commands 📝
- "note down [content]"
- "take a note: [content]"
- "add to my notes: [content]"
- "read my notes"
- "clear my notes"

#### Task Management ✅
- "add task: [task description]"
- "list my tasks"
- "mark task [X] as complete"
- "delete task [X]"
- "what's my next task?"

#### Weather Information 🌤️
- "what's the weather in [city]"
- "weather forecast for [city]"
- "is it going to rain in [city] today?"
- "what's the temperature in [city]"

#### System Commands ⚙️
- "goodbye" / "bye" / "stop" / "exit" (to exit the assistant)
- "help" (to list available commands)
- "what can you do?" (to hear capabilities)

Note: The assistant uses natural language processing, so you can phrase these commands in different ways. For example, instead of "set a timer for 5 minutes", you could say "remind me in 5 minutes" or "timer 5 minutes".

## Project Structure 📁

```
voxa/
├── voice_assistant/           # Main package directory
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Main entry point and CLI interface
│   ├── alarm.wav             # Default alarm sound file
│   ├── audio/                # Audio processing components
│   │   ├── speech.py         # Speech recognition and processing
│   │   ├── tts.py            # Text-to-speech implementation
│   │   └── vad.py            # Voice activity detection
│   ├── core/                 # Core assistant functionality
│   │   ├── assistant.py      # Main assistant class
│   │   ├── state.py          # State management
│   │   └── tasks.py          # Task management system
│   ├── llm/                  # LLM integration
│   │   ├── gemini.py         # Google Gemini API client
│   │   └── prompts.py        # LLM prompt templates
│   └── utils/                # Utility functions
│       ├── config.py         # Configuration management
│       └── helpers.py        # Helper functions
├── assistant_state.pkl       # Persistent state storage (tasks, conversation history)
├── requirements.txt         # Project dependencies
├── setup.py                 # Package configuration
└── README.md                # Project documentation
```

Each component serves a specific purpose:

- **audio/**: Handles all audio-related functionality including speech recognition, text-to-speech conversion, and voice activity detection
- **core/**: Contains the main assistant logic, state management, and task handling systems
- **llm/**: Manages interactions with Google's Gemini API and prompt engineering
- **utils/**: Provides helper functions and configuration management
- **data/**: Directory for additional data storage
- **assistant_state.pkl**: Stores persistent state including tasks, conversation history, and user preferences
- **main.py**: Entry point that ties all components together and provides the CLI interface

## Development 👨‍💻

The project is set up as a Python package with the following key components:

- `setup.py`: Package configuration and entry points
- `requirements.txt`: Project dependencies
- `voice_assistant/`: Main package directory
  - `main.py`: Entry point for the voice assistant
  - `core/`: Core functionality implementation
  - `llm/`: Google Gemini API integration
  - `audio/`: Audio processing and TTS
  - `utils/`: Helper functions and utilities

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.
