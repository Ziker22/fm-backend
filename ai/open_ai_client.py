"""
Utility functions and classes for the AI app.
This module contains utilities for interacting with AI services.
"""
import os
import re
from typing import Optional, List, Dict, Any

from openai import OpenAI


class OpenAIClient:
    """
    A client for interacting with the OpenAI API.

    This class provides methods for generating chat completions using OpenAI's API,
    including web search capabilities for retrieving up-to-date information.
    It reads the API key from the environment variables.

    Usage:
        # Basic chat completion
        client = OpenAIClient(model="gpt-4", temperature=0.5)
        response = client.get_chat_completion("Tell me a joke")

        # Web search enabled completion
        client = OpenAIClient(model="gpt-4-turbo")
        result = client.get_websearch_response("What are the latest developments in AI?")
        content = result['content']
        citations = result['citations']
    """

    def __init__(self, model: str = "gpt-4.1-mini-2025-04-14", temperature: float = 0.3):
        """
        Initialize the OpenAI client with the API key from environment variables.

        Args:
            model: The OpenAI model to use (default: gpt-3.5-turbo)
            temperature: Controls randomness (0-1, lower is more deterministic)
        """
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.country = "SK"

    def __get_json_string_from_completion(self, completion: str | None):
        if completion is None:
            return None

        split_completion = completion.split("</think>")
        without_thinking = split_completion[-1] if "<think>" in completion else completion
        cleaned = (
            re.sub(r"^```json\s*|\s*```$", "", without_thinking.strip())
            if "json" in without_thinking
            else without_thinking.strip()
        )
        return cleaned


    def get_chat_completion(
        self, 
        prompt: str, 
        system_message: Optional[str] = None
    ) -> str:
        """
        Generate a chat completion using OpenAI's API.

        Args:
            prompt: The user's input prompt
            system_message: Optional system message to set context

        Returns:
            The generated text response
        """
        messages = []

        # Add system message if provided
        if system_message:
            messages.append({"role": "system", "content": system_message})

        # Add user message
        messages.append({"role": "user", "content": prompt})

        # Create completion
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature
        )

        # Return the generated text
        return response.choices[0].message.content

    def get_websearch_response(
        self,
        prompt: str,
        is_json_reponse: bool = True,
    ) -> Dict[str, Any]:

        response =  self.client.responses.create(
            model=self.model,
            tools=[{"type": "web_search_preview"}],
            input=prompt,
            temperature=self.temperature
        )
        return response.output_text if not is_json_reponse else self.__get_json_string_from_completion(response.output_text)
