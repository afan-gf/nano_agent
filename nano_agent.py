from config import get_config
from voice_chat_agent import VoiceChatAgent

if __name__ == "__main__":
    config = get_config()
    
    print("Configuration:")
    for key, value in config.items():
        # Mask API keys for security
        if "api_key" in key and value:
            print(f"  {key}: {'*' * len(value)}")
        else:
            print(f"  {key}: {value}")
    
    agent = VoiceChatAgent(config)
    agent.run_agent()