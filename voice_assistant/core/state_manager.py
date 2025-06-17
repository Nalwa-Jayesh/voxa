"""State management for the voice assistant."""

import pickle
from datetime import datetime
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..utils.logging_config import logger

@dataclass
class ConversationMessage:
    """Represents a message in the conversation history."""
    role: str  # "user" or "model"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class StateManager:
    """Persistent state management for the assistant."""
    
    def __init__(self, state_file: str = "assistant_state.pkl"):
        """Initialize the state manager."""
        self.state_file = Path(state_file)
        self.state = {
            'conversation_history': [],
            'tasks': {},
            'user_preferences': {},
            'session_count': 0,
            'last_active': None
        }
        self.load_state()
    
    def load_state(self):
        """Load state from file."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'rb') as f:
                    loaded_state = pickle.load(f)
                    self.state.update(loaded_state)
                    logger.info(f"State loaded from {self.state_file}")
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
    
    def save_state(self):
        """Save state to file."""
        try:
            self.state['last_active'] = datetime.now()
            with open(self.state_file, 'wb') as f:
                pickle.dump(self.state, f)
            logger.debug("State saved successfully")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def get(self, key: str, default=None):
        """Get state value."""
        return self.state.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set state value."""
        self.state[key] = value
        self.save_state()
    
    def update_conversation(self, message: ConversationMessage):
        """Update conversation history."""
        if 'conversation_history' not in self.state:
            self.state['conversation_history'] = []
        
        self.state['conversation_history'].append(asdict(message))
        
        # Keep only last 50 messages
        if len(self.state['conversation_history']) > 50:
            self.state['conversation_history'] = self.state['conversation_history'][-50:]
        
        self.save_state() 