import os
import logging
import json
from datetime import datetime

class AIParser:
    """
    Parser that uses LLMs (OpenAI/Gemini) to extract structured data from unstructured text/HTML.
    """
    
    def __init__(self, provider="openai", model="gpt-4o"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.provider = provider
        self.model = model
        self.client = None
        self.api_key = None

        self._setup_client()

    def _setup_client(self):
        """Initialize the AI client"""
        if self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if self.api_key:
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=self.api_key)
                except ImportError:
                    self.logger.warning("openai package not installed. AI parsing disabled.")
            else:
                self.logger.warning("OPENAI_API_KEY not found. AI parsing disabled.")
        
        elif self.provider == "gemini":
            self.api_key = os.getenv("GOOGLE_API_KEY")
            if self.api_key:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.api_key)
                    self.client = genai.GenerativeModel('gemini-1.5-pro')
                except ImportError:
                    self.logger.warning("google-generativeai package not installed. AI parsing disabled.")
            else:
                 self.logger.warning("GOOGLE_API_KEY not found. AI parsing disabled.")

    def parse_notification(self, text_content: str) -> dict:
        """
        Extract Exam Notification details from text using LLM.
        """
        if not self.client:
            return None

        prompt = f"""
        Extract the following details from the text below in valid JSON format.
        If a field is not found, use null.
        
        Fields:
        - exam_name (string)
        - organization (string)
        - notification_date (YYYY-MM-DD)
        - application_start (YYYY-MM-DD or null)
        - application_end (YYYY-MM-DD or null)
        - exam_date (YYYY-MM-DD or null)
        - total_vacancies (integer or null)
        - official_link (string or null)
        
        Text Content:
        {text_content[:4000]}  # Limit context window
        """

        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that extracts structured data from exam notifications."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                return json.loads(content)
            
            elif self.provider == "gemini":
                response = self.client.generate_content(prompt)
                # Naive JSON extraction for Gemini (it sometimes wraps in markdown)
                content = response.text.replace('```json', '').replace('```', '').strip()
                return json.loads(content)

        except Exception as e:
            self.logger.error(f"AI Parsing failed: {e}")
            return None
