from models import Base, engine

# Crear todas las tablas definidas en los modelos
Base.metadata.create_all(bind=engine)

print("✅ Tablas creadas correctamente.")