"""Prueba de conexión estándar del conector key_vault.

Firma estándar Ruvic: def test_connection() -> tuple[bool, str]
- Lee la configuración EXCLUSIVAMENTE de las env vars RUVIC_KEY_VAULT_*.
- Nunca lanza excepciones; retorna (ok, mensaje).

Ejecutable también como script para pruebas locales:
    python test_connection.py
"""

from __future__ import annotations


def test_connection() -> tuple[bool, str]:
    """Conecta a Azure Key Vault y lista un secreto usando las env vars
    RUVIC_KEY_VAULT_*."""
    try:
        from ruvic_key_vault_connector import (
            KeyVaultAuthError,
            KeyVaultClient,
            KeyVaultDataError,
            KeyVaultNetworkError,
        )
    except ImportError:
        return (
            False,
            "La librería ruvic-key-vault-connector no está instalada. "
            "Instala con: pip install git+https://github.com/Dgirto/"
            "Azure-Key-Vault.git#subdirectory=lib",
        )

    try:
        client = KeyVaultClient()  # valida que existan las env vars
    except ValueError as exc:
        return False, str(exc)

    try:
        client.ping()
    except KeyVaultAuthError as exc:
        return False, f"Autenticación fallida: {exc}"
    except KeyVaultNetworkError as exc:
        return False, f"Error de red: {exc}"
    except KeyVaultDataError as exc:
        return False, f"Error de datos: {exc}"
    except Exception as exc:  # red de seguridad: jamás propagar
        return False, f"Error inesperado: {exc}"

    return (
        True,
        f"Conexión exitosa al Key Vault {client.config.vault_url!r}",
    )


if __name__ == "__main__":
    ok, message = test_connection()
    print(f"{'OK' if ok else 'FALLO'}: {message}")
    raise SystemExit(0 if ok else 1)
