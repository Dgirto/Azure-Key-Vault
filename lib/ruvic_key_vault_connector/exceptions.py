"""Excepciones propias del conector Azure Key Vault.

Separan los tres tipos de fallo que el usuario debe distinguir:
autenticación, red/servidor y datos. Nunca exponemos excepciones
crípticas del SDK subyacente.
"""


class KeyVaultConnectorError(Exception):
    """Error base del conector."""


class KeyVaultAuthError(KeyVaultConnectorError):
    """Credenciales inválidas o permisos insuficientes (RBAC/access policy)."""


class KeyVaultNetworkError(KeyVaultConnectorError):
    """No se pudo alcanzar el Key Vault (red/timeout)."""


class KeyVaultDataError(KeyVaultConnectorError):
    """La operación es válida pero el secreto/certificado es inválido."""
