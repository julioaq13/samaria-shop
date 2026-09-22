"""
Módulo de Arquitectura para Publicaciones / Estados Programados (WhatsApp / Redes).
Permite crear publicaciones con imágenes, selección de días y horas sin alterar el módulo principal.
"""
from app.database import query_db, execute_db

class PublicationModel:
    @staticmethod
    def get_all():
        return query_db("""
            SELECT pub.*, p.nombre as producto_nombre, p.marca as producto_marca 
            FROM programacion_publicaciones pub
            LEFT JOIN productos p ON pub.producto_id = p.id
            ORDER BY pub.id DESC
        """)

    @staticmethod
    def create(titulo, mensaje, dias_semana, hora, activo=1, producto_id=None, imagen_url=None):
        return execute_db("""
            INSERT INTO programacion_publicaciones (titulo, mensaje, dias_semana, hora, activo, producto_id, imagen_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [titulo, mensaje, dias_semana, hora, activo, producto_id, imagen_url])

    @staticmethod
    def toggle_active(pub_id):
        execute_db("""
            UPDATE programacion_publicaciones 
            SET activo = CASE WHEN activo = 1 THEN 0 ELSE 1 END
            WHERE id = ?
        """, [pub_id])
        return True

    @staticmethod
    def delete(pub_id):
        execute_db('DELETE FROM programacion_publicaciones WHERE id = ?', [pub_id])
        return True