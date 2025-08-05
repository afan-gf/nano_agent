import pyaudio
from typing import Dict, Any, Optional
from speech.vad import VAD

class AudioRecorder:
    """
    Audio recording functionality with VAD and silence detection
    """
    def __init__(self, config: Dict[str, Any]):
        self.sample_rate = config.get("audio_recorder_sample_rate", 16000)
        self.chunk_size = config.get("audio_recorder_chunk_size", 1024)
        self.format = pyaudio.paInt16
        self.channels = 1
        self.vad = VAD(config)
    
    def initialize_audio_stream(self) -> tuple:
        """
        Initialize the PyAudio stream for recording
        """
        p = pyaudio.PyAudio()
        stream = p.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
        )
        return p, stream
    
    def read_audio_chunk(self, stream) -> Optional[bytes]:
        """
        Read a chunk of audio data from the stream
        """
        try:
            data = stream.read(self.chunk_size, exception_on_overflow=False)
            return data
        except OSError as e:
            if e.errno == -9981:  # Input overflow
                print("Warning: Audio input overflow, skipping...")
                return None
            else:
                raise
    
    def cleanup_audio_stream(self, p, stream, stream_open: bool):
        """
        Clean up the audio stream and PyAudio resources
        """
        if stream_open:
            try:
                stream.stop_stream()
                stream.close()
            except Exception as e:
                print(f"Error closing audio stream: {e}")
        p.terminate()