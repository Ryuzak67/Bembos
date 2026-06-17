from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id       = db.Column(db.Integer, primary_key=True)
    nombre   = db.Column(db.String(120), nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    creado   = db.Column(db.DateTime, default=datetime.utcnow)

class Cliente(db.Model):
    __tablename__ = "clientes"
    id       = db.Column(db.Integer, primary_key=True)
    nombre   = db.Column(db.String(120), nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    distrito = db.Column(db.String(80))
    activo   = db.Column(db.Boolean, default=True)
    creado   = db.Column(db.DateTime, default=datetime.utcnow)

class Producto(db.Model):
    __tablename__ = "productos"
    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text)
    precio      = db.Column(db.Float, nullable=False)
    categoria   = db.Column(db.String(80))
    imagen_url  = db.Column(db.String(512))
    activo      = db.Column(db.Boolean, default=True)
    creado      = db.Column(db.DateTime, default=datetime.utcnow)

class Servicio(db.Model):
    __tablename__ = "servicios"
    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text)
    activo      = db.Column(db.Boolean, default=True)
    creado      = db.Column(db.DateTime, default=datetime.utcnow)
