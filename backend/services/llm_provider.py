import os
import json
import ollama
from tenacity import retry, stop_after_attempt, wait_fixed
from backend.utils.logger import logger

class OllamaService:
    def __init__(self):
        # Default to 'mistral' if not set in .env
        self.model = os.getenv("OLLAMA_MODEL", "mistral")
        
        # Check connection immediately on startup
        try:
            ollama.list()
            logger.info(f"✅ Connected to Local Ollama (Model: {self.model})")
        except Exception:
            logger.critical("❌ Could not connect to Ollama! Is it running?")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def analyze_text(self, text: str) -> dict:
        """
        Sends text to local LLM and forces a JSON response.
        """
        prompt = f"""
        You are an API that outputs strictly valid JSON.
        Analyze this text:
        "{text}"

        Return JSON matching this schema exactly:
        {{
            "sentiment": "positive" | "neutral" | "negative",
            "sentiment_score": 0.5,
            "summary": "One sentence summary.",
            "topics": ["topic1", "topic2"],
            "intent": "informational" | "complaint",
            "entities": [{{"text": "EntityName", "label": "ORG"}}]
        }}
        """

        try:
            logger.info("🧠 Processing locally with Ollama...")
            
            # We use format='json' to force structured output
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                format='json', 
            )

            response_text = response['message']['content']
            
            # Parse the JSON string
            return json.loads(response_text)

        except json.JSONDecodeError:
            logger.error(f"❌ LLM produced invalid JSON: {response_text}")
            # Fallback for bad JSON
            return {
                "sentiment": "neutral", 
                "sentiment_score": 0.0,
                "summary": "Error: Model produced invalid JSON format.",
                "topics": [],
                "intent": "unknown",
                "entities": []
            }
        except Exception as e:
            logger.error(f"❌ Ollama Error: {e}")
            raise es