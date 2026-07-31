"""Configuración del conector leída desde variables de entorno.

Convención de la plataforma: cada campo del formulario de configuración
llega como variable de entorno {ENV_PREFIX}{CAMPO} en mayúsculas.
Para este conector el prefijo es RUVIC_KEY_VAULT_.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

ENV_PREFIX = "RUVIC_KEY_VAULT_"


@dataclass(frozen=True)
class KeyVaultConfig:
    """Parámetros de conexión a Azure Key Vault vía Service Principal."""

    tenant_id: str
    client_id: str
    client_secret: str
    vault_url: str
    connect_timeout: int = 10

    @classmethod
    def from_env(cls) -> "KeyVaultConfig":
        """Construye la configuración desde las variables RUVIC_KEY_VAULT_*.

        Raises:
            ValueError: si falta alguna variable obligatoria.

        Ejemplo:
            >>> config = KeyVaultConfig.from_env()
            >>> config.vault_url
            'https://mi-vault.vault.azure.net'
        """
        missing = [
            f"{ENV_PREFIX}{name}"
            for name in ("TENANT_ID", "CLIENT_ID", "CLIENT_SECRET", "VAULT_URL")
            if not os.environ.get(f"{ENV_PREFIX}{name}")
        ]
        if missing:
            raise ValueError(
                "Faltan variables de entorno del conector key_vault: "
                + ", ".join(missing)
                + ". Configura el conector en Settings → Conectores."
            )
        return cls(
            tenant_id=os.environ[f"{ENV_PREFIX}TENANT_ID"],
            client_id=os.environ[f"{ENV_PREFIX}CLIENT_ID"],
            client_secret=os.environ[f"{ENV_PREFIX}CLIENT_SECRET"],
            vault_url=os.environ[f"{ENV_PREFIX}VAULT_URL"].rstrip("/"),
            connect_timeout=int(os.environ.get(f"{ENV_PREFIX}CONNECT_TIMEOUT", "10")),
        )
