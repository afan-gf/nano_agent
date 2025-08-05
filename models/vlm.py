import base64
from typing import Dict, Any
from openai import AsyncOpenAI
from datetime import datetime
from utils.logger import print_timestamp_debug_log

class VLM:
    """
    Vision Language Model using Qwen-vl-plus via OpenAI API
    """
    def __init__(self, config: Dict[str, Any]):
        self.client = AsyncOpenAI(
            api_key=config.get("vlm_api_key", ""),
            base_url=config.get("vlm_base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        )
        self.model = config.get("vlm_model", "qwen-vl-plus")
        self.max_tokens = config.get("vlm_max_tokens", 1500)
    
    async def analyze(self, image_path: str, prompt: str) -> str:
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Create messages in the format expected by the OpenAI API
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
        #print_timestamp_debug_log(f"---VLM prompt:{prompt}")
        # Call the model using the OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens
        )
        #print_timestamp_debug_log(f"---VLM response:{response.choices[0].message.content}")
        return response.choices[0].message.content