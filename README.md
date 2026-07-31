# Conector Azure Key Vault (CON-071)

Conector Ruvic de lectura de secretos, llaves y certificados en Azure
Key Vault. Permite obtener el valor de un secreto, listar los secretos
disponibles (metadatos, no valores), y obtener los metadatos de un
certificado.

## Instalación

```bash
pip install git+https://github.com/Dgirto/Azure-Key-Vault.git#subdirectory=lib
```

Python 3.10+. Dependencias: `azure-identity`, `azure-keyvault-secrets`,
`azure-keyvault-certificates`.

## Permisos requeridos en Azure

Crea un **Service Principal dedicado** (App Registration en Azure AD) y
otorgale acceso al Key Vault con el **mínimo privilegio**:

- Si el vault usa **RBAC** (recomendado, modelo moderno): asigná los
  roles **"Key Vault Secrets User"** y **"Key Vault Certificate User"**
  al Service Principal, con alcance limitado a ese vault específico.
- Si el vault usa el modelo clásico de **Access Policies**: otorgá
  permisos `Get` y `List` sobre `Secrets` y `Certificates` únicamente.

No otorgues permisos de escritura (`Set`, `Delete`, `Purge`, `Recover`)
ni de administración de acceso.

## Variables de entorno (`RUVIC_KEY_VAULT_*`)

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| `RUVIC_KEY_VAULT_TENANT_ID` | Sí | Tenant ID de Azure AD |
| `RUVIC_KEY_VAULT_CLIENT_ID` | Sí | Client ID del Service Principal |
| `RUVIC_KEY_VAULT_CLIENT_SECRET` | Sí | Client Secret del Service Principal |
| `RUVIC_KEY_VAULT_VAULT_URL` | Sí | URL del Key Vault (ej. `https://mi-vault.vault.azure.net`) |
| `RUVIC_KEY_VAULT_CONNECT_TIMEOUT` | No (default `10`) | Timeout de conexión en segundos |

## Pruebas locales

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ./lib

export RUVIC_KEY_VAULT_TENANT_ID=tu-tenant-id
export RUVIC_KEY_VAULT_CLIENT_ID=tu-client-id
export RUVIC_KEY_VAULT_CLIENT_SECRET=tu-client-secret
export RUVIC_KEY_VAULT_VAULT_URL=https://tu-vault.vault.azure.net

python test_connection.py
python validate_local.py
```

Antes de correr `validate_local.py`, editá `TEST_SECRET_NAME` y
`TEST_CERTIFICATE_NAME` con nombres de un secreto y un certificado ya
existentes en tu vault.

## Notas de integración

- Este conector es **100% de solo lectura** — no existe ninguna
  operación de escritura, aunque devuelve valores reales de secretos.
- `get_certificate` **no exporta la clave privada** del certificado,
  solo sus metadatos (fecha de expiración, huella digital, si está
  habilitado).
- `list_secrets` **nunca** devuelve valores de secretos, solo metadatos
  — para obtener un valor hay que llamar a `get_secret` explícitamente.
- Requiere que el Service Principal tenga acceso de red al Key Vault
  (por defecto los vaults son accesibles desde internet salvo que se
  configure un firewall/red privada específico).
