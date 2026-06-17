from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from database import db, Usuario, Cliente, Producto, Servicio
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "bembos-secret-2025")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bembos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Debes iniciar sesión como administrador.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ─── PUBLIC ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email")
        password = request.form.get("password")
        user = Usuario.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"]   = user.id
            session["user_name"] = user.nombre
            session["is_admin"]  = user.is_admin
            if user.is_admin:
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("index"))
        flash("Correo o contraseña incorrectos", "error")
    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombres   = request.form.get("nombres")
        apellidos = request.form.get("apellidos")
        email     = request.form.get("email")
        password  = request.form.get("password")
        telefono  = request.form.get("telefono")
        distrito  = request.form.get("distrito")
        if Usuario.query.filter_by(email=email).first():
            flash("Ya existe una cuenta con ese correo", "error")
            return render_template("registro.html")
        hashed  = generate_password_hash(password)
        nuevo   = Usuario(nombre=f"{nombres} {apellidos}", email=email, password=hashed, is_admin=False)
        cliente = Cliente(nombre=f"{nombres} {apellidos}", email=email, telefono=telefono, distrito=distrito)
        db.session.add(nuevo)
        db.session.add(cliente)
        db.session.commit()
        flash("¡Cuenta creada! Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("login"))
    return render_template("registro.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ─── ADMIN DASHBOARD ───────────────────────────────────────────────────────────

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    total_clientes  = Cliente.query.count()
    total_productos = Producto.query.filter_by(activo=True).count()
    total_servicios = Servicio.query.count()
    return render_template("admin/dashboard.html", active="dashboard",
                           total_clientes=total_clientes,
                           total_productos=total_productos,
                           total_servicios=total_servicios)

# ─── ADMIN CLIENTES ────────────────────────────────────────────────────────────

@app.route("/admin/clientes")
@admin_required
def admin_clientes():
    clientes = Cliente.query.order_by(Cliente.id.desc()).all()
    return render_template("admin/clientes.html", clientes=clientes, active="clientes")

@app.route("/admin/clientes/nuevo", methods=["GET", "POST"])
@admin_required
def admin_nuevo_cliente():
    if request.method == "POST":
        c = Cliente(
            nombre   = request.form["nombre"],
            email    = request.form["email"],
            telefono = request.form.get("telefono", ""),
            distrito = request.form.get("distrito", ""),
        )
        db.session.add(c)
        db.session.commit()
        flash("Cliente creado correctamente.", "success")
        return redirect(url_for("admin_clientes"))
    return render_template("admin/cliente_form.html", cliente=None, active="clientes")

@app.route("/admin/clientes/<int:id>/editar", methods=["GET", "POST"])
@admin_required
def admin_editar_cliente(id):
    c = Cliente.query.get_or_404(id)
    if request.method == "POST":
        c.nombre   = request.form["nombre"]
        c.email    = request.form["email"]
        c.telefono = request.form.get("telefono", "")
        c.distrito = request.form.get("distrito", "")
        db.session.commit()
        flash("Cliente actualizado.", "success")
        return redirect(url_for("admin_clientes"))
    return render_template("admin/cliente_form.html", cliente=c, active="clientes")

@app.route("/admin/clientes/<int:id>/eliminar", methods=["POST"])
@admin_required
def admin_eliminar_cliente(id):
    c = Cliente.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash("Cliente eliminado.", "success")
    return redirect(url_for("admin_clientes"))

# ─── ADMIN PRODUCTOS ───────────────────────────────────────────────────────────

@app.route("/admin/productos")
@admin_required
def admin_productos():
    productos = Producto.query.order_by(Producto.id.desc()).all()
    return render_template("admin/productos.html", productos=productos, active="productos")

@app.route("/admin/productos/nuevo", methods=["GET", "POST"])
@admin_required
def admin_nuevo_producto():
    if request.method == "POST":
        p = Producto(
            nombre      = request.form["nombre"],
            descripcion = request.form.get("descripcion", ""),
            precio      = float(request.form["precio"]),
            categoria   = request.form.get("categoria", ""),
            imagen_url  = request.form.get("imagen_url", ""),
            activo      = "activo" in request.form,
        )
        db.session.add(p)
        db.session.commit()
        flash("Producto creado correctamente.", "success")
        return redirect(url_for("admin_productos"))
    return render_template("admin/producto_form.html", producto=None, active="productos")

@app.route("/admin/productos/<int:id>/editar", methods=["GET", "POST"])
@admin_required
def admin_editar_producto(id):
    p = Producto.query.get_or_404(id)
    if request.method == "POST":
        p.nombre      = request.form["nombre"]
        p.descripcion = request.form.get("descripcion", "")
        p.precio      = float(request.form["precio"])
        p.categoria   = request.form.get("categoria", "")
        p.imagen_url  = request.form.get("imagen_url", "")
        p.activo      = "activo" in request.form
        db.session.commit()
        flash("Producto actualizado.", "success")
        return redirect(url_for("admin_productos"))
    return render_template("admin/producto_form.html", producto=p, active="productos")

@app.route("/admin/productos/<int:id>/eliminar", methods=["POST"])
@admin_required
def admin_eliminar_producto(id):
    p = Producto.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash("Producto eliminado.", "success")
    return redirect(url_for("admin_productos"))

# ─── ADMIN SERVICIOS ───────────────────────────────────────────────────────────

@app.route("/admin/servicios")
@admin_required
def admin_servicios():
    servicios = Servicio.query.order_by(Servicio.id.desc()).all()
    return render_template("admin/servicios.html", servicios=servicios, active="servicios")

@app.route("/admin/servicios/nuevo", methods=["GET", "POST"])
@admin_required
def admin_nuevo_servicio():
    if request.method == "POST":
        s = Servicio(
            nombre      = request.form["nombre"],
            descripcion = request.form.get("descripcion", ""),
            activo      = "activo" in request.form,
        )
        db.session.add(s)
        db.session.commit()
        flash("Servicio creado correctamente.", "success")
        return redirect(url_for("admin_servicios"))
    return render_template("admin/servicio_form.html", servicio=None, active="servicios")

@app.route("/admin/servicios/<int:id>/editar", methods=["GET", "POST"])
@admin_required
def admin_editar_servicio(id):
    s = Servicio.query.get_or_404(id)
    if request.method == "POST":
        s.nombre      = request.form["nombre"]
        s.descripcion = request.form.get("descripcion", "")
        s.activo      = "activo" in request.form
        db.session.commit()
        flash("Servicio actualizado.", "success")
        return redirect(url_for("admin_servicios"))
    return render_template("admin/servicio_form.html", servicio=s, active="servicios")

@app.route("/admin/servicios/<int:id>/eliminar", methods=["POST"])
@admin_required
def admin_eliminar_servicio(id):
    s = Servicio.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    flash("Servicio eliminado.", "success")
    return redirect(url_for("admin_servicios"))

# ─── ADMIN USUARIOS ────────────────────────────────────────────────────────────

@app.route("/admin/usuarios")
@admin_required
def admin_usuarios():
    usuarios = Usuario.query.order_by(Usuario.id.desc()).all()
    return render_template("admin/usuarios.html", usuarios=usuarios, active="usuarios")

@app.route("/admin/usuarios/nuevo", methods=["GET", "POST"])
@admin_required
def admin_nuevo_usuario():
    if request.method == "POST":
        email = request.form["email"]
        if Usuario.query.filter_by(email=email).first():
            flash("Ya existe un usuario con ese correo.", "error")
            return render_template("admin/usuario_form.html", usuario=None, active="usuarios")
        u = Usuario(
            nombre   = request.form["nombre"],
            email    = email,
            password = generate_password_hash(request.form["password"]),
            is_admin = "is_admin" in request.form,
        )
        db.session.add(u)
        db.session.commit()
        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("admin_usuarios"))
    return render_template("admin/usuario_form.html", usuario=None, active="usuarios")

@app.route("/admin/usuarios/<int:id>/editar", methods=["GET", "POST"])
@admin_required
def admin_editar_usuario(id):
    u = Usuario.query.get_or_404(id)
    if request.method == "POST":
        u.nombre   = request.form["nombre"]
        u.email    = request.form["email"]
        u.is_admin = "is_admin" in request.form
        if request.form.get("password"):
            u.password = generate_password_hash(request.form["password"])
        db.session.commit()
        flash("Usuario actualizado.", "success")
        return redirect(url_for("admin_usuarios"))
    return render_template("admin/usuario_form.html", usuario=u, active="usuarios")

@app.route("/admin/usuarios/<int:id>/eliminar", methods=["POST"])
@admin_required
def admin_eliminar_usuario(id):
    u = Usuario.query.get_or_404(id)
    if u.id == session.get("user_id"):
        flash("No puedes eliminar tu propia cuenta.", "error")
        return redirect(url_for("admin_usuarios"))
    db.session.delete(u)
    db.session.commit()
    flash("Usuario eliminado.", "success")
    return redirect(url_for("admin_usuarios"))

if __name__ == "__main__":
    app.run(debug=True)
