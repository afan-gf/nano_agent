from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from utils.logger import print_timestamp_debug_log

class LLM:
    """
    Large Language Model using Qwen-plus API
    """
    def __init__(self, config: Dict[str, Any]):
        self.client = AsyncOpenAI(
            api_key=config.get("llm_api_key", ""),
            base_url=config.get("llm_base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        )
        self.model = config.get("llm_model", "qwen-plus")
        # System message to be included in all conversations
        self.system_message = {
            "role": "system", 
            "content": config.get("llm_system_prompt", "你是 小白, 人工智能助手。提供有用的回复，回复精简不超过200个字。")
        }
    
    async def generate(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        # Add system message at the beginning of the conversation
        messages_with_system = [self.system_message] + messages
        
        params = {
            "model": self.model,
            "messages": messages_with_system,
            "temperature": 0.7,
            "max_tokens": 512,
            "extra_body": {"enable_thinking": False, "enable_search": True},
        }
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        
        #print_timestamp_debug_log(f"----prompt: {params}")
        response = await self.client.chat.completions.create(**params)
        #print_timestamp_debug_log(f"----response: {response.choices[0].message}")
        return response.choices[0].message