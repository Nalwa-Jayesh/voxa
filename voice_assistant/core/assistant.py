"""Main voice assistant implementation."""

import os
import re
import time
import wave
import asyncio
import speech_recognition as sr
from datetime import datetime, timedelta

from voice_assistant.utils.logging_config import logger
from voice_assistant.utils.constants import (
    AssistantState,
    TaskType,
    WAKE_WORDS,
    SYSTEM_PROMPT,
    MAX_ERRORS
)
from voice_assistant.audio.stream_manager import AudioStreamManager, AudioConfig
from voice_assistant.audio.tts_manager import TTSManager
from voice_assistant.llm.gemini_client import GeminiClient
from voice_assistant.core.state_manager import StateManager, ConversationMessage
from voice_assistant.core.task_manager import TaskManager

class VoiceAssistant:
    """Main Voice Assistant with advanced capabilities."""
    
    def __init__(self, gemini_api_key: str, openweather_api_key: str):
        """Initialize the voice assistant."""
        # Initialize components
        self.gemini_client = GeminiClient(gemini_api_key)
        self.gemini_client.weather_api_key = openweather_api_key  # Set the weather API key
        self.audio_config = AudioConfig()
        self.audio_manager = AudioStreamManager(self.audio_config)
        self.tts_manager = TTSManager()
        self.state_manager = StateManager()
        self.task_manager = TaskManager(self.state_manager)
        
        # Register task callback
        self.task_manager.add_task_callback(self._on_task_completed)
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        
        # State management
        self.current_state = AssistantState.IDLE
        self.wake_words = WAKE_WORDS
        self.should_stop = False
        self.conversation_active = False
        self.is_sleeping = False  # New state for sleep mode
        
        # Error recovery
        self.error_count = 0
        self.max_errors = MAX_ERRORS
        
        # Event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        logger.info("Voice Assistant initialized successfully!")
    
    def speak(self, text: str):
        """Text-to-speech with state management."""
        try:
            self.current_state = AssistantState.SPEAKING
            self.tts_manager.speak(text)
        finally:
            self.current_state = AssistantState.IDLE
    
    def _on_task_completed(self, task):
        """Handle task completion."""
        if task.type == TaskType.TIMER:
            # Play alarm sound
            alarm_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'alarm.wav')
            if os.path.exists(alarm_path):
                self.audio_manager.play_wav_file(alarm_path)
            self.speak(f"Timer finished! {task.content}")
        elif task.type == TaskType.REMINDER:
            self.speak(f"Reminder: {task.content}")
    
    def listen_for_wake_word(self) -> bool:
        """Listen for wake word using streaming audio."""
        try:
            self.current_state = AssistantState.LISTENING
            
            # Record audio stream
            audio_data = self.audio_manager.record_audio_stream(timeout=5.0)
            
            if audio_data:
                # Convert to speech
                try:
                    # Create temporary wav file for speech recognition
                    with wave.open('temp_audio.wav', 'wb') as wav_file:
                        wav_file.setnchannels(self.audio_config.channels)
                        wav_file.setsampwidth(2)  # 16-bit
                        wav_file.setframerate(self.audio_config.sample_rate)
                        wav_file.writeframes(audio_data)
                    
                    # Use speech recognition
                    with sr.AudioFile('temp_audio.wav') as source:
                        audio = self.recognizer.record(source)
                        text = self.recognizer.recognize_google(audio, language='en-US')
                        
                        logger.info(f"Heard: {text}")
                        
                        # Check for wake words
                        text_lower = text.lower()
                        for wake_word in self.wake_words:
                            if wake_word in text_lower:
                                return True
                                
                except sr.UnknownValueError:
                    pass  # No speech detected
                except sr.RequestError as e:
                    logger.error(f"Speech recognition error: {e}")
                finally:
                    # Clean up temp file
                    try:
                        os.remove('temp_audio.wav')
                    except:
                        pass
            
            return False
            
        except Exception as e:
            logger.error(f"Wake word detection error: {e}")
            self.error_count += 1
            return False
        finally:
            self.current_state = AssistantState.IDLE
    
    def listen_for_command(self) -> str:
        """Listen for user command."""
        try:
            self.current_state = AssistantState.LISTENING
            logger.info("Listening for command...")
            
            # Record audio with longer timeout for commands
            audio_data = self.audio_manager.record_audio_stream(timeout=10.0)
            
            if audio_data:
                try:
                    # Create temporary wav file
                    with wave.open('temp_command.wav', 'wb') as wav_file:
                        wav_file.setnchannels(self.audio_config.channels)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(self.audio_config.sample_rate)
                        wav_file.writeframes(audio_data)
                    
                    # Speech recognition
                    with sr.AudioFile('temp_command.wav') as source:
                        audio = self.recognizer.record(source)
                        text = self.recognizer.recognize_google(audio, language='en-US')
                        
                        logger.info(f"Command: {text}")
                        return text
                        
                except sr.UnknownValueError:
                    return None
                except sr.RequestError as e:
                    logger.error(f"Speech recognition error: {e}")
                    return None
                finally:
                    try:
                        os.remove('temp_command.wav')
                    except:
                        pass
            
            return None
            
        except Exception as e:
            logger.error(f"Command listening error: {e}")
            self.error_count += 1
            return None
        finally:
            self.current_state = AssistantState.IDLE
    
    async def process_command(self, command: str) -> str:
        """Process user command and generate response."""
        try:
            self.current_state = AssistantState.PROCESSING
            
            # Add to conversation history
            message = ConversationMessage(role="user", content=command)
            self.state_manager.update_conversation(message)
            
            # Check for task-specific intents
            task_response = self._handle_task_commands(command)
            if task_response:
                return task_response
            
            # Generate response using Gemini
            context = self._build_context()
            response = await self.gemini_client.generate_response(command, context)
            
            # Add assistant response to history
            response_message = ConversationMessage(role="model", content=response)
            self.state_manager.update_conversation(response_message)
            
            # Reset error count on successful processing
            self.error_count = 0
            
            return response
            
        except Exception as e:
            logger.error(f"Command processing error: {e}")
            self.error_count += 1
            return "I'm sorry, I had trouble processing that. Could you try again?"
        finally:
            self.current_state = AssistantState.IDLE
    
    def _handle_task_commands(self, command: str) -> str:
        """Handle specific task commands."""
        command_lower = command.lower()
        
        # Sleep commands
        if any(phrase in command_lower for phrase in ['sleep', 'okay for now', 'goodbye for now']):
            self.is_sleeping = True
            return "Going to sleep. Say a wake word when you need me."
        
        # Timer commands
        if any(word in command_lower for word in ['timer', 'set timer', 'countdown']):
            return self._create_timer(command)
        
        # Reminder commands
        if any(word in command_lower for word in ['remind', 'reminder', 'remember to']):
            return self._create_reminder(command)
        
        # Note commands
        if any(word in command_lower for word in ['note', 'write down', 'save this']):
            return self._create_note(command)
        
        # List tasks
        if any(word in command_lower for word in ['list tasks', 'show tasks', 'my tasks']):
            return self._list_tasks()
        
        return None
    
    def _create_timer(self, command: str) -> str:
        """Create a timer from voice command."""
        # Extract duration
        patterns = [
            (r'(\d+)\s*(?:minute|min)s?', 60),
            (r'(\d+)\s*(?:hour|hr)s?', 3600),
            (r'(\d+)\s*(?:second|sec)s?', 1)
        ]
        
        total_seconds = 0
        for pattern, multiplier in patterns:
            matches = re.findall(pattern, command.lower())
            for match in matches:
                value = int(match)
                total_seconds += value * multiplier
        
        if total_seconds > 0:
            scheduled_time = datetime.now() + timedelta(seconds=total_seconds)
            task_id = self.task_manager.create_task(
                TaskType.TIMER,
                f"Timer for {total_seconds} seconds",
                scheduled_time=scheduled_time,
                metadata={'duration': total_seconds}
            )
            
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            
            if minutes > 0:
                return f"Timer set for {minutes} minute{'s' if minutes != 1 else ''} and {seconds} second{'s' if seconds != 1 else ''}."
            else:
                return f"Timer set for {seconds} second{'s' if seconds != 1 else ''}."
        else:
            return "I couldn't understand the timer duration. Please specify how long you want the timer for."
    
    def _create_reminder(self, command: str) -> str:
        """Create a reminder from voice command."""
        # Simple time parsing - you could enhance this
        time_patterns = [
            (r'in (\d+) minutes?', lambda m: datetime.now() + timedelta(minutes=int(m))),
            (r'in (\d+) hours?', lambda m: datetime.now() + timedelta(hours=int(m))),
            (r'at (\d{1,2}):(\d{2})', lambda h, m: datetime.now().replace(hour=int(h), minute=int(m), second=0, microsecond=0)),
        ]
        
        scheduled_time = None
        for pattern, time_func in time_patterns:
            match = re.search(pattern, command.lower())
            if match:
                try:
                    if len(match.groups()) == 1:
                        scheduled_time = time_func(match.group(1))
                    else:
                        scheduled_time = time_func(match.group(1), match.group(2))
                    break
                except:
                    continue
        
        task_id = self.task_manager.create_task(
            TaskType.REMINDER,
            command,
            scheduled_time=scheduled_time,
            metadata={'original_command': command}
        )
        
        if scheduled_time:
            return f"Reminder set for {scheduled_time.strftime('%I:%M %p')}."
        else:
            return "Reminder noted. I'll help you specify the time later."
    
    def _create_note(self, command: str) -> str:
        """Create a note from voice command."""
        task_id = self.task_manager.create_task(
            TaskType.NOTE,
            command,
            metadata={'created_via': 'voice'}
        )
        return "Note saved successfully."
    
    def _list_tasks(self) -> str:
        """List active tasks."""
        active_tasks = [task for task in self.task_manager.tasks.values() if not task.completed]
        
        if not active_tasks:
            return "You have no active tasks."
        
        task_list = []
        for task in active_tasks:
            if task.type == TaskType.TIMER and task.scheduled_time:
                remaining = (task.scheduled_time - datetime.now()).total_seconds()
                if remaining > 0:
                    task_list.append(f"Timer: {int(remaining // 60)} minutes {int(remaining % 60)} seconds remaining")
            elif task.type == TaskType.REMINDER:
                if task.scheduled_time:
                    task_list.append(f"Reminder at {task.scheduled_time.strftime('%I:%M %p')}: {task.content}")
                else:
                    task_list.append(f"Reminder: {task.content}")
            elif task.type == TaskType.NOTE:
                task_list.append(f"Note: {task.content[:50]}...")
        
        if len(task_list) <= 3:
            return f"Here are your active tasks:\n" + "\n".join(task_list)
        else:
            return f"You have {len(task_list)} active tasks. Here are the first 3:\n" + "\n".join(task_list[:3])
    
    def _build_context(self) -> str:
        """Build context for Gemini from conversation history."""
        history = self.state_manager.get('conversation_history', [])
        if not history:
            return SYSTEM_PROMPT
        
        # Get last 5 messages for context
        recent_messages = history[-5:]
        context = SYSTEM_PROMPT + "\n\nRecent conversation:\n"
        
        for msg in recent_messages:
            role = "User" if msg['role'] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n"
        
        return context
    
    def run(self):
        """Main assistant loop."""
        try:
            self.speak("Voice assistant initialized and ready.")
            
            while not self.should_stop:
                try:
                    # Listen for wake word
                    if self.listen_for_wake_word():
                        self.is_sleeping = False  # Wake up when wake word is detected
                        self.speak("Yes?")
                        
                        # Listen for command
                        command = self.listen_for_command()
                        if command:
                            # Process command asynchronously
                            response = self.loop.run_until_complete(self.process_command(command))
                            self.speak(response)
                            
                            # Check for conversation end
                            if any(phrase in command.lower() for phrase in ['goodbye', 'bye', 'stop', 'exit']):
                                self.speak("Goodbye!")
                                self.should_stop = True
                    
                    # If sleeping, only listen for wake word
                    elif self.is_sleeping:
                        continue
                    
                    # Check error count
                    if self.error_count >= self.max_errors:
                        logger.error("Too many errors, stopping assistant")
                        self.speak("I'm experiencing technical difficulties. Please restart me.")
                        self.should_stop = True
                    
                    # Small delay to prevent CPU overuse
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    self.error_count += 1
                    time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Assistant stopped by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            self.task_manager.stop_scheduler()
            self.audio_manager.cleanup()
            self.tts_manager.cleanup()
            self.state_manager.save_state()
            self.loop.close()
            logger.info("Assistant cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}") 