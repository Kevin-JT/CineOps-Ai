from enum import Enum


class Environment(str, Enum):
    """
    Standard environments for the application.
    """

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
