import os

def get_config():
    return {
        # API Keys
        "llm_api_key": os.getenv("DASHSCOPE_API_KEY"),
        "vlm_api_key": os.getenv("DASHSCOPE_API_KEY"),
        
        # Model settings
        "llm_model": "qwen-plus",
        "vlm_model": "qwen-vl-plus",
        "asr_model": "iic/SenseVoiceSmall",
        
        # Base URLs
        "llm_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "vlm_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        
        # System prompts
        "llm_system_prompt": "你是 小白, 人工智能助手。提供有用的回复，回复精简不超过200个字。",
        
        # Voice settings
        "tts_voice": "zh-CN-XiaoxiaoNeural",
        "tts_rate": "+0%",
        "tts_volume": "+0%",
        
        # Memory settings
        "memory_max_turns": 100,
        
        # Session settings
        "session_timeout": 20.0,
        "session_end_phrases": [
            "再见", "拜拜", "bye", "goodbye", "结束对话", "结束聊天", 
            "就聊到这里", "下次再聊", "回聊", "结束了", "聊完了"
        ],
        
        # Audio settings
        "audio_player_frequency": 24000,
        "audio_recorder_sample_rate": 16000,
        "audio_recorder_chunk_size": 1024,
        "silence_threshold": 2.0,
        
        # VAD settings
        "vad_sample_rate": 16000,
        "vad_frame_duration": 30,
        "vad_aggressiveness": 3,
        
        # Camera settings
        "camera_device_index": 0,
        "camera_warmup_frames": 5,
        "camera_warmup_delay": 0.1,
        
        # VLM settings
        "vlm_max_tokens": 1500,
        
        # Guardrail settings
        "guardrail_supported_languages": ['zh', 'en'],
        "guardrail_unspeakable_chars_pattern": r'[\U0001F600-\U0001F64F|\U0001F300-\U0001F5FF|\U0001F680-\U0001F6FF|\U0001F1E0-\U0001F1FF|\u2600-\u26FF|\u2700-\u27BF]+',
        "guardrail_special_chars_pattern": r'[*#$%^&\[\]{}|<>`]+',
        "guardrail_unsafe_keywords": ['violence', 'hate', 'explicit'],
        
        # Speaker verification
        "speaker_verification_voice_path": "./reference_voice.wav",
        "speaker_verification_threshold": 0.35,
        "speaker_verification_model": "iic/speech_campplus_sv_zh-cn_16k-common",
        
        # Search settings
        "search_timeout": 10
    }