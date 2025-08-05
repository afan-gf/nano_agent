import asyncio
import io
import json
import threading
import time
import wave
import tempfile
import os
from collections import deque
from typing import List, Dict, Any, Optional

from components import WorkMemory, SessionManager, TextGuardrail
from speech import ASR, VAD, TTS, SpeakerVerification
from models import LLM, VLM
from audio import AudioRecorder, AudioPlayer
from vision import Camera
from tools import SearchEngine
from audio.audio_player import AudioStreamBuffer
from utils.logger import print_timestamp_debug_log
import edge_tts


class VoiceChatAgent:
    """
    Main voice chat agent implementing the complete workflow
    """
    def __init__(self, config: Dict[str, Any]):
        # Initialize components
        self.memory = WorkMemory(config)
        self.asr = ASR(config)
        self.speaker_verification = SpeakerVerification(config)
        self.llm = LLM(config)
        self.tts = TTS(config)
        self.vlm = VLM(config)
        self.search_engine = SearchEngine(config)
        self.audio_player = AudioPlayer(config)
        self.camera = Camera(config)
        
        # Session management
        self.session_manager = SessionManager(self.memory, config)
        
        # Audio recording
        self.audio_recorder = AudioRecorder(config)
        self.silence_threshold = config.get("silence_threshold", 2.0)  # seconds
        
        # Threading and async management
        self.recording = False
        self.processing = False
        self.tts_queue = asyncio.Queue()
        self.event_loop = None  # Store the event loop reference
        
        # Interrupt flag
        self.user_speaking = False
        
        # Text guardrail for content safety
        self.text_guardrail = TextGuardrail(config)
        
        # Tools for LLM
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "vision_analysis",
                    "description": "Analyze an image captured from the camera",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The user's request related to visual content"
                            }
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web for up-to-date information using Baidu or Google",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            },
                            "engine": {
                                "type": "string",
                                "enum": ["baidu", "google"],
                                "description": "Search engine to use (default: baidu)"
                            },
                            "num_results": {
                                "type": "integer",
                                "description": "Number of results to return (default: 5)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    
    async def handle_tool_calls(self, tool_calls) -> List[Dict[str, Any]]:
        """
        Handle tool calls from LLM
        """
        tool_responses = []
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            if function_name == "vision_analysis":
                # Capture image
                image_path = "captured_image.jpg"
                if self.camera.capture_image(image_path):
                    # Analyze with VLM
                    try:
                        result = await self.vlm.analyze(image_path, arguments["prompt"])
                        tool_responses.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": result
                        })
                    except Exception as e:
                        tool_responses.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                        "content": f"视觉分析失败: {str(e)}"
                        })
                else:
                    tool_responses.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": "无法捕获图像"
                    })
            
            elif function_name == "web_search":
                # Search the web
                try:
                    # Extract engine and query from arguments
                    query = arguments.get("query", "")
                    engine = arguments.get("engine", "baidu")  # Default to Baidu
                    num_results = arguments.get("num_results", 5)
                    
                    result = await self.search_engine.search(query, engine, num_results)
                    tool_responses.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": result
                    })
                except Exception as e:
                    tool_responses.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": f"搜索失败: {str(e)}"
                    })
        
        return tool_responses
    
    async def process_text_with_llm(self, text: str) -> str:
        """
        Process text with LLM and handle tool calls
        """
        # Check and update session context
        current_session_id = self.session_manager.check_and_update_session(text)
        
        # Add user message to memory
        self.memory.add_message(current_session_id, "user", text)
        
        # Get conversation history for current session
        history = self.memory.get_history(current_session_id)
        
        # Get LLM response
        start_time = time.time()
        response = await self.llm.generate(history, self.tools)
        print_timestamp_debug_log(f"Main routing LLM takes: {time.time()-start_time} s")
        
        # Handle tool calls if any
        if hasattr(response, 'tool_calls') and response.tool_calls:
            # Get tool responses
            start_time = time.time()
            tool_responses = await self.handle_tool_calls(response.tool_calls)
            print_timestamp_debug_log(f"Handle tool_calls takes: {time.time()-start_time} s")
            
            # Add the assistant message with tool calls to history first
            assistant_message = {
                "role": "assistant",
                "content": response.content if response.content else "",
                "tool_calls": [  # Convert tool_calls to the proper format
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in response.tool_calls
                ]
            }
            history.append(assistant_message)
            
            # Add tool responses to history
            for tool_response in tool_responses:
                history.append(tool_response)
            
            # Get final response after tool calls
            start_time = time.time()
            final_response = await self.llm.generate(history)
            print_timestamp_debug_log(f"LLM final summarize takes: {time.time()-start_time} s")
            reply = final_response.content
        else:
            reply = response.content
        
        # Add assistant message to memory
        self.memory.add_message(current_session_id, "assistant", reply)
        
        return reply
    
    def _start_recording(self, data: bytes) -> tuple:
        """
        Start recording when speech is detected
        """
        print("Started recording...")
        self.user_speaking = True
        
        # Note: We no longer interrupt audio here, but will do so after
        # confirming 1 second of continuous speech
        
        return [data], None  # recording_buffer, silence_start

    def _process_audio_chunk(self, data: bytes, recording_buffer: list, silence_start: float) -> tuple:
        """
        Process an audio chunk during recording
        """
        recording_buffer.append(data)
        is_speech = self.audio_recorder.vad.is_speech(data)
        
        # Check if we should interrupt audio playback
        # Only interrupt if we've detected 1+ seconds of continuous speech
        if not self.audio_player.playback_interrupted and is_speech:
            # Calculate duration of continuous speech
            speech_duration = len(recording_buffer) * self.audio_recorder.chunk_size / self.audio_recorder.sample_rate
            if speech_duration >= 1.0:  # 1 second threshold
                if self.audio_player.interrupt():
                    print("Interrupted ongoing audio playback due to sustained speech")
        
        if not is_speech:
            if silence_start is None:
                silence_start = time.time()
            elif time.time() - silence_start >= self.silence_threshold:
                # End of utterance - silence threshold reached
                return recording_buffer, silence_start, True  # finished_recording
        else:
            # Reset silence timer if speech detected
            silence_start = None
            
        return recording_buffer, silence_start, False
    
    def _process_complete_utterance(self, recording_buffer: list):
        """
        Process a complete utterance after recording is finished
        """
        print("Finished recording due to silence")
        self.user_speaking = False  # Clear flag when user stops speaking
        
        # Check and update session context
        self.session_manager.check_and_update_session("")

        # Update last user activity time
        self.session_manager.update_activity_time()
        
        # Process the recorded audio
        if len(recording_buffer) > 0:
            # Convert to bytes
            audio_data = b''.join(recording_buffer)
            
            # Speaker verification
            if not self.speaker_verification.verify(audio_data):
                print("Speaker verification failed. Skipping further processing.")
                return
            
            # Save to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                temp_filename = tmp_file.name
            
            try:
                # Write audio data to temporary WAV file
                with wave.open(temp_filename, 'wb') as wf:
                    wf.setnchannels(1)  # Mono
                    wf.setsampwidth(2)  # 16 bits
                    wf.setframerate(self.audio_recorder.sample_rate)
                    wf.writeframes(audio_data)
                
                # Transcribe using ASR
                text = self.asr.transcribe(audio_data)
                print(f"Recognized: {text}")
                
                # Process in a separate task to avoid blocking
                if self.event_loop:
                    asyncio.run_coroutine_threadsafe(
                        self.process_user_input(text), 
                        self.event_loop
                    )
            finally:
                # Clean up temporary file
                if os.path.exists(temp_filename):
                    os.unlink(temp_filename)
    
    def record_audio(self):
        """
        Record audio with VAD and silence detection
        """
        # Initialize audio stream
        p, stream = self.audio_recorder.initialize_audio_stream()
        print("Listening... Press Ctrl+C to stop")
        
        # Recording state variables
        recording_buffer = []
        is_recording = False
        silence_start = None
        stream_open = True
        
        try:
            while self.recording:
                # Read audio chunk
                data = self.audio_recorder.read_audio_chunk(stream)
                if data is None:
                    continue  # Skip this chunk due to overflow
                
                # Check for speech
                is_speech = self.audio_recorder.vad.is_speech(data)
                
                if not is_recording and is_speech:
                    # Start recording when speech is detected
                    is_recording = True
                    recording_buffer, silence_start = self._start_recording(data)
                
                elif is_recording:
                    # Process audio chunk during recording
                    recording_buffer, silence_start, finished = self._process_audio_chunk(
                        data, recording_buffer, silence_start
                    )
                    
                    if finished:
                        # Process complete utterance
                        self._process_complete_utterance(recording_buffer)
                        
                        # Reset recording state
                        is_recording = False
                        recording_buffer = []
                        silence_start = None
                        
        except KeyboardInterrupt:
            print("Recording stopped")
        except Exception as e:
            print(f"Unexpected error in record_audio: {e}")
        finally:
            # Clean up audio resources
            self.audio_recorder.cleanup_audio_stream(p, stream, stream_open)
    
    async def process_user_input(self, text: str):
        """
        Process user input through the pipeline
        """
        if self.processing:
            return
        
        self.processing = True
        
        try:
            # Process with LLM
            llm_response = await self.process_text_with_llm(text)
            print_timestamp_debug_log(f"LLM Response: {llm_response}")
            
            # Convert to speech and play
            await self.text_to_speech_and_play(llm_response)
            # Update session activity time
            print_timestamp_debug_log("Speech done, updating session activity time...")
            self.session_manager.update_activity_time()
        except Exception as e:
            print(f"Error processing user input: {e}")
        finally:
            self.processing = False
    
    def run_agent(self):
        """
        Start and run the voice chat agent
        """
        self.recording = True
        # Store reference to the event loop
        self.event_loop = asyncio.get_event_loop()
        # Start recording in a separate thread
        recording_thread = threading.Thread(target=self.record_audio)
        recording_thread.start()
        
        try:
            # Run the asyncio event loop in the main thread
            asyncio.get_event_loop().run_until_complete(self._agent_wait_loop())
        except KeyboardInterrupt:
            print("Stopping agent...")
        finally:
            self.recording = False
            recording_thread.join()
    
    async def _agent_wait_loop(self):
        """
        Agent wait loop, async sleeping
        """
        # This is a placeholder for any async tasks that need to run
        while self.recording:
            await asyncio.sleep(0.1)
    
    async def text_to_speech_and_play(self, text: str):
        """
        Convert text to speech and play it with streaming
        """
        try:
            # Apply text guardrail to LLM output before TTS
            is_valid, message, cleaned_text = self.text_guardrail.validate_and_clean(text)
            
            # If text is not valid, inform the user
            if not is_valid:
                print(f"Text Guardrail Warning: {message}")
                # Use the warning message for TTS instead
                text_to_speak = message
            else:
                # Use the cleaned text for TTS
                text_to_speak = cleaned_text
                print(f"Text Guardrail: {message}")
            
            # Detect language and select appropriate voice
            language = self._detect_language(text_to_speak)
            
            if language == "en":
                voice = "en-GB-SoniaNeural"
            else:  # Default to Chinese
                voice = "zh-CN-XiaoxiaoNeural"
            
            # Use edge-tts for streaming audio generation
            communicate = edge_tts.Communicate(text_to_speak, voice)
            
            print_timestamp_debug_log(f"TTS Generating audio...")
            # Stream audio and play in chunks
            audio_stream = AudioStreamBuffer(min_chunk_size=3200)  # ~200ms minimum
            
            # Start playing as soon as we have enough data
            play_task = asyncio.create_task(
                self.audio_player.play_stream(audio_stream)
            )
            
            # Feed audio data to the stream
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    await audio_stream.write(chunk["data"])
                    
            # Mark end of stream
            await audio_stream.finish()
            
            # Wait for playback to complete
            await play_task
            
        except Exception as e:
            print(f"TTS or playback error: {e}")
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text (simplified approach)"""
        # Count Chinese characters
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        # Count English letters
        english_chars = len([c for c in text if 'a' <= c.lower() <= 'z'])
        
        return "en" if english_chars > chinese_chars else "zh"