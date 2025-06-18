from models import Base, engine

# Crea las tablas en la base de datos según el modelo actualizado
Base.metadata.drop_all(bind=engine)  # Elimina las tablas existentes (¡CUIDADO! borra todos los datos)
Base.metadata.create_all(bind=engine)  # Crea las nuevas tablas

print("✅ Base de datos recreada con éxito.")