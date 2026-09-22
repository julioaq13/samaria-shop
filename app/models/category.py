from app.database import query_db, execute_db

class CategoryModel:
    @staticmethod
    def get_all():
        return query_db('SELECT * FROM categorias ORDER BY id ASC')

    @staticmethod
    def get_by_slug(slug):
        return query_db('SELECT * FROM categorias WHERE slug = ?', [slug.lower()], one=True)

    @staticmethod
    def get_by_id(cat_id):
        return query_db('SELECT * FROM categorias WHERE id = ?', [cat_id], one=True)

    @staticmethod
    def init_default_categories():
        defaults = [
            ('Nuevo', 'nuevo', 'Calzado recién llegado a nuestra tienda'),
            ('Hombre', 'hombre', 'Colección de calzado para caballeros'),
            ('Mujer', 'mujer', 'Colección de calzado para damas'),
            ('Promo', 'promo', 'Ofertas especiales y precios de descuento')
        ]
        for nombre, slug, desc in defaults:
            existing = CategoryModel.get_by_slug(slug)
            if not existing:
                execute_db(
                    'INSERT INTO categorias (nombre, slug, descripcion) VALUES (?, ?, ?)',
                    [nombre, slug, desc]
                )