from config import get_config
from voice_chat_agent import VoiceChatAgent

if __name__ == "__main__":
    config = get_config()    
    agent = VoiceChatAgent(config)
    agent.run_agent()
