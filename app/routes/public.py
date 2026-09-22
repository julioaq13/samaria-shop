from flask import Blueprint, render_template, request, abort, jsonify
from app.models.product import ProductModel
from app.models.category import CategoryModel
from app.models.banner import BannerModel

public_bp = Blueprint('public', __name__)

CATEGORY_TITLES = {
    'nuevo': 'Nuevos productos',
    'hombre': 'Calzado para Hombre',
    'mujer': 'Calzado para Mujer',
    'promo': 'Promociones',
}

@public_bp.route('/')
@public_bp.route('/catalogo')
def index():
    search_query = request.args.get('q', '').strip()
    products = ProductModel.get_all(only_available=True, search_query=search_query if search_query else None)
    banners = BannerModel.get_active()
    
    title = 'Todos nuestros productos'
    if search_query:
        title = f'Resultados de búsqueda: "{search_query}"'

    categories = CategoryModel.get_all()
    return render_template(
        'catalog.html',
        products=products,
        banners=banners,
        current_category=None,
        page_title=title,
        search_query=search_query,
        categories=categories
    )

@public_bp.route('/categoria/<slug>')
def category_view(slug):
    slug_clean = slug.lower().strip()
    cat = CategoryModel.get_by_slug(slug_clean)
    if not cat:
        abort(404)

    search_query = request.args.get('q', '').strip()
    products = ProductModel.get_all(
        only_available=True,
        category_slug=slug_clean,
        search_query=search_query if search_query else None
    )
    banners = BannerModel.get_active()

    title = CATEGORY_TITLES.get(slug_clean, cat['nombre'])
    if search_query:
        title = f'{title} - Búsqueda: "{search_query}"'

    categories = CategoryModel.get_all()
    return render_template(
        'catalog.html',
        products=products,
        banners=banners,
        current_category=slug_clean,
        current_category_data=cat,
        page_title=title,
        search_query=search_query,
        categories=categories
    )

@public_bp.route('/producto/<int:product_id>')
def product_detail(product_id):
    product = ProductModel.get_by_id(product_id)
    if not product or product['disponible'] != 1:
        abort(404)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('format') == 'json':
        return jsonify({
            'id': product['id'],
            'nombre': product['nombre'],
            'marca': product['marca'],
            'precio': product['precio'],
            'descripcion': product['descripcion'],
            'disponible': product['disponible'],
            'categorias': [dict(c) for c in product['categorias']],
            'imagenes': [dict(img) for img in product['imagenes']]
        })

    return render_template('product_detail.html', product=product)