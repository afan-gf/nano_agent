# Nano Voice Agent

Nano Voice Agent is an intelligent voice chat agent that enables natural conversation with AI using voice input and output. It integrates speech recognition, natural language processing, text-to-speech synthesis, and various tools to create a comprehensive voice interaction experience.

## Features

- **Voice Interaction**: Full voice-based conversation with automatic speech recognition (ASR) and text-to-speech (TTS)
- **Multi-Turn Conversation**: Multi-turn conversation with working momery
- **Natural Language Understanding**: Powered by large language models for contextual understanding
- **Visual Capabilities**: Integration with camera for image capture and vision-language model analysis
- **Web Search**: Real-time information retrieval from Baidu and Google
- **Session Management**: Intelligent session handling with timeout and context management
- **Content Safety**: Text guardrails for content filtering and safety
- **Speaker Verification**: Optional speaker verification for personalized experience
- **Real-time Audio Processing**: Voice activity detection (VAD) and audio streaming

## Architecture

The system consists of several key components:

1. **VoiceChatAgent**: Main orchestrator managing the complete voice interaction workflow
2. **Audio Processing**: AudioRecorder and AudioPlayer for handling input/output audio
3. **Speech Components**: ASR, VAD, TTS, and SpeakerVerification for speech processing
4. **AI Models**: LLM (Large Language Model) and VLM (Vision-Language Model) for intelligence
5. **Tools**: Web search engine integration for up-to-date information
6. **Memory Management**: WorkMemory and SessionManager for context handling
7. **Safety**: TextGuardrail for content filtering

## Requirements

- Python 3.10+
- Audio libraries: PyAudio, webrtcvad, pygame, edge-tts
- Speech recognition: funasr, modelscope
- Computer vision: opencv-python
- Web libraries: requests, beautifulsoup4
- AI libraries: openai, dashscope
- Search tools: baidusearch, googlesearch-python

## Installation from git repo

1. Setup conda
```bash
conda create --name nano_agent python=3.10
conda activate nano_agent
```

2. Clone the repository:
```bash
git clone https://github.com/afan-gf/nano_voice_agent.git
cd nano_voice_agent
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the system by creating a [config.py] file with necessary API keys and settings.
export your API-KEY
```bash
export DASHSCOPE_API_KEY=your_dashscope_api_key
```

## Usage

Run the voice agent:
```bash
python nano_agent.py
```

The agent will start listening for voice input. Speak naturally and wait for the AI response.

## Configuration

Key configuration parameters include:

- API keys for LLM, VLM, and other services
- Audio settings (sample rate, chunk size, etc.)
- Model parameters (model names, system prompts)
- Session management (timeout, end phrases)
- Safety settings (language filters, character patterns)
- Camera settings (device index, warmup parameters)
- Search settings (timeout, result count)

## Tools

The agent supports two main tools:

1. **Vision Analysis**: Capture images and analyze them with a vision-language model
2. **Web Search**: Search the web for up-to-date information using Baidu or Google

## Safety Features

- Text guardrails to filter unsafe content
- Language detection and filtering
- Special character removal
- Emoji and symbol filtering

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
