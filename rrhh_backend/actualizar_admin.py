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

password_hash = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

cursor.execute("""
INSERT OR IGNORE INTO cuentas_empresa (nombre_empresa, usuario, password, base_datos)
VALUES (?, ?, ?, ?)
""", ("Alican", "admin", password_hash, "cliente1.db"))

cursor.execute("""
UPDATE cuentas_empresa SET password = ?, base_datos = ? WHERE usuario = ?
""", (password_hash, "cliente1.db", "admin"))

conn.commit()
conn.close()

print("✅ Usuario 'admin' creado con contraseña 'admin123'. Hash generado:", password_hash)