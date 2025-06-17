"""Constants used throughout the voice assistant."""

from enum import Enum

class AssistantState(Enum):
    """States that the assistant can be in."""
    IDLE = "idle"
    LISTENING = "listening" 
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"

class TaskType(Enum):
    """Types of tasks that can be created."""
    TIMER = "timer"
    REMINDER = "reminder"
    NOTE = "note"
    CALENDAR = "calendar"
    LOOKUP = "lookup"
    WEATHER = "weather"
    GENERAL = "general"

# Audio configuration
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_CHUNK_SIZE = 1024
DEFAULT_CHANNELS = 1
DEFAULT_SILENCE_THRESHOLD = 1000
DEFAULT_SILENCE_DURATION = 1.5
DEFAULT_MAX_RECORDING_TIME = 10.0

# Wake words
WAKE_WORDS = ["assistant", "hey assistant", "ok assistant"]

# System prompt for Gemini
SYSTEM_PROMPT = """You are a helpful voice assistant with the following capabilities:
- Natural conversation and Q&A
- Setting timers and reminders
- Taking notes and managing tasks
- Looking up information
- Managing calendar events

Be conversational, concise, and helpful. When users ask for tasks:
- For timers: Extract duration and confirm
- For reminders: Extract time/date and content
- For notes: Acknowledge and confirm saving
- Always ask for clarification if something is unclear

Respond in a natural, friendly manner as if speaking aloud. Keep responses concise but informative."""

# Error handling
MAX_ERRORS = 5
ERROR_RETRY_DELAY = 1
MAX_RETRIES = 3 