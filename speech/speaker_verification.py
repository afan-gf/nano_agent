import os
import tempfile
import wave
from typing import Dict, Any
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

class SpeakerVerification:
    """
    Speaker verification using voiceprint comparison
    """
    def __init__(self, config: Dict[str, Any]):
        self.registered_voice_path = config.get("speaker_verification_voice_path", "")
        self.threshold = config.get("speaker_verification_threshold", 0.5)
        self.model_name = config.get("speaker_verification_model", "iic/speech_campplus_sv_zh-cn_16k-common")
        self.model = None
        
        # Try to initialize the speaker verification model
        try:
            # Use modelscope.pipelines to load the speaker verification model
            self.model = pipeline(task=Tasks.speaker_verification, model=self.model_name)
        except Exception as e:
            print(f"Warning: Could not load speaker verification model: {e}")
            print("Speaker verification will be skipped.")
    
    def verify(self, audio_data: bytes) -> bool:
        """
        Verify if the audio matches the registered speaker
        """
        # If no registered voice path is provided or model failed to load, skip verification
        if not self.registered_voice_path or not os.path.exists(self.registered_voice_path):
            print("Speaker verification: No registered voice file found, skipping verification")
            return True
            
        # If model failed to load, skip verification
        if self.model is None:
            print("Speaker verification: Model not available, skipping verification")
            return True
        
        # Create a temporary WAV file for the input audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            temp_filename = tmp_file.name
            
        try:
            # Write audio data to temporary WAV file
            with wave.open(temp_filename, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 16 bits
                wf.setframerate(16000)  # 16kHz
                wf.writeframes(audio_data)
            
            # Perform speaker verification
            result = self.model([temp_filename, self.registered_voice_path])
            
            # Extract similarity score
            score = result["score"]
            is_same_spk = result["decision"] if "decision" in result else (score >= self.threshold)
            
            print(f"Speaker verification: score={score}, decision={is_same_spk}")
            
            return is_same_spk
        except Exception as e:
            print(f"Speaker verification error: {e}")
            # In case of error, we'll allow processing to continue
            return True
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)