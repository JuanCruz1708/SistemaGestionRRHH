import sqlite3

conn = sqlite3.connect("cuentas.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = cursor.fetchall()

print("📋 Tablas en cuentas.db:")
for t in tablas:
    print(" -", t[0])

conn.close()