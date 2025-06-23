import sqlite3

conn = sqlite3.connect("cuentas.db")
cursor = conn.cursor()

cursor.execute("SELECT usuario, password FROM cuentas_empresa")
usuarios = cursor.fetchall()

print("👤 Usuarios en cuentas.db:")
for u in usuarios:
    print(f" - Usuario: {u[0]} | Contraseña: {u[1]}")

conn.close()