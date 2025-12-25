'''
This module implements a multi-layered AI fallback system designed for production use.

It provides a robust and resilient way to interact with multiple AI providers,
ensuring high availability and graceful degradation of service in case of failures.
The system is designed to be easily integrated into existing applications.
'''

import logging
import os
import requests

# Configure logging for the module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

class AIFallbackSystem:
    '''
    A multi-layered AI fallback system that sequentially tries different AI providers.

    The system is designed with a layered approach to ensure that if one service
    fails, it automatically switches to the next one in the predefined order:
    1. Primary Jetski Service
    2. Secondary OpenAI-compatible Service
    3. Tertiary Local LLM Service
    4. Offline Mode (as a last resort)
    '''

    def __init__(self, openai_api_key: str = None, openai_base_url: str = None, jetski_api_endpoint: str = None, local_llm_endpoint: str = None):
        '''
        Initializes the AI Fallback System with configurations for the different services.

        Args:
            openai_api_key (str, optional): API key for the OpenAI-compatible service.
                                             If not provided, it will be read from the `OPENAI_API_KEY` environment variable.
            openai_base_url (str, optional): Base URL for the OpenAI-compatible service.
            jetski_api_endpoint (str, optional): The API endpoint for the Primary Jetski service.
            local_llm_endpoint (str, optional): The API endpoint for the Tertiary Local LLM service.
        '''
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.openai_base_url = openai_base_url
        self.jetski_api_endpoint = jetski_api_endpoint
        self.local_llm_endpoint = local_llm_endpoint

        self.providers = [
            {"name": "Primary Jetski", "method": self._call_jetski},
            {"name": "Secondary OpenAI-compatible", "method": self._call_openai_compatible},
            {"name": "Tertiary Local LLM", "method": self._call_local_llm},
        ]

    def generate_response(self, prompt: str) -> str:
        '''
        Generates a response from the AI system by trying each provider in sequence.

        This is the main entry point for the system. It iterates through the configured
        AI providers and attempts to get a response. If all providers fail, it returns
        a default offline message.

        Args:
            prompt (str): The prompt to send to the AI.

        Returns:
            str: The AI-generated response, or a default message if all services fail.
        '''
        for provider in self.providers:
            try:
                logger.info(f"Attempting to generate response from {provider['name']}...")
                response = provider["method"](prompt)
                if response:
                    logger.info(f"Successfully received response from {provider['name']}.")
                    return response
            except Exception as e:
                logger.error(f"{provider['name']} failed: {e}", exc_info=True)

        logger.warning("All AI providers failed. Falling back to offline mode.")
        return self._offline_mode()

    def _call_jetski(self, prompt: str) -> str:
        '''
        Calls the Primary Jetski service.

        This is a placeholder for the actual Jetski API call. In a real-world scenario,
        this method would contain the logic to send a request to the Jetski API
        and handle its response.

        Args:
            prompt (str): The prompt to send to Jetski.

        Returns:
            str: The response from Jetski, or None if the endpoint is not configured.

        Raises:
            ConnectionError: If the Jetski service is not configured or fails to connect.
        '''
        if not self.jetski_api_endpoint:
            logger.warning("Jetski API endpoint is not configured.")
            return None
        # In a real implementation, you would make an API call here.
        # For demonstration, we simulate a failure.
        raise ConnectionError("Failed to connect to Jetski service at " + self.jetski_api_endpoint)

    def _call_openai_compatible(self, prompt: str) -> str:
        '''
        Calls a secondary OpenAI-compatible service.

        This method sends a request to an AI service that is compatible with the OpenAI API.
        It requires an API key and a base URL to be configured.

        Args:
            prompt (str): The prompt to send to the service.

        Returns:
            str: The content of the AI's response message.

        Raises:
            ValueError: If the OpenAI API key or base URL are not provided.
            requests.exceptions.RequestException: For network-related errors.
            KeyError: If the response from the API is not in the expected format.
        '''
        if not self.openai_api_key or not self.openai_base_url:
            raise ValueError("OpenAI API key and base URL must be provided for the secondary service.")

        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "gemini-2.5-flash",
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(f"{self.openai_base_url}/chat/completions", headers=headers, json=data, timeout=30)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while calling OpenAI-compatible service: {e}")
            raise
        except KeyError as e:
            logger.error(f"Unexpected response format from OpenAI-compatible service: {e}")
            raise

    def _call_local_llm(self, prompt: str) -> str:
        '''
        Calls the Tertiary Local LLM service.

        This is a placeholder for an API call to a locally hosted Large Language Model.
        You would replace the implementation with the actual client code for your local LLM.

        Args:
            prompt (str): The prompt to send to the local LLM.

        Returns:
            str: The response from the local LLM, or None if the endpoint is not configured.

        Raises:
            ConnectionError: If the local LLM service is not configured or fails to connect.
        '''
        if not self.local_llm_endpoint:
            logger.warning("Local LLM endpoint is not configured.")
            return None
        # In a real implementation, you would make an API call here.
        # For demonstration, we simulate a failure.
        raise ConnectionError("Failed to connect to Local LLM service at " + self.local_llm_endpoint)

    def _offline_mode(self) -> str:
        '''
        Provides a default, canned response when all online AI services are unavailable.

        Returns:
            str: A static offline message.
        '''
        return "The AI system is currently unavailable. Please try again later."

if __name__ == '__main__':
    # Example of how to use the AIFallbackSystem.
    # To run this example, you must have an OpenAI-compatible API key.
    # Set it as an environment variable: export OPENAI_API_KEY='your_api_key_here'

    logger.info("Starting AI Fallback System demonstration.")

    # Initialize the system. For this example, we will only configure the
    # OpenAI-compatible service, so we expect the Jetski call to be skipped
    # and the OpenAI call to be attempted.
    # We will use the pre-configured base URL for the OpenAI-compatible API.
    fallback_system = AIFallbackSystem(
        openai_base_url="https://api.openai.com/v1",
        jetski_api_endpoint="http://localhost:8080/api/generate" # Example endpoint
    )

    # The user's prompt to the AI.
    user_prompt = "Explain the importance of a fallback system in 30 words."

    # Generate a response using the fallback system.
    logger.info(f"Sending prompt: '{user_prompt}'")
    ai_response = fallback_system.generate_response(user_prompt)

    # Print the final response from the AI.
    print("\n" + "="*50)
    print(f"Final AI Response: {ai_response}")
    print("="*50 + "\n")

    # --- Example with simulated failure of all online services ---
    logger.info("Demonstrating full fallback to offline mode.")
    failing_system = AIFallbackSystem(
        openai_base_url="http://localhost:12345", # A non-existent URL to simulate failure
        jetski_api_endpoint="http://localhost:8080/api/generate",
        local_llm_endpoint="http://localhost:11434/api/generate"
    )
    offline_response = failing_system.generate_response(user_prompt)

    print("\n" + "="*50)
    print(f"Offline Fallback Response: {offline_response}")
    print("="*50 + "\n")
