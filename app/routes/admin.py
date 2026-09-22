from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.routes.auth import login_required
from app.models.product import ProductModel
from app.models.category import CategoryModel
from app.models.banner import BannerModel
from app.services.image_service import ImageService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# -------------------------------------------------------------
# 1. Dashboard Principal
# -------------------------------------------------------------
@admin_bp.route('/', strict_slashes=False)
@admin_bp.route('/dashboard', strict_slashes=False)
@login_required
def dashboard():
    stats = ProductModel.get_dashboard_stats()
    products = ProductModel.get_all()
    banners_count = len(BannerModel.get_all())
    stats['total_banners'] = banners_count
    return render_template('admin/dashboard.html', stats=stats, products=products)

# -------------------------------------------------------------
# 2. Gestión de Productos (CRUD + Google Drive)
# -------------------------------------------------------------
@admin_bp.route('/productos/nuevo', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def product_new():
    categories = CategoryModel.get_all()
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        marca = request.form.get('marca', '').strip()
        precio_str = request.form.get('precio', '').strip().replace(',', '.')
        descripcion = request.form.get('descripcion', '').strip()
        disponible = 1 if request.form.get('disponible') else 0
        categoria_ids = request.form.getlist('categorias')
        drive_links_raw = request.form.get('drive_links', '').strip()

        if not nombre or not marca or not precio_str:
            flash('Por favor complete los campos obligatorios: Nombre, Marca y Precio.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=None)

        try:
            precio = float(precio_str)
            if precio < 0:
                raise ValueError()
        except ValueError:
            flash('El precio debe ser un número válido.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=None)

        prod_id = ProductModel.create(
            nombre=nombre,
            marca=marca,
            precio=precio,
            descripcion=descripcion,
            disponible=disponible,
            categoria_ids=categoria_ids
        )

        first_img = True
        
        # 1. Procesar imágenes locales subidas
        files = request.files.getlist('imagenes')
        for file in files:
            if file and file.filename:
                try:
                    filename = ImageService.save_image(file)
                    if filename:
                        ProductModel.add_image(
                            product_id=prod_id,
                            ruta_o_url=filename,
                            origen='local',
                            es_principal=1 if first_img else 0
                        )
                        first_img = False
                except Exception as e:
                    flash(f'Error al subir una de las imágenes: {str(e)}', 'warning')

        # 2. Procesar enlaces de Google Drive (separados por líneas o comas)
        if drive_links_raw:
            drive_lines = [l.strip() for l in drive_links_raw.replace(',', '\n').split('\n') if l.strip()]
            for link in drive_lines:
                drive_id = ImageService.extract_drive_id(link)
                if drive_id:
                    ProductModel.add_image(
                        product_id=prod_id,
                        ruta_o_url=drive_id,
                        origen='drive',
                        es_principal=1 if first_img else 0
                    )
                    first_img = False

        flash(f'¡Producto "{nombre}" creado exitosamente!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/product_form.html', categories=categories, product=None)

@admin_bp.route('/productos/editar/<int:product_id>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def product_edit(product_id):
    product = ProductModel.get_by_id(product_id)
    if not product:
        flash('El producto no existe.', 'danger')
        return redirect(url_for('admin.dashboard'))

    categories = CategoryModel.get_all()

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        marca = request.form.get('marca', '').strip()
        precio_str = request.form.get('precio', '').strip().replace(',', '.')
        descripcion = request.form.get('descripcion', '').strip()
        disponible = 1 if request.form.get('disponible') else 0
        categoria_ids = request.form.getlist('categorias')
        drive_links_raw = request.form.get('drive_links', '').strip()

        if not nombre or not marca or not precio_str:
            flash('Nombre, Marca y Precio son obligatorios.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=product)

        try:
            precio = float(precio_str)
            if precio < 0:
                raise ValueError()
        except ValueError:
            flash('El precio ingresado no es válido.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=product)

        ProductModel.update(
            product_id=product_id,
            nombre=nombre,
            marca=marca,
            precio=precio,
            descripcion=descripcion,
            disponible=disponible,
            categoria_ids=categoria_ids
        )

        # 1. Procesar imágenes locales adicionales
        files = request.files.getlist('imagenes')
        for file in files:
            if file and file.filename:
                try:
                    filename = ImageService.save_image(file)
                    if filename:
                        ProductModel.add_image(
                            product_id=product_id,
                            ruta_o_url=filename,
                            origen='local',
                            es_principal=0
                        )
                except Exception as e:
                    flash(f'Error al subir imagen adicional: {str(e)}', 'warning')

        # 2. Procesar nuevos enlaces de Google Drive
        if drive_links_raw:
            drive_lines = [l.strip() for l in drive_links_raw.replace(',', '\n').split('\n') if l.strip()]
            for link in drive_lines:
                drive_id = ImageService.extract_drive_id(link)
                if drive_id:
                    ProductModel.add_image(
                        product_id=product_id,
                        ruta_o_url=drive_id,
                        origen='drive',
                        es_principal=0
                    )

        flash(f'¡Producto "{nombre}" actualizado exitosamente!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/product_form.html', categories=categories, product=product)

@admin_bp.route('/productos/eliminar/<int:product_id>', methods=['POST'], strict_slashes=False)
@login_required
def product_delete(product_id):
    product = ProductModel.get_by_id(product_id)
    if product:
        for img in product['imagenes']:
            if img['origen'] == 'local':
                ImageService.delete_local_file(img['ruta_o_url'])
        
        ProductModel.delete(product_id)
        flash(f'Producto "{product["nombre"]}" eliminado correctamente.', 'info')
    else:
        flash('Producto no encontrado.', 'danger')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/productos/toggle-disponible/<int:product_id>', methods=['POST'], strict_slashes=False)
@login_required
def product_toggle(product_id):
    ProductModel.toggle_disponible(product_id)
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/productos/<int:product_id>/imagen-principal/<int:image_id>', methods=['POST'], strict_slashes=False)
@login_required
def set_main_image(product_id, image_id):
    ProductModel.set_main_image(product_id, image_id)
    flash('Imagen principal actualizada.', 'success')
    return redirect(url_for('admin.product_edit', product_id=product_id))

@admin_bp.route('/productos/<int:product_id>/eliminar-imagen/<int:image_id>', methods=['POST'], strict_slashes=False)
@login_required
def delete_image(product_id, image_id):
    img = ProductModel.delete_image(product_id, image_id)
    if img and img.get('origen') == 'local':
        ImageService.delete_local_file(img['ruta_o_url'])
    flash('Imagen eliminada.', 'info')
    return redirect(url_for('admin.product_edit', product_id=product_id))

# -------------------------------------------------------------
# 3. Gestión de Banners Rotativos
# -------------------------------------------------------------
@admin_bp.route('/banners', strict_slashes=False)
@login_required
def banners_list():
    banners = BannerModel.get_all()
    return render_template('admin/banners.html', banners=banners)

@admin_bp.route('/banners/nuevo', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def banner_new():
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        subtitulo = request.form.get('subtitulo', '').strip()
        texto_boton = request.form.get('texto_boton', 'Explorar Colección').strip()
        enlace_url = request.form.get('enlace_url', '#catalogo-seccion').strip()
        orden = int(request.form.get('orden', 0) or 0)
        activo = 1 if request.form.get('activo') else 0
        
        drive_link = request.form.get('drive_link', '').strip()
        imagen_file = request.files.get('imagen_archivo')

        imagen_url = 'banner.jpg'
        origen = 'local'

        if drive_link:
            imagen_url = ImageService.extract_drive_id(drive_link)
            origen = 'drive'
        elif imagen_file and imagen_file.filename:
            try:
                filename = ImageService.save_image(imagen_file)
                if filename:
                    imagen_url = filename
                    origen = 'local'
            except Exception as e:
                flash(f'Error al procesar la imagen del banner: {str(e)}', 'danger')
                return render_template('admin/banner_form.html', banner=None)

        if not titulo:
            flash('El título del banner es obligatorio.', 'danger')
            return render_template('admin/banner_form.html', banner=None)

        BannerModel.create(
            titulo=titulo,
            subtitulo=subtitulo,
            texto_boton=texto_boton,
            enlace_url=enlace_url,
            imagen_url=imagen_url,
            origen=origen,
            orden=orden,
            activo=activo
        )
        flash('¡Banner creado exitosamente!', 'success')
        return redirect(url_for('admin.banners_list'))

    return render_template('admin/banner_form.html', banner=None)

@admin_bp.route('/banners/editar/<int:banner_id>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def banner_edit(banner_id):
    banner = BannerModel.get_by_id(banner_id)
    if not banner:
        flash('El banner no existe.', 'danger')
        return redirect(url_for('admin.banners_list'))

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        subtitulo = request.form.get('subtitulo', '').strip()
        texto_boton = request.form.get('texto_boton', 'Explorar Colección').strip()
        enlace_url = request.form.get('enlace_url', '#catalogo-seccion').strip()
        orden = int(request.form.get('orden', 0) or 0)
        activo = 1 if request.form.get('activo') else 0
        
        drive_link = request.form.get('drive_link', '').strip()
        imagen_file = request.files.get('imagen_archivo')

        imagen_url = None
        origen = banner['origen']

        if drive_link:
            imagen_url = ImageService.extract_drive_id(drive_link)
            origen = 'drive'
        elif imagen_file and imagen_file.filename:
            try:
                filename = ImageService.save_image(imagen_file)
                if filename:
                    imagen_url = filename
                    origen = 'local'
            except Exception as e:
                flash(f'Error al procesar la imagen: {str(e)}', 'danger')

        if not titulo:
            flash('El título del banner es obligatorio.', 'danger')
            return render_template('admin/banner_form.html', banner=banner)

        BannerModel.update(
            banner_id=banner_id,
            titulo=titulo,
            subtitulo=subtitulo,
            texto_boton=texto_boton,
            enlace_url=enlace_url,
            imagen_url=imagen_url,
            origen=origen,
            orden=orden,
            activo=activo
        )
        flash('¡Banner actualizado exitosamente!', 'success')
        return redirect(url_for('admin.banners_list'))

    return render_template('admin/banner_form.html', banner=banner)

@admin_bp.route('/banners/toggle/<int:banner_id>', methods=['POST'], strict_slashes=False)
@login_required
def banner_toggle(banner_id):
    BannerModel.toggle_active(banner_id)
    return redirect(url_for('admin.banners_list'))

@admin_bp.route('/banners/eliminar/<int:banner_id>', methods=['POST'], strict_slashes=False)
@login_required
def banner_delete(banner_id):
    BannerModel.delete(banner_id)
    flash('Banner eliminado correctamente.', 'info')
    return redirect(url_for('admin.banners_list'))