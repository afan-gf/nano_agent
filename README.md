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

Configuration

The agent can be configured through the config dictionary in the main script. Key configuration options include:

- API Keys: DashScope API key for LLM and VLM services
- Model Settings: Selection of models for different tasks
- Audio Settings: Sample rates, chunk sizes, and other audio parameters
- Voice Settings: TTS voice selection and parameters
- Memory Settings: Conversation history management
- Session Settings: Session timeout and end phrases
- VAD Settings: Voice activity detection parameters
- Camera Settings: Camera device and capture parameters
- Guardrail Settings: Content safety and text cleaning parameters
- Speaker Verification: Voiceprint verification parameters

Usage

Run the voice chat agent: 
python nano_agent.py

The agent will start listening for voice input. Speak naturally and wait for the agent to respond. The conversation will continue until you say one of the predefined end phrases like "再见" or "bye".

Capabilities

Voice Interaction
- Real-time voice recording with silence detection
- Voice activity detection to identify speech segments
- Audio playback with interruption handling

Natural Language Processing
- Context-aware conversation with memory management
- Session-based conversation handling with timeout
- Support for function calling (tools)

Tools Integration
1. Vision Analysis: Capture images and analyze visual content
2. Web Search: Retrieve up-to-date information from search engines

Content Safety
- Text validation and cleaning before TTS
- Language detection and filtering
- Removal of unspeakable characters and special symbols

Speaker Verification
- Voiceprint-based authentication
- Configurable verification threshold
- Fallback to skip verification if not configured

Architecture

The system consists of several modular components:

- Memory: Conversation history management
- ASR: Automatic Speech Recognition using SenseVoiceSmall
- VAD: Voice Activity Detection using WebRTC
- SpeakerVerification: Speaker authentication
- LLM: Large Language Model interface (Qwen-plus)
- TTS: Text-to-Speech using Edge-TTS
- VLM: Vision Language Model (Qwen-vl-plus)
- SearchEngine: Web search capabilities
- AudioPlayer: Audio playback management
- Camera: Image capture functionality
- SessionManager: Conversation session management
- AudioRecorder: Audio recording with VAD
- TextGuardrail: Content safety and text cleaning

Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

License

This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgments

- DashScope (https://dashscope.aliyun.com/) for LLM and VLM services
- ModelScope (https://modelscope.cn/) for various AI models
- Edge-TTS (https://github.com/rany2/edge-tts) for text-to-speech capabilities
- WebRTC VAD (https://github.com/wiseman/py-webrtcvad) for voice activity detection
- FunASR (https://github.com/modelscope/FunASR) for speech recognition models
