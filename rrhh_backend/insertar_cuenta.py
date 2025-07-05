import sqlite3

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

# Usa INSERT OR IGNORE para no duplicar
cursor.execute("""
INSERT OR IGNORE INTO cuentas_empresa (nombre_empresa, usuario, password, base_datos)
VALUES (?, ?, ?, ?)
""", ("Alican", "admin", "admin123", "cliente1.db"))

# Si ya existía, aseguramos actualizar la contraseña
cursor.execute("""
UPDATE cuentas_empresa SET password = ?, base_datos = ? WHERE usuario = ?
""", ("admin123", "cliente1.db", "admin"))

conn.commit()
conn.close()

print("✅ Usuario 'admin' insertado/actualizado correctamente en cuentas.db")