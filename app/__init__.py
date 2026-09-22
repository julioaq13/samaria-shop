import os
from flask import Flask
from app.config import Config
from app.database import close_db, init_db
from app.models.category import CategoryModel
from app.models.user import UserModel
from app.services.image_service import ImageService

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    app.teardown_appcontext(close_db)

    from app.routes.public import public_bp
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)

    @app.template_filter('currency')
    def currency_filter(value):
        try:
            val = float(value)
            if val.is_integer():
                return f"${int(val):,}".replace(',', '.')
            else:
                return f"${val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except (ValueError, TypeError):
            return f"${value}"

    @app.template_filter('img_url')
    def img_url_filter(image_record_or_path, origen='local'):
        return ImageService.get_image_url(image_record_or_path, origen)

    @app.context_processor
    def inject_global_vars():
        return {
            'site_name': 'SAMARIA',
            'site_tagline': 'Calzado Exclusivo y Confort'
        }

    with app.app_context():
        init_db(app)
        CategoryModel.init_default_categories()
        admin_user = UserModel.get_by_username(app.config['ADMIN_USERNAME'])
        if not admin_user:
            UserModel.create(
                username=app.config['ADMIN_USERNAME'],
                password=app.config['ADMIN_PASSWORD'],
                nombre=app.config['ADMIN_NAME']
            )

    return app