class ChatbotDomainError(Exception):
    """Base exception for all domain-related errors in the chatbot."""


class UnsafeSQLError(ChatbotDomainError):
    """Raised when a SQL query contains forbidden or unsafe operations."""


class LLMGenerationError(ChatbotDomainError):
    """Raised when the language model fails to generate a valid SQL query or response."""
