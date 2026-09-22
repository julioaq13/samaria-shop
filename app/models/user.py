from werkzeug.security import generate_password_hash, check_password_hash
from app.database import query_db, execute_db

class UserModel:
    @staticmethod
    def get_by_id(user_id):
        return query_db('SELECT * FROM usuarios WHERE id = ?', [user_id], one=True)

    @staticmethod
    def get_by_username(username):
        return query_db('SELECT * FROM usuarios WHERE username = ?', [username], one=True)

    @staticmethod
    def authenticate(username, password):
        user = UserModel.get_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None

    @staticmethod
    def create(username, password, nombre='Administrador'):
        password_hash = generate_password_hash(password)
        return execute_db(
            'INSERT INTO usuarios (username, password_hash, nombre) VALUES (?, ?, ?)',
            [username, password_hash, nombre]
        )

    @staticmethod
    def update_password(user_id, new_password):
        password_hash = generate_password_hash(new_password)
        execute_db(
            'UPDATE usuarios SET password_hash = ? WHERE id = ?',
            [password_hash, user_id]
        )