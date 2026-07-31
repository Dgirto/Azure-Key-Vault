"""Cliente de lectura de secretos, llaves y certificados para Azure Key Vault.

Capacidades:
- get_secret():        obtiene el valor de un secreto.
- list_secrets():       lista los secretos disponibles (metadatos, no valores).
- get_certificate():    obtiene los metadatos de un certificado.

Las credenciales SIEMPRE provienen de variables de entorno
RUVIC_KEY_VAULT_* (ver config.KeyVaultConfig.from_env). Prohibido
hardcodearlas.
"""

from __future__ import annotations

from typing import Any

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceNotFoundError,
    ServiceRequestError,
)
from azure.identity import ClientSecretCredential
from azure.keyvault.certificates import CertificateClient
from azure.keyvault.secrets import SecretClient

from .config import KeyVaultConfig
from .exceptions import KeyVaultAuthError, KeyVaultDataError, KeyVaultNetworkError
from .logging_utils import get_logger


class KeyVaultClient:
    """Cliente de lectura de secretos, llaves y certificados de Azure
    Key Vault.

    Args:
        config: configuración de conexión. Si se omite, se lee de las
            variables de entorno RUVIC_KEY_VAULT_* (comportamiento
            estándar en el runtime de la plataforma).

    Ejemplo:
        >>> client = KeyVaultClient()  # lee RUVIC_KEY_VAULT_* del entorno
        >>> client.get_secret("db-password")
        'super-secreto-real'
    """

    def __init__(self, config: KeyVaultConfig | None = None) -> None:
        self.config = config or KeyVaultConfig.from_env()
        self._logger = get_logger()
        self._credential: ClientSecretCredential | None = None
        self._secret_client: SecretClient | None = None
        self._certificate_client: CertificateClient | None = None

    # ------------------------------------------------------------------ #
    # Conexión
    # ------------------------------------------------------------------ #

    def _get_credential(self) -> ClientSecretCredential:
        if self._credential is None:
            self._credential = ClientSecretCredential(
                tenant_id=self.config.tenant_id,
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
            )
        return self._credential

    def _get_secret_client(self) -> SecretClient:
        if self._secret_client is None:
            self._secret_client = SecretClient(
                vault_url=self.config.vault_url,
                credential=self._get_credential(),
                connection_timeout=self.config.connect_timeout,
            )
        return self._secret_client

    def _get_certificate_client(self) -> CertificateClient:
        if self._certificate_client is None:
            self._certificate_client = CertificateClient(
                vault_url=self.config.vault_url,
                credential=self._get_credential(),
                connection_timeout=self.config.connect_timeout,
            )
        return self._certificate_client

    def ping(self) -> bool:
        """Verifica la conexión listando hasta 1 secreto.

        Returns:
            True si la conexión funciona.

        Raises:
            KeyVaultAuthError / KeyVaultNetworkError / KeyVaultDataError.
        """
        self.list_secrets(max_results=1)
        self._logger.info("Ping exitoso a Key Vault %s", self.config.vault_url)
        return True

    # ------------------------------------------------------------------ #
    # Capacidad 1: obtener un secreto
    # ------------------------------------------------------------------ #

    def get_secret(self, secret_name: str) -> str:
        """Obtiene el valor de un secreto.

        Args:
            secret_name: nombre del secreto en el Key Vault.

        Returns:
            El valor del secreto.

        Ejemplo:
            >>> client.get_secret("db-password")
            'super-secreto-real'
        """
        secret_name = (secret_name or "").strip()
        if not secret_name:
            raise KeyVaultDataError("secret_name no puede estar vacío.")
        client = self._get_secret_client()
        try:
            secret = client.get_secret(secret_name)
        except ClientAuthenticationError as exc:
            raise KeyVaultAuthError(
                "Credenciales inválidas o sin permiso RBAC/access policy "
                f"suficiente para leer secretos: {exc}"
            ) from exc
        except ResourceNotFoundError as exc:
            raise KeyVaultDataError(
                f"El secreto {secret_name!r} no existe en el vault."
            ) from exc
        except ServiceRequestError as exc:
            raise KeyVaultNetworkError(f"No se pudo conectar al Key Vault: {exc}") from exc
        except HttpResponseError as exc:
            raise KeyVaultDataError(f"Error de Key Vault: {exc}") from exc
        self._logger.info("Secreto %s obtenido", secret_name)
        return secret.value or ""

    # ------------------------------------------------------------------ #
    # Capacidad 2: listar secretos (metadatos, no valores)
    # ------------------------------------------------------------------ #

    def list_secrets(self, max_results: int = 50) -> list[dict[str, Any]]:
        """Lista los secretos disponibles (solo metadatos, nunca valores).

        Args:
            max_results: máximo de secretos a retornar (default 50,
                máximo 200).

        Returns:
            Lista de dicts: {"name", "enabled", "updated_on"}.

        Ejemplo:
            >>> client.list_secrets()
            [{'name': 'db-password', 'enabled': True, ...}]
        """
        max_results = max(1, min(int(max_results), 200))
        client = self._get_secret_client()
        try:
            result = []
            for i, item in enumerate(client.list_properties_of_secrets()):
                if i >= max_results:
                    break
                result.append(
                    {
                        "name": item.name,
                        "enabled": item.enabled,
                        "updated_on": item.updated_on.isoformat() if item.updated_on else None,
                    }
                )
        except ClientAuthenticationError as exc:
            raise KeyVaultAuthError(
                f"Credenciales inválidas o sin permiso suficiente para listar secretos: {exc}"
            ) from exc
        except ServiceRequestError as exc:
            raise KeyVaultNetworkError(f"No se pudo conectar al Key Vault: {exc}") from exc
        except HttpResponseError as exc:
            raise KeyVaultDataError(f"Error de Key Vault: {exc}") from exc
        self._logger.info("Se listaron %d secreto(s)", len(result))
        return result

    # ------------------------------------------------------------------ #
    # Capacidad 3: obtener un certificado
    # ------------------------------------------------------------------ #

    def get_certificate(self, certificate_name: str) -> dict[str, Any]:
        """Obtiene los metadatos de un certificado (sin exportar la
        clave privada).

        Args:
            certificate_name: nombre del certificado en el Key Vault.

        Returns:
            Dict con: name, enabled, expires_on, thumbprint (hex).

        Ejemplo:
            >>> client.get_certificate("mi-cert")
            {'name': 'mi-cert', 'enabled': True, 'expires_on': '2027-01-01T00:00:00', ...}
        """
        certificate_name = (certificate_name or "").strip()
        if not certificate_name:
            raise KeyVaultDataError("certificate_name no puede estar vacío.")
        client = self._get_certificate_client()
        try:
            cert = client.get_certificate(certificate_name)
        except ClientAuthenticationError as exc:
            raise KeyVaultAuthError(
                "Credenciales inválidas o sin permiso suficiente para leer "
                f"certificados: {exc}"
            ) from exc
        except ResourceNotFoundError as exc:
            raise KeyVaultDataError(
                f"El certificado {certificate_name!r} no existe en el vault."
            ) from exc
        except ServiceRequestError as exc:
            raise KeyVaultNetworkError(f"No se pudo conectar al Key Vault: {exc}") from exc
        except HttpResponseError as exc:
            raise KeyVaultDataError(f"Error de Key Vault: {exc}") from exc
        self._logger.info("Certificado %s obtenido", certificate_name)
        return {
            "name": cert.name,
            "enabled": cert.properties.enabled,
            "expires_on": cert.properties.expires_on.isoformat()
            if cert.properties.expires_on
            else None,
            "thumbprint": cert.properties.x509_thumbprint.hex()
            if cert.properties.x509_thumbprint
            else None,
        }
