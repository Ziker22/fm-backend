"""
Test script to verify that the OpenAIClient's get_websearch_response function works correctly.

This script creates an instance of the OpenAIClient and calls the get_websearch_response
function with a simple prompt. It then prints the response to verify that the function
works as expected.

Note: This script requires the openai package to be installed and the OPENAI_API_KEY
environment variable to be set.
"""
from ai.utils import OpenAIClient

def test_websearch():
    """
    Test the get_websearch_response function of the OpenAIClient.
    """
    try:
        # Initialize the OpenAI client
        client = OpenAIClient(
            model="gpt-4-turbo",  # Using a model that supports web search
            temperature=0.7
        )
        
        # Simple prompt for testing
        prompt = "What is the current weather in Bratislava, Slovakia?"
        
        print(f"Testing get_websearch_response with prompt: '{prompt}'")
        
        # Call the get_websearch_response function
        response = client.get_websearch_response(prompt)
        
        # Print the response content
        print("\nResponse content:")
        print(response['content'])
        
        # Print the number of citations
        print(f"\nNumber of citations: {len(response['citations'])}")
        
        # Print the first citation if available
        if response['citations']:
            print("\nFirst citation:")
            citation = response['citations'][0]
            print(f"Title: {citation['title']}")
            print(f"URL: {citation['url']}")
            print(f"Snippet: {citation['snippet'][:100]}...")
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nError during test: {e}")
        print("This might be because:")
        print("1. The openai package is not installed")
        print("2. The OPENAI_API_KEY environment variable is not set")
        print("3. Web search is not available for your OpenAI account or API key")
        print("4. The model specified does not support web search")
        return False

if __name__ == "__main__":
    test_websearch()