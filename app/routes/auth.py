from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user import UserModel

auth_bp = Blueprint('auth', __name__, url_prefix='/admin')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicie sesión para acceder al panel de administración.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Por favor ingrese usuario y contraseña.', 'danger')
            return render_template('admin/login.html')

        user = UserModel.authenticate(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_nombre'] = user['nombre']
            flash(f'¡Bienvenido, {user["nombre"]}!', 'success')
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/admin'):
                return redirect(next_page)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('admin/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Ha cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))