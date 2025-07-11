import sqlite3
import bcrypt

conn = sqlite3.connect("cuentas.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS cuentas_empresa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_empresa TEXT,
    usuario TEXT UNIQUE,
    password TEXT,
    base_datos TEXT
)
""")

# Generar el hash de la contraseña correctamente
plain_password = "admin123"
hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Insertar el usuario con contraseña hasheada
cursor.execute("""
INSERT OR IGNORE INTO cuentas_empresa (nombre_empresa, usuario, password, base_datos)
VALUES (?, ?, ?, ?)
""", ("Alican", "admin", hashed_password, "cliente1.db"))

# Si ya existía, actualizar la contraseña con el hash
cursor.execute("""
UPDATE cuentas_empresa SET password = ?, base_datos = ? WHERE usuario = ?
""", (hashed_password, "cliente1.db", "admin"))

conn.commit()
conn.close()

print("✅ Usuario 'admin' insertado/actualizado correctamente en cuentas.db con contraseña hasheada.")