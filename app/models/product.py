from app.database import query_db, execute_db, get_db

class ProductModel:
    @staticmethod
    def get_all(only_available=False, category_slug=None, search_query=None):
        sql = """
            SELECT DISTINCT p.*, 
                   (SELECT img.ruta_o_url FROM imagenes img 
                    WHERE img.producto_id = p.id 
                    ORDER BY img.es_principal DESC, img.id ASC LIMIT 1) as imagen_principal,
                   (SELECT img.origen FROM imagenes img 
                    WHERE img.producto_id = p.id 
                    ORDER BY img.es_principal DESC, img.id ASC LIMIT 1) as imagen_origen
            FROM productos p
        """
        joins = []
        conditions = []
        params = []

        if category_slug:
            joins.append('JOIN producto_categoria pc ON p.id = pc.producto_id')
            joins.append('JOIN categorias c ON pc.categoria_id = c.id')
            conditions.append('c.slug = ?')
            params.append(category_slug.lower())

        if only_available:
            conditions.append('p.disponible = 1')

        if search_query:
            term = f'%{search_query.strip()}%'
            conditions.append('(p.nombre LIKE ? OR p.marca LIKE ? OR p.descripcion LIKE ?)')
            params.extend([term, term, term])

        if joins:
            sql += ' ' + ' '.join(joins)
        if conditions:
            sql += ' WHERE ' + ' AND '.join(conditions)

        sql += ' ORDER BY p.id DESC'

        rows = query_db(sql, params)
        
        products = []
        for row in rows:
            prod_dict = dict(row)
            prod_dict['categorias'] = ProductModel.get_categories_for_product(row['id'])
            products.append(prod_dict)
        return products

    @staticmethod
    def get_by_id(product_id):
        row = query_db('SELECT * FROM productos WHERE id = ?', [product_id], one=True)
        if not row:
            return None
        
        prod = dict(row)
        prod['categorias'] = ProductModel.get_categories_for_product(product_id)
        prod['categoria_ids'] = [c['id'] for c in prod['categorias']]
        prod['imagenes'] = ProductModel.get_images_for_product(product_id)
        
        main_img = next((img for img in prod['imagenes'] if img['es_principal'] == 1), None)
        if not main_img and prod['imagenes']:
            main_img = prod['imagenes'][0]
        prod['imagen_principal'] = main_img['ruta_o_url'] if main_img else None
        prod['imagen_origen'] = main_img['origen'] if main_img else 'local'
        
        return prod

    @staticmethod
    def get_categories_for_product(product_id):
        return query_db("""
            SELECT c.* FROM categorias c
            JOIN producto_categoria pc ON c.id = pc.categoria_id
            WHERE pc.producto_id = ?
            ORDER BY c.id ASC
        """, [product_id])

    @staticmethod
    def get_images_for_product(product_id):
        return query_db("""
            SELECT * FROM imagenes 
            WHERE producto_id = ? 
            ORDER BY es_principal DESC, orden ASC, id ASC
        """, [product_id])

    @staticmethod
    def create(nombre, marca, precio, descripcion='', disponible=1, categoria_ids=None):
        db = get_db()
        cur = db.execute("""
            INSERT INTO productos (nombre, marca, precio, descripcion, disponible)
            VALUES (?, ?, ?, ?, ?)
        """, [nombre, marca, precio, descripcion, disponible])
        prod_id = cur.lastrowid

        if categoria_ids:
            for cat_id in categoria_ids:
                db.execute("""
                    INSERT OR IGNORE INTO producto_categoria (producto_id, categoria_id)
                    VALUES (?, ?)
                """, [prod_id, int(cat_id)])

        db.commit()
        return prod_id

    @staticmethod
    def update(product_id, nombre, marca, precio, descripcion='', disponible=1, categoria_ids=None):
        db = get_db()
        db.execute("""
            UPDATE productos 
            SET nombre = ?, marca = ?, precio = ?, descripcion = ?, disponible = ?, fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id = ?
        """, [nombre, marca, precio, descripcion, disponible, product_id])

        if categoria_ids is not None:
            db.execute('DELETE FROM producto_categoria WHERE producto_id = ?', [product_id])
            for cat_id in categoria_ids:
                db.execute("""
                    INSERT INTO producto_categoria (producto_id, categoria_id)
                    VALUES (?, ?)
                """, [product_id, int(cat_id)])

        db.commit()
        return True

    @staticmethod
    def delete(product_id):
        execute_db('DELETE FROM productos WHERE id = ?', [product_id])
        return True

    @staticmethod
    def toggle_disponible(product_id):
        execute_db("""
            UPDATE productos 
            SET disponible = CASE WHEN disponible = 1 THEN 0 ELSE 1 END,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id = ?
        """, [product_id])
        return True

    @staticmethod
    def add_image(product_id, ruta_o_url, origen='local', es_principal=0, orden=0):
        if es_principal:
            execute_db('UPDATE imagenes SET es_principal = 0 WHERE producto_id = ?', [product_id])
        
        existing = query_db('SELECT COUNT(*) as count FROM imagenes WHERE producto_id = ?', [product_id], one=True)
        if existing and existing['count'] == 0:
            es_principal = 1

        return execute_db("""
            INSERT INTO imagenes (producto_id, ruta_o_url, origen, es_principal, orden)
            VALUES (?, ?, ?, ?, ?)
        """, [product_id, ruta_o_url, origen, es_principal, orden])

    @staticmethod
    def set_main_image(product_id, image_id):
        db = get_db()
        db.execute('UPDATE imagenes SET es_principal = 0 WHERE producto_id = ?', [product_id])
        db.execute('UPDATE imagenes SET es_principal = 1 WHERE id = ? AND producto_id = ?', [image_id, product_id])
        db.commit()
        return True

    @staticmethod
    def delete_image(product_id, image_id):
        img = query_db('SELECT * FROM imagenes WHERE id = ? AND producto_id = ?', [image_id, product_id], one=True)
        if not img:
            return None
        
        execute_db('DELETE FROM imagenes WHERE id = ? AND producto_id = ?', [image_id, product_id])
        
        if img['es_principal'] == 1:
            remaining = query_db('SELECT id FROM imagenes WHERE producto_id = ? LIMIT 1', [product_id], one=True)
            if remaining:
                execute_db('UPDATE imagenes SET es_principal = 1 WHERE id = ?', [remaining['id']])
                
        return dict(img)

    @staticmethod
    def get_dashboard_stats():
        total = query_db('SELECT COUNT(*) as total FROM productos', one=True)['total']
        activos = query_db('SELECT COUNT(*) as total FROM productos WHERE disponible = 1', one=True)['total']
        
        promos = query_db("""
            SELECT COUNT(DISTINCT p.id) as total 
            FROM productos p
            JOIN producto_categoria pc ON p.id = pc.producto_id
            JOIN categorias c ON pc.categoria_id = c.id
            WHERE c.slug = 'promo'
        """, one=True)['total']
        
        return {
            'total_productos': total,
            'productos_activos': activos,
            'productos_inactivos': total - activos,
            'productos_promocion': promos
        }