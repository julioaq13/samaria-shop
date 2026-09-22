from app.database import query_db, execute_db

class BannerModel:
    @staticmethod
    def get_all():
        return query_db('SELECT * FROM banners ORDER BY orden ASC, id DESC')

    @staticmethod
    def get_active():
        return query_db('SELECT * FROM banners WHERE activo = 1 ORDER BY orden ASC, id ASC')

    @staticmethod
    def get_by_id(banner_id):
        return query_db('SELECT * FROM banners WHERE id = ?', [banner_id], one=True)

    @staticmethod
    def create(titulo, subtitulo='', texto_boton='Explorar Colección', enlace_url='#catalogo-seccion', imagen_url='banner.jpg', origen='local', orden=0, activo=1):
        return execute_db("""
            INSERT INTO banners (titulo, subtitulo, texto_boton, enlace_url, imagen_url, origen, orden, activo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [titulo, subtitulo, texto_boton, enlace_url, imagen_url, origen, orden, activo])

    @staticmethod
    def update(banner_id, titulo, subtitulo='', texto_boton='Explorar Colección', enlace_url='#catalogo-seccion', imagen_url=None, origen='local', orden=0, activo=1):
        if imagen_url:
            execute_db("""
                UPDATE banners 
                SET titulo = ?, subtitulo = ?, texto_boton = ?, enlace_url = ?, imagen_url = ?, origen = ?, orden = ?, activo = ?
                WHERE id = ?
            """, [titulo, subtitulo, texto_boton, enlace_url, imagen_url, origen, orden, activo, banner_id])
        else:
            execute_db("""
                UPDATE banners 
                SET titulo = ?, subtitulo = ?, texto_boton = ?, enlace_url = ?, orden = ?, activo = ?
                WHERE id = ?
            """, [titulo, subtitulo, texto_boton, enlace_url, orden, activo, banner_id])
        return True

    @staticmethod
    def toggle_active(banner_id):
        execute_db("""
            UPDATE banners 
            SET activo = CASE WHEN activo = 1 THEN 0 ELSE 1 END
            WHERE id = ?
        """, [banner_id])
        return True

    @staticmethod
    def delete(banner_id):
        execute_db('DELETE FROM banners WHERE id = ?', [banner_id])
        return True

    @staticmethod
    def init_default_banners():
        existing = query_db('SELECT COUNT(*) as count FROM banners', one=True)
        if existing and existing['count'] == 0:
            defaults = [
                ('CALZADO CON ESTILO & CONFORT', 'Descubre las últimas tendencias en calzado exclusivo para Hombre y Mujer.', 'Explorar Colección', '#catalogo-seccion', 'banner.jpg', 'local', 1, 1),
                ('NUEVA COLECCIÓN 2026', 'Diseños exclusivos fabricados con materiales de máxima calidad y confort.', 'Ver Novedades', '/categoria/nuevo', 'banner.jpg', 'local', 2, 1),
                ('PROMOCIONES ESPECIALES', 'Aprovecha ofertas exclusivas por tiempo limitado en calzado seleccionado.', 'Ver Promos', '/categoria/promo', 'banner.jpg', 'local', 3, 1)
            ]
            for tit, sub, btn, link, img, orig, ord_num, act in defaults:
                BannerModel.create(tit, sub, btn, link, img, orig, ord_num, act)