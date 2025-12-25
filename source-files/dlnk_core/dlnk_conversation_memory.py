
"""
This module provides a Conversation Memory system for the dLNk Production.
"""

import logging
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KnowledgeBase:
    """Manages a simple file-based knowledge base."""

    def __init__(self, storage_path: str = "/home/ubuntu/conversation_memory/knowledge_base"):
        """Initializes the KnowledgeBase.

        Args:
            storage_path (str, optional): The directory to store knowledge base files. 
                                      Defaults to "/home/ubuntu/conversation_memory/knowledge_base".
        """
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)

    def add_entry(self, key: str, value: str):
        """Adds an entry to the knowledge base.

        Args:
            key (str): The key for the knowledge entry.
            value (str): The value of the knowledge entry.
        """
        if not isinstance(key, str) or not key:
            raise ValueError("key must be a non-empty string.")
        if not isinstance(value, str):
            raise ValueError("value must be a string.")

        entry_file = os.path.join(self.storage_path, f"{key}.json")
        try:
            with open(entry_file, "w", encoding="utf-8") as f:
                json.dump({"key": key, "value": value}, f, indent=4)
            logging.info(f"Added knowledge base entry for key: {key}")
        except IOError as e:
            logging.error(f"Error adding knowledge base entry for key {key}: {e}")

    def get_entry(self, key: str) -> str | None:
        """Retrieves an entry from the knowledge base.

        Args:
            key (str): The key of the knowledge entry to retrieve.

        Returns:
            str | None: The value of the knowledge entry, or None if not found.
        """
        entry_file = os.path.join(self.storage_path, f"{key}.json")
        if os.path.exists(entry_file):
            try:
                with open(entry_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("value")
            except (IOError, json.JSONDecodeError) as e:
                logging.error(f"Error retrieving knowledge base entry for key {key}: {e}")
        return None

    def search(self, query: str) -> list[dict]:
        """Searches the knowledge base for relevant entries.

        Args:
            query (str): The search query.

        Returns:
            list[dict]: A list of matching knowledge base entries.
        """
        results = []
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                entry_file = os.path.join(self.storage_path, filename)
                try:
                    with open(entry_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if query.lower() in data.get("value", "").lower() or query.lower() in data.get("key", "").lower():
                            results.append(data)
                except (IOError, json.JSONDecodeError) as e:
                    logging.error(f"Error searching knowledge base file {filename}: {e}")
        return results

class ConversationMemory:
    '''Manages conversation history and context for an AI.

    This class handles session persistence, context window management, and provides
    a foundation for long-term memory and knowledge base integration.
    '''

    def __init__(self, session_id: str, max_tokens: int = 4096, storage_path: str = "/home/ubuntu/conversation_memory/sessions", knowledge_base_path: str = "/home/ubuntu/conversation_memory/knowledge_base"):
        '''Initializes the ConversationMemory.

        Args:
            session_id (str): The unique identifier for the conversation session.
            max_tokens (int, optional): The maximum number of tokens in the context window. Defaults to 4096.
            storage_path (str, optional): The directory to store session files. Defaults to "/home/ubuntu/conversation_memory/sessions".
            knowledge_base_path (str, optional): The directory for the knowledge base. Defaults to "/home/ubuntu/conversation_memory/knowledge_base".
        '''
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("session_id must be a non-empty string.")
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            raise ValueError("max_tokens must be a positive integer.")

        self.session_id = session_id
        self.max_tokens = max_tokens
        self.storage_path = storage_path
        self.history = []
        self.knowledge_base = KnowledgeBase(storage_path=knowledge_base_path)

        os.makedirs(self.storage_path, exist_ok=True)
        self.load_session()

    def add_message(self, role: str, content: str):
        '''Adds a message to the conversation history.

        Args:
            role (str): The role of the speaker (e.g., "user", "assistant").
            content (str): The content of the message.
        '''
        if not isinstance(role, str) or not role:
            raise ValueError("role must be a non-empty string.")
        if not isinstance(content, str):
            raise ValueError("content must be a string.")

        timestamp = datetime.utcnow().isoformat()
        message = {"role": role, "content": content, "timestamp": timestamp}
        self.history.append(message)
        logging.info(f"Added message for session {self.session_id}: {message}")
        self._trim_context()
        self.save_session()

    def get_context(self, query: str | None = None) -> list[dict]:
        '''Retrieves the current conversation context, optionally augmented with knowledge base search results.

        Args:
            query (str | None, optional): A query to search the knowledge base. Defaults to None.

        Returns:
            list[dict]: A list of messages within the context window.
        '''
        context = self.history
        if query:
            kb_results = self.knowledge_base.search(query)
            if kb_results:
                kb_content = " ".join([res['value'] for res in kb_results])
                context.insert(0, {"role": "system", "content": f"Knowledge base results for '{query}': {kb_content}"})

        return context

    def _trim_context(self):
        '''Trims the conversation history to fit within the max_tokens limit.'''
        total_tokens = sum(len(message["content"].split()) for message in self.history)
        while total_tokens > self.max_tokens and len(self.history) > 1:
            removed_message = self.history.pop(0)
            total_tokens -= len(removed_message["content"].split())
            logging.info(f"Trimmed message from session {self.session_id} to manage context window.")

    def clear(self):
        '''Clears the conversation history for the current session.'''
        self.history = []
        self.save_session()
        logging.info(f"Cleared conversation history for session {self.session_id}.")

    def save_session(self):
        '''Saves the current conversation session to a file.'''
        session_file = os.path.join(self.storage_path, f"{self.session_id}.json")
        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4)
            logging.info(f"Session {self.session_id} saved to {session_file}")
        except IOError as e:
            logging.error(f"Error saving session {self.session_id} to {session_file}: {e}")

    def load_session(self):
        '''Loads a conversation session from a file.'''
        session_file = os.path.join(self.storage_path, f"{self.session_id}.json")
        if os.path.exists(session_file):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
                logging.info(f"Session {self.session_id} loaded from {session_file}")
            except (IOError, json.JSONDecodeError) as e:
                logging.error(f"Error loading session {self.session_id} from {session_file}: {e}")
                self.history = [] # Keep history empty if loading fails

    def summarize_and_store(self, summary_key: str):
        '''Summarizes the conversation and stores it in the knowledge base.

        Args:
            summary_key (str): The key to store the summary under.
        '''
        summary = " ".join([msg['content'] for msg in self.history])
        self.knowledge_base.add_entry(summary_key, summary)
        logging.info(f"Stored conversation summary for session {self.session_id} with key {summary_key}")
