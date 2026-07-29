"""
Custom exception hierarchy for the CineOps AI application.
"""


class CineOpsError(Exception):
    """
    Base exception for all custom errors in CineOps AI.
    """


class ConfigurationError(CineOpsError):
    """
    Raised when there is an issue with the application configuration.
    """


class ProviderError(CineOpsError):
    """
    Raised when an external provider (e.g., API) fails.
    """


class RepositoryError(CineOpsError):
    """
    Raised when a storage repository operation fails.
    """


class ValidationError(CineOpsError):
    """
    Raised when data validation fails.
    """
