import re
from typing import Dict, Any

class TextGuardrail:
    """
    Guardrail for text content safety and cleaning before TTS
    """
    def __init__(self, config: Dict[str, Any]):
        # Define supported languages (Chinese and English)
        self.supported_languages = config.get("guardrail_supported_languages", ['zh', 'en'])
        
        # Define patterns for characters that can't be converted to speech
        self.unspeakable_chars = re.compile(config.get("guardrail_unspeakable_chars_pattern", 
                                          r'[\U0001F600-\U0001F64F'  # Emoticons
                                          r'|\U0001F300-\U0001F5FF'  # Miscellaneous Symbols and Pictographs
                                          r'|\U0001F680-\U0001F6FF'  # Transport and Map Symbols
                                          r'|\U0001F1E0-\U0001F1FF'  # Flags
                                          r'|\u2600-\u26FF'          # Miscellaneous Symbols
                                          r'|\u2700-\u27BF]+'), flags=re.UNICODE)  # Dingbats
        
        # Define special characters to be removed
        self.special_chars = re.compile(config.get("guardrail_special_chars_pattern", r'[*#$%^&\[\]{}|\\<>~`]+'))
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the text (simplified approach)
        """
        # Count Chinese characters
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        # Count English letters
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if chinese_chars > english_chars:
            return 'zh'
        else:
            return 'en'
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing unspeakable characters and special characters
        """
        # Remove unspeakable characters
        cleaned_text = self.unspeakable_chars.sub('', text)
        
        # Remove special characters
        cleaned_text = self.special_chars.sub('', cleaned_text)
        
        # Remove extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text
    
    def check_compliance(self, text: str) -> tuple[bool, str]:
        """
        Check if text complies with safety requirements
        Returns (is_compliant, message)
        """
        # Check language support
        detected_lang = self.detect_language(text)
        if detected_lang not in self.supported_languages:
            return False, f"Unsupported language detected: {detected_lang}. Only Chinese and English are supported."
        
        # Check for potentially unsafe content patterns
        # This is a simplified example - in a real implementation, you might connect to a content moderation API
        unsafe_keywords = []  # Simplified example
        for keyword in unsafe_keywords:
            if keyword in text.lower():
                return False, f"Content contains potentially unsafe keyword: {keyword}"
        
        return True, "Content is compliant"
    
    def validate_and_clean(self, text: str) -> tuple[bool, str, str]:
        """
        Validate text and return cleaned version if compliant
        Returns (is_valid, message, cleaned_text)
        """
        # Check compliance
        is_compliant, compliance_message = self.check_compliance(text)
        if not is_compliant:
            return False, compliance_message, ""
        
        # Clean text
        cleaned_text = self.clean_text(text)
        
        return True, "Text is valid and cleaned", cleaned_text