"""
Ejecutar UNA sola vez para crear el usuario administrador:
    python crear_admin.py
"""
from app import app, db
from database import Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    # Cambia el email y la contraseña a los que quieras
    EMAIL    = "admin@bembos.pe"
    PASSWORD = "admin123"

    if Usuario.query.filter_by(email=EMAIL).first():
        print(f"⚠️  Ya existe un usuario con el email '{EMAIL}'")
    else:
        admin = Usuario(
            nombre   = "Administrador Bembos",
            email    = EMAIL,
            password = generate_password_hash(PASSWORD),
            is_admin = True,
        )
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Admin creado exitosamente")
        print(f"   Email:      {EMAIL}")
        print(f"   Contraseña: {PASSWORD}")
