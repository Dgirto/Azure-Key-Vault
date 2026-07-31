---
name: key_vault
description: >
  Usa la librería ruvic_key_vault_connector para leer secretos, llaves
  y certificados en Azure Key Vault - obtener el valor de un secreto
  (get_secret), listar los secretos disponibles (list_secrets), y
  obtener los metadatos de un certificado (get_certificate). Úsala
  cuando el usuario pida consultar un secreto o certificado almacenado
  en Azure Key Vault.
triggers:
- azure key vault
- keyvault
- secreto azure
- certificado azure
---

# Conector Azure Key Vault (ruvic_key_vault_connector)

Librería Python de lectura de secretos, llaves y certificados de Azure
Key Vault. Está **preinstalada en el runtime** cuando el conector está
configurado (si no, instálala con `pip install git+https://github.com/Dgirto/Azure-Key-Vault.git#subdirectory=lib`).

## Regla crítica de credenciales

El código generado **NUNCA hardcodea credenciales**. Siempre se leen de
variables de entorno, disponibles cuando el conector `key_vault` está
configurado:

| Variable | Contenido |
|----------|-----------|
| `RUVIC_KEY_VAULT_TENANT_ID` | Tenant ID de Azure AD |
| `RUVIC_KEY_VAULT_CLIENT_ID` | Client ID del Service Principal |
| `RUVIC_KEY_VAULT_CLIENT_SECRET` | Client Secret del Service Principal |
| `RUVIC_KEY_VAULT_VAULT_URL` | URL del Key Vault |
| `RUVIC_KEY_VAULT_CONNECT_TIMEOUT` | (opcional) timeout en segundos |

Si estas variables NO existen, el conector no está configurado: no
generes código que lo use; indica al usuario que lo configure en
**Settings → Conectores**.

## Este conector expone valores reales de secretos

`get_secret` devuelve el **valor real** del secreto en texto plano.
**Nunca imprimas, loguees ni muestres el valor completo de un secreto
en la salida al usuario a menos que te lo pida explícitamente y
entienda que lo va a ver en texto plano.** Si el usuario solo necesita
confirmar que un secreto existe, usá `list_secrets` en vez de
`get_secret`.

## Conexión (siempre igual)

```python
from ruvic_key_vault_connector import KeyVaultClient

client = KeyVaultClient()  # lee RUVIC_KEY_VAULT_* del entorno automáticamente
```

## Capacidad 1 — Obtener un secreto

```python
valor = client.get_secret("db-password")
```

## Capacidad 2 — Listar secretos (solo metadatos)

```python
secretos = client.list_secrets()
for s in secretos:
    print(s["name"], s["enabled"])
```

## Capacidad 3 — Obtener un certificado

```python
cert = client.get_certificate("mi-cert")
print(cert["expires_on"], cert["thumbprint"])
```

`get_certificate` no exporta la clave privada, solo metadatos.

## Manejo de errores

```python
from ruvic_key_vault_connector import (
    KeyVaultAuthError, KeyVaultDataError, KeyVaultNetworkError,
)

try:
    valor = client.get_secret("db-password")
except KeyVaultAuthError:
    print("Credenciales inválidas o sin permiso suficiente")
except KeyVaultNetworkError:
    print("No se pudo alcanzar el Key Vault — reintenta en unos segundos")
except KeyVaultDataError as e:
    print(f"Error de datos: {e}")  # ej. el secreto/certificado no existe
```

## Buenas prácticas al generar código

1. Lee credenciales SOLO de las variables `RUVIC_KEY_VAULT_*` (el constructor de `KeyVaultClient` ya lo hace).
2. Nunca imprimas `RUVIC_KEY_VAULT_CLIENT_SECRET` en logs ni en la salida.
3. **No expongas el valor devuelto por `get_secret` sin que el usuario lo haya pedido explícitamente sabiendo que va a verlo en texto plano.**
4. Usá `list_secrets` para explorar qué secretos existen antes de pedir uno específico con `get_secret`.
5. `get_certificate` nunca expone la clave privada — si el usuario necesita la clave privada, indicale que esta librería no lo soporta por diseño (es de solo lectura de metadatos).
