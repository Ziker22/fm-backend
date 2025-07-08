"""
Example usage of the OpenAIClient class.

This module demonstrates how to use the OpenAIClient class to generate
chat completions using OpenAI's API, including web search capabilities.

Before running this example, make sure to:
1. Install the openai package: pip install openai
2. Set the OPENAI_API_KEY environment variable in your .env file
"""
from ai.open_ai_client import OpenAIClient


def simple_chat_example():
    """
    A simple example of using the OpenAIClient to generate a chat completion.
    """
    try:
        # Initialize the OpenAI client with default model and temperature
        client = OpenAIClient()

        # Generate a simple chat completion
        prompt = "Tell me a short joke about programming"
        response = client.get_chat_completion(prompt)

        print(f"Prompt: {prompt}")
        print(f"Response: {response}")

    except ValueError as e:
        print(f"Error: {e}")
        print("Make sure you have set the OPENAI_API_KEY environment variable in your .env file.")


def advanced_chat_example():
    """
    A more advanced example showing different parameters of the OpenAIClient.
    """
    try:
        # Initialize the OpenAI client with custom model and temperature
        client = OpenAIClient(
            model="gpt-4",  # Using a more advanced model
            temperature=0.3  # Lower temperature for more deterministic responses
        )

        # Generate a chat completion with system message
        prompt = "Explain the concept of recursion"
        system_message = "You are a computer science professor explaining concepts to beginners."

        response = client.get_chat_completion(
            prompt=prompt,
            system_message=system_message  # Set the context
        )

        print(f"Prompt: {prompt}")
        print(f"System Message: {system_message}")
        print(f"Response: {response}")

    except ValueError as e:
        print(f"Error: {e}")
        print("Make sure you have set the OPENAI_API_KEY environment variable in your .env file.")


def websearch_example():
    """
    An example of using the OpenAIClient to generate a chat completion with web search.

    This example demonstrates how to use the get_websearch_response method to get
    information from the web as part of the response.
    """
    try:
        # Initialize the OpenAI client
        client = OpenAIClient(
            model="gpt-4-turbo",  # Using a model that supports web search
            temperature=0.5
        )

        # Generate a chat completion with web search
        prompt = "What are the latest developments in quantum computing in 2024?"
        system_message = "You are a helpful assistant that provides accurate and up-to-date information."

        response = client.get_websearch_response(
            prompt=prompt,
            system_message=system_message,
            search_count=5  # Get 5 search results
        )

        print(f"Prompt: {prompt}")
        print(f"System Message: {system_message}")
        print(f"Response Content: {response['content']}")

        # Print citations if available
        if response['citations']:
            print("\nCitations:")
            for i, citation in enumerate(response['citations'], 1):
                print(f"{i}. {citation['title']}")
                print(f"   URL: {citation['url']}")
                print(f"   Snippet: {citation['snippet'][:100]}...")
        else:
            print("\nNo citations available.")

    except ValueError as e:
        print(f"Error: {e}")
        print("Make sure you have set the OPENAI_API_KEY environment variable in your .env file.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("This might be because web search is not available for your OpenAI account or API key.")


if __name__ == "__main__":
    print("Running simple chat example:")
    simple_chat_example()

    print("\nRunning advanced chat example:")
    advanced_chat_example()

    print("\nRunning web search example:")
    websearch_example()
