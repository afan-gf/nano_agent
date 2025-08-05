import time
import uuid
from typing import List, Dict, Any, Optional

class WorkMemory:
    """
    Memory management for conversation history
    """
    def __init__(self, config: Dict[str, Any]):
        self.max_turns = config.get("memory_max_turns", 100)
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self.session_timestamps: Dict[str, float] = {}  # Track last activity time for each session
    
    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append({
            "role": role,
            "content": content
        })
        
        # Update session timestamp
        self.session_timestamps[session_id] = time.time()
        
        # Keep only the last max_turns messages
        if len(self.sessions[session_id]) > self.max_turns * 2:  # *2 for user + assistant pairs
            self.sessions[session_id] = self.sessions[session_id][-self.max_turns*2:]
    
    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self.sessions.get(session_id, [])
    
    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.session_timestamps:
            del self.session_timestamps[session_id]
    
    def get_session_timestamp(self, session_id: str) -> Optional[float]:
        return self.session_timestamps.get(session_id)
    
    def create_new_session(self) -> str:
        new_session_id = str(uuid.uuid4())
        self.session_timestamps[new_session_id] = time.time()
        return new_session_id