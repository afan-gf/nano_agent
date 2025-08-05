# Nano Voice Agent
An intelligent voice chat agent that combines realtime speech recognition, LLM, text-to-speech, vision, and web search capabilities to create a helpful conversational AI Agent.

Features

- Voice Interaction: Real-time voice input and output with voice activity detection
- Speech Recognition: Automatic speech recognition using SenseVoiceSmall model
- Natural Language Processing: Powered by Qwen-plus large language model
- Text-to-Speech: High-quality speech synthesis using Edge-TTS
- Computer Vision: Image analysis capabilities with Qwen-vl-plus model
- Web Search: Up-to-date information retrieval from Baidu and Google
- Speaker Verification: Voiceprint-based speaker authentication
- Conversation Memory: Context-aware conversation management with session handling
- Content Safety: Text validation and cleaning for TTS output

Prerequisites

- Python 3.10 or higher
- Audio input/output devices (microphone and speakers)
- Camera (for vision capabilities)
- API keys for DashScope (for LLM and VLM services)

Installation

1. Clone the repository:
   git clone https://github.com/afan-gf/nano_voice_agent.git
   cd nano_voice_agent

2. Install required dependencies:
   pip install -r requirements.txt

3. Set up environment variables:
   export DASHSCOPE_API_KEY=your_dashscope_api_key
