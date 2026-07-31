"""Validación local del conector key_vault: ejercita las 3 capacidades
de solo lectura.

Uso:
    python validate_local.py

Requiere las variables RUVIC_KEY_VAULT_* exportadas en el entorno, y el
nombre de un secreto y un certificado de prueba ya existentes en el
vault (editá TEST_SECRET_NAME y TEST_CERTIFICATE_NAME abajo).
"""

from ruvic_key_vault_connector import KeyVaultClient, setup_logging

TEST_SECRET_NAME = "ruvic-test-secret"  # <-- reemplaza por un secreto de prueba real
TEST_CERTIFICATE_NAME = "ruvic-test-cert"  # <-- reemplaza por un certificado de prueba real

setup_logging("INFO")
client = KeyVaultClient()

print("== 1. Listar secretos ==")
secretos = client.list_secrets()
for s in secretos[:5]:
    print(f"  {s['name']}: enabled={s['enabled']}")

print("== 2. Obtener secreto de prueba ==")
valor = client.get_secret(TEST_SECRET_NAME)
print(f"  longitud del valor: {len(valor)} caracteres (no se imprime el contenido)")

print("== 3. Obtener certificado de prueba ==")
cert = client.get_certificate(TEST_CERTIFICATE_NAME)
print(f"  {cert}")

print("\nTodo OK: list_secrets, get_secret y get_certificate funcionan.")
