import io
import pygame
import tempfile
import os
import asyncio
from typing import Dict, Any, Optional
from utils.logger import print_timestamp_debug_log

class AudioStreamBuffer:
    """Buffer for streaming audio data"""
    
    def __init__(self, min_chunk_size: int = 3200):  # Increased to ~200ms at 16kHz
        self.buffer = io.BytesIO()
        self.min_chunk_size = min_chunk_size
        self.finished = False
        self.condition = asyncio.Condition()
        
    async def write(self, data: bytes):
        """Write audio data to buffer"""
        async with self.condition:
            self.buffer.write(data)
            # Notify waiting consumers if we have enough data
            if self.buffer.tell() >= self.min_chunk_size:
                self.condition.notify_all()
    
    async def read_chunk(self) -> Optional[bytes]:
        """Read a chunk of audio data when available"""
        async with self.condition:
            while self.buffer.tell() < self.min_chunk_size and not self.finished:
                await self.condition.wait()
                
            if self.buffer.tell() == 0:
                return None
                
            # Return all buffered data
            self.buffer.seek(0)
            data = self.buffer.read()
            self.buffer = io.BytesIO()  # Reset buffer
            return data if data else None
    
    async def finish(self):
        """Mark the stream as finished"""
        async with self.condition:
            self.finished = True
            self.condition.notify_all()

class AudioPlayer:
    """
    Audio player using pygame with streaming capability
    """
    def __init__(self, config: Dict[str, Any]):
        frequency = config.get("audio_player_frequency", 24000)
        pygame.mixer.pre_init(frequency=frequency, size=-16, channels=1, buffer=512)  # Better settings for TTS
        pygame.mixer.init()
        self.is_playing = False
        self.current_sound = None
        self.playback_interrupted = False
    
    async def play_stream(self, stream: AudioStreamBuffer):
        """Play audio stream in real-time"""
        self.playback_interrupted = False
        try:
            # Play audio chunks as they arrive
            while not self.playback_interrupted:
                chunk = await stream.read_chunk()
                if chunk is None:
                    break
                    
                if not self.playback_interrupted:
                    await self._play_audio_chunk(chunk)
                
            # Play any remaining audio data
            if not self.playback_interrupted:
                chunk = await stream.read_chunk()
                if chunk:
                    await self._play_audio_chunk(chunk)
        except Exception as e:
            print(f"Error during playback: {e}")
        finally:
            self.playback_interrupted = False

    async def _play_audio_chunk(self, audio_data: bytes):
        """Play a single audio chunk"""
        if self.playback_interrupted:
            return
            
        try:
            # Write to BytesIO for pygame
            audio_file = io.BytesIO(audio_data)
            
            print_timestamp_debug_log(f"play audio trunk_{len(audio_data)}...")
            # Load and play sound
            sound = pygame.mixer.Sound(file=audio_file)
            channel = sound.play()
            
            # Wait for chunk to finish playing
            while channel.get_busy() and not self.playback_interrupted:
                await asyncio.sleep(0.01)
        except pygame.error as e:
            print(f"Pygame audio error: {e}")
            # Try saving to temp file as fallback
            await self._play_chunk_with_temp_file(audio_data)
        except Exception as e:
            print(f"Unexpected error in audio playback: {e}")
            # Try alternative method for problematic audio data
            await self._play_chunk_as_wav(audio_data)
            
    async def _play_chunk_with_temp_file(self, audio_data: bytes):
        """Fallback method using temporary file"""
        if self.playback_interrupted:
            return
            
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_filename = temp_file.name
                
            # Load and play sound from file
            sound = pygame.mixer.Sound(temp_filename)
            channel = sound.play()
            
            # Wait for playback to finish
            while channel.get_busy() and not self.playback_interrupted:
                await asyncio.sleep(0.01)
                
            # Clean up
            os.unlink(temp_filename)
        except Exception as e:
            print(f"Fallback audio playback error: {e}")
            # Try converting to WAV as last resort
            await self._play_chunk_as_wav(audio_data)
    
    # 添加: 处理有问题的音频数据的新方法
    async def _play_chunk_as_wav(self, audio_data: bytes):
        """
        Additional fallback method converting MP3 to WAV format
        This helps with problematic MP3 data that causes mpg123 errors
        """
        if self.playback_interrupted:
            return
            
        try:
            import subprocess
            import sys
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as mp3_temp:
                mp3_temp.write(audio_data)
                mp3_filename = mp3_temp.name
                
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_temp:
                wav_filename = wav_temp.name
                
            try:
                # Use ffmpeg to convert MP3 to WAV (more robust than pygame's MP3 decoder)
                # This bypasses the problematic mpg123 library
                result = subprocess.run([
                    "ffmpeg", "-y", "-i", mp3_filename, 
                    "-acodec", "pcm_s16le", "-ar", "24000", "-ac", "1", 
                    wav_filename
                ], capture_output=True, timeout=10)
                
                if result.returncode == 0 and os.path.exists(wav_filename):
                    # Load and play the converted WAV file
                    sound = pygame.mixer.Sound(wav_filename)
                    channel = sound.play()
                    
                    # Wait for playback to finish
                    while channel.get_busy() and not self.playback_interrupted:
                        await asyncio.sleep(0.01)
                else:
                    print("Failed to convert MP3 to WAV for playback")
            finally:
                # Clean up temporary files
                for filename in [mp3_filename, wav_filename]:
                    if os.path.exists(filename):
                        os.unlink(filename)
                        
        except Exception as e:
            print(f"Error in _play_chunk_as_wav: {e}")
            # Last resort: try to play with pygame even if it might fail
            try:
                audio_file = io.BytesIO(audio_data)
                sound = pygame.mixer.Sound(file=audio_file)
                channel = sound.play()
                while channel.get_busy() and not self.playback_interrupted:
                    await asyncio.sleep(0.01)
            except Exception:
                print("Completely failed to play audio chunk")
                pass
    
    def interrupt(self):
        pygame.mixer.stop()
        self.playback_interrupted = True
        return True