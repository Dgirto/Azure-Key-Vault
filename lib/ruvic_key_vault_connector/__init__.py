"""Conector Ruvic de lectura de secretos, llaves y certificados en Azure Key Vault."""

from .client import KeyVaultClient
from .config import ENV_PREFIX, KeyVaultConfig
from .exceptions import (
    KeyVaultAuthError,
    KeyVaultConnectorError,
    KeyVaultDataError,
    KeyVaultNetworkError,
)
from .logging_utils import setup_logging

__all__ = [
    "ENV_PREFIX",
    "KeyVaultAuthError",
    "KeyVaultClient",
    "KeyVaultConfig",
    "KeyVaultConnectorError",
    "KeyVaultDataError",
    "KeyVaultNetworkError",
    "setup_logging",
]

__version__ = "1.0.0"
