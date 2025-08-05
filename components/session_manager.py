import time
import uuid
from typing import Dict, Any
from .memory import WorkMemory

class SessionManager:
    """
    Session management for conversation context
    """
    def __init__(self, memory: WorkMemory, config: Dict[str, Any]):
        self.memory = memory
        self.session_timeout = config.get("session_timeout", 20.0)
        self.session_id = str(uuid.uuid4())  # Create initial session
        self.last_user_activity = time.time()
        
        # Phrases that indicate end of session
        self.end_phrases = config.get("session_end_phrases", [
            "再见", "拜拜", "bye", "goodbye", "结束对话", "结束聊天", 
            "就聊到这里", "下次再聊", "回聊", "结束了", "聊完了"
        ])
    
    def should_end_session(self, user_text: str) -> bool:
        """
        Check if user text indicates end of session
        """
        # Check if any end phrase is in the user text
        for phrase in self.end_phrases:
            if phrase in user_text:
                return True
        return False
    
    def check_and_update_session(self, user_text: str = None) -> str:
        """
        Check if session should be ended and create new one if needed
        Returns the current session ID
        """
        current_time = time.time()
        
        # Check if user explicitly wants to end session
        if user_text and self.should_end_session(user_text):
            print("User requested to end session")
            old_session_id = self.session_id
            self.session_id = self.memory.create_new_session()
            print(f"Ended session {old_session_id}, created new session {self.session_id}")
            return self.session_id
        
        # Check if session timed out due to inactivity
        if current_time - self.last_user_activity > self.session_timeout:
            print("Session timed out due to inactivity")
            old_session_id = self.session_id
            self.session_id = self.memory.create_new_session()
            print(f"Ended session {old_session_id} due to timeout, created new session {self.session_id}")
            return self.session_id
        
        # Update last activity time
        self.last_user_activity = current_time
        return self.session_id
    
    def update_activity_time(self):
        """
        Update the last user activity time
        """
        self.last_user_activity = time.time()