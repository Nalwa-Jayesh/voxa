"""Audio stream management for voice input."""

import os
import wave
import queue
import time
import numpy as np
import pyaudio
import webrtcvad
from dataclasses import dataclass
from typing import Optional

from voice_assistant.utils.logging_config import logger
from voice_assistant.utils.constants import (
    DEFAULT_SAMPLE_RATE,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHANNELS,
    DEFAULT_SILENCE_THRESHOLD,
    DEFAULT_SILENCE_DURATION
)

@dataclass
class AudioConfig:
    """Configuration for audio input."""
    sample_rate: int = DEFAULT_SAMPLE_RATE
    chunk_size: int = DEFAULT_CHUNK_SIZE
    channels: int = DEFAULT_CHANNELS
    format: int = pyaudio.paInt16
    silence_threshold: int = DEFAULT_SILENCE_THRESHOLD
    silence_duration: float = DEFAULT_SILENCE_DURATION
    max_recording_time: float = 10.0

class AudioStreamManager:
    """Advanced audio streaming with PyAudio and voice activity detection"""
    
    def __init__(self, config: AudioConfig):
        self.config = config
        self.audio = pyaudio.PyAudio()
        self.vad = webrtcvad.Vad(2) if self._check_vad() else None  # Aggressiveness level 2
        self.is_recording = False
        self.audio_queue = queue.Queue()
        
        # Find the best audio device
        self.input_device_index = self._find_best_input_device()
    
    def _check_vad(self) -> bool:
        """Check if VAD is available."""
        try:
            import webrtcvad
            return True
        except ImportError:
            logger.warning("webrtcvad not available - using basic silence detection")
            return False
        
    def _find_best_input_device(self) -> Optional[int]:
        """Find the best audio input device."""
        try:
            default_device = self.audio.get_default_input_device_info()
            return default_device['index']
        except Exception as e:
            logger.warning(f"Could not find default input device: {e}")
            # Fallback to first available device
            for i in range(self.audio.get_device_count()):
                try:
                    device_info = self.audio.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        return i
                except Exception:
                    continue
        return None
    
    def start_stream(self) -> pyaudio.Stream:
        """Start audio input stream."""
        try:
            stream = self.audio.open(
                format=self.config.format,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.config.chunk_size,
                stream_callback=self._audio_callback
            )
            return stream
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            raise
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Audio stream callback."""
        if self.is_recording:
            self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)
    
    def detect_voice_activity(self, audio_data: bytes) -> bool:
        """Detect voice activity in audio data."""
        if self.vad and len(audio_data) >= 320:  # 20ms at 16kHz
            # VAD expects 10, 20, or 30ms frames
            frame_size = 320  # 20ms at 16kHz
            for i in range(0, len(audio_data) - frame_size + 1, frame_size):
                frame = audio_data[i:i + frame_size]
                if len(frame) == frame_size:
                    try:
                        if self.vad.is_speech(frame, self.config.sample_rate):
                            return True
                    except Exception:
                        pass
            return False
        else:
            # Fallback to amplitude-based detection
            try:
                audio_np = np.frombuffer(audio_data, dtype=np.int16)
                rms = np.sqrt(np.mean(audio_np ** 2))
                return rms > self.config.silence_threshold
            except Exception:
                return False
    
    def record_audio_stream(self, timeout: float = 10.0) -> Optional[bytes]:
        """Record audio with voice activity detection."""
        stream = None
        try:
            stream = self.start_stream()
            stream.start_stream()
            
            self.is_recording = True
            audio_frames = []
            silence_start = None
            recording_start = time.time()
            
            logger.info("Recording started - speak now...")
            
            while time.time() - recording_start < timeout:
                try:
                    audio_data = self.audio_queue.get(timeout=0.1)
                    audio_frames.append(audio_data)
                    
                    has_voice = self.detect_voice_activity(audio_data)
                    
                    if has_voice:
                        silence_start = None
                    else:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > self.config.silence_duration:
                            if len(audio_frames) > 10:  # Ensure we have some audio
                                logger.info("Silence detected - stopping recording")
                                break
                            
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error during recording: {e}")
                    break
            
            self.is_recording = False
            
            if audio_frames:
                return b''.join(audio_frames)
            return None
            
        except Exception as e:
            logger.error(f"Recording failed: {e}")
            return None
        finally:
            self.is_recording = False
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    logger.error(f"Error closing stream: {e}")
    
    def cleanup(self):
        """Cleanup audio resources."""
        try:
            self.audio.terminate()
        except Exception as e:
            logger.error(f"Error during audio cleanup: {e}")
    
    def play_wav_file(self, wav_file_path: str):
        """Play a WAV file through the default audio output device."""
        try:
            # Open the WAV file
            with wave.open(wav_file_path, 'rb') as wf:
                # Get audio parameters
                channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                frame_rate = wf.getframerate()
                
                # Map sample width to PyAudio format
                if sample_width == 1:
                    format = pyaudio.paInt8
                elif sample_width == 2:
                    format = pyaudio.paInt16
                elif sample_width == 4:
                    format = pyaudio.paInt32
                else:
                    raise ValueError(f"Unsupported sample width: {sample_width}")
                
                # Create output stream
                stream = self.audio.open(
                    format=format,
                    channels=channels,
                    rate=frame_rate,
                    output=True
                )
                
                # Read data in chunks and play
                chunk_size = 1024
                data = wf.readframes(chunk_size)
                
                while data:
                    stream.write(data)
                    data = wf.readframes(chunk_size)
                
                # Clean up
                stream.stop_stream()
                stream.close()
                
        except Exception as e:
            logger.error(f"Error playing WAV file: {e}")
            # Try alternative playback method if the first one fails
            try:
                import winsound
                winsound.PlaySound(wav_file_path, winsound.SND_FILENAME)
            except Exception as e2:
                logger.error(f"Alternative playback also failed: {e2}") 