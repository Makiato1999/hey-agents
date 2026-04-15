import os
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class HeyAgentsLLM:
    """
    LLM client
    """

    def __init__(
        self,
        model: str = None,
        apiKey: str = None,
        baseUrl: str = None,
        timeout: int = None,
    ):
        self.model = model or os.getenv("LLM_MODEL_ID")
        self.apiKey = apiKey or os.getenv("LLM_API_KEY")
        self.baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        self.timeout = timeout or os.getenv("LLM_TIMEOUT")

        if not all([self.model, self.apiKey, self.baseUrl]):
            raise ValueError("The model ID, API key, and service URL must be provided or defined in the .env file.")

        self.client = OpenAI(
            api_key=self.apiKey, base_url=self.baseUrl  # 换成你在 AiHubMix 生成的密钥
        )

    def think(self, messages: List[Dict[str, str]], temperature: float = 0) -> str:
        print(f"Calling the {self.model} model...")
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=temperature
            )
            collected_content = response.choices[0].message.content
            return "".join(collected_content)
        except Exception as e:
            print(f"An error occurred while calling the LLM API: {e}.")
            return None

if __name__ == '__main__':
    try:
        llmClient = HeyAgentsLLM()
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        print("--- Calling LLM ---")
        response_text = llmClient.think(messages)
        if response_text:
            print("\n\n--- Full model response ---")
            print(response_text)
    except ValueError as e:
        print(e)
