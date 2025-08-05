import webrtcvad
from typing import Dict, Any

class VAD:
    """
    Voice Activity Detection using WebRTC VAD
    """
    def __init__(self, config: Dict[str, Any]):
        self.sample_rate = config.get("vad_sample_rate", 16000)
        self.frame_duration = config.get("vad_frame_duration", 30)
        aggressiveness = config.get("vad_aggressiveness", 3)
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        self.vad = webrtcvad.Vad(aggressiveness)  # Aggressiveness mode 3 (highest)
        
        # Validate sample rate
        if self.sample_rate not in [8000, 16000, 32000, 48000]:
            raise ValueError("Sample rate must be 8000, 16000, 32000, or 48000")
            
        # Validate frame duration
        if self.frame_duration not in [10, 20, 30]:
            raise ValueError("Frame duration must be 10, 20, or 30 ms")
    
    def is_speech(self, audio_frame: bytes) -> bool:
        # Check if frame size is correct
        expected_size = int(self.sample_rate * self.frame_duration / 1000) * 2  # 2 bytes per sample (16-bit)
        if len(audio_frame) != expected_size:
            # Pad or truncate frame to correct size
            if len(audio_frame) < expected_size:
                audio_frame = audio_frame.ljust(expected_size, b'\x00')
            else:
                audio_frame = audio_frame[:expected_size]
        
        try:
            return self.vad.is_speech(audio_frame, self.sample_rate)
        except Exception:
            # If VAD fails, assume it's not speech
            return False