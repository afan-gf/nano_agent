import os
import tempfile
import wave
from typing import Dict, Any
from funasr import AutoModel

class ASR:
    """
    Automatic Speech Recognition using SenseVoiceSmall model
    """
    def __init__(self, config: Dict[str, Any]):
        # Remove the remote_code parameter which was causing the error
        model_name = config.get("asr_model", "iic/SenseVoiceSmall")
        self.model = AutoModel(model=model_name, trust_remote_code=True)
    
    def transcribe(self, audio_data: bytes) -> str:
        # Create a temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            temp_filename = tmp_file.name
            
        try:
            # Write audio data to temporary WAV file
            with wave.open(temp_filename, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 16 bits
                wf.setframerate(16000)  # 16kHz
                wf.writeframes(audio_data)
            
            # Transcribe using SenseVoiceSmall model with the temporary file
            result = self.model.generate(input=temp_filename, 
                                         cache={}, 
                                         language="auto", # "zh", "en", "yue", "ja", "ko", "nospeech"
                                         use_itn=True)
            
            return result[0]['text']
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)