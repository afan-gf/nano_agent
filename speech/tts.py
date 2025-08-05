import edge_tts
from typing import Dict, Any
from components.text_guardrail import TextGuardrail

class TTS:
    """
    Text-to-Speech using Edge-TTS with guardrail
    """
    def __init__(self, config: Dict[str, Any]):
        self.voice = config.get("tts_voice", "zh-CN-XiaoxiaoNeural")
        self.rate = config.get("tts_rate", "+0%")
        self.volume = config.get("tts_volume", "+0%")
        self.guardrail = TextGuardrail(config)
    
    async def synthesize(self, text: str) -> bytes:
        # Validate and clean text before synthesis
        is_valid, message, cleaned_text = self.guardrail.validate_and_clean(text)
        
        if not is_valid:
            # If validation fails, synthesize the error message instead
            print(f"TTS Guardrail Warning: {message}")
            # Use the message to inform the user about the issue
            communicate = edge_tts.Communicate(message, self.voice, rate=self.rate, volume=self.volume)
        else:
            # If validation passes, use the cleaned text
            print(f"TTS Guardrail: {message}")
            communicate = edge_tts.Communicate(cleaned_text, self.voice, rate=self.rate, volume=self.volume)
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data