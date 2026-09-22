# SAMARIA - Tienda y Catálogo Web de Calzado 👠👞

Aplicación web completa, funcional y responsive desarrollada en **Python (Flask)**, **SQLite**, **HTML5**, **CSS3** y **JavaScript moderno**. Incluye catálogo público con filtros por categoría y búsqueda, además de un panel de administración intuitivo y seguro para gestionar productos, precios, disponibilidad e imágenes sin necesidad de programar.

---

## 📋 Tabla de Contenidos
- [Características Principales](#-características-principales)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación y Configuración Paso a Paso](#-instalación-y-configuración-paso-a-paso)
- [Ejecución de la Aplicación](#-ejecución-de-la-aplicación)
- [Acceso y Rutas](#-acceso-y-rutas)
- [Panel de Administración y Credenciales](#-panel-de-administración-y-credenciales)
- [Gestión de Imágenes y Extensibilidad (Google Drive)](#-gestión-de-imágenes-y-extensibilidad-google-drive)
- [Preparación para WhatsApp / Estados](#-preparación-para-whatsapp--estados)
- [Ejecución de Pruebas Automatizadas](#-ejecución-de-pruebas-automatizadas)

---

## 🌟 Características Principales

### Catálogo Público
- **Diseño Responsive:** Adaptado automáticamente para computadores, tablets y celulares sin desbordamiento horizontal.
- **Encabezado Elegante:** Barra superior oscura con el logo oficial de **SAMARIA** (`static/img/logo.png`).
- **Navegación Exclusiva (5 Opciones):**
  1. `NUEVO` (`/categoria/nuevo`): Título "Nuevos productos".
  2. `CATÁLOGO` (`/` o `/catalogo`): Título "Todos nuestros productos".
  3. `HOMBRE` (`/categoria/hombre`): Título "Calzado para Hombre".
  4. `MUJER` (`/categoria/mujer`): Título "Calzado para Mujer".
  5. `PROMOS` (`/categoria/promo`): Título "Promociones".
- **Banner Principal:** Banner personalizable con mensajes y llamados a la acción.
- **Buscador en Vivo:** Permite buscar productos por **Nombre** y **Marca** con limpieza rápida.
- **Tarjetas de Calzado:** Muestran imagen con efecto hover, nombre, marca en mayúsculas, precio formateado en moneda, badges de categoría (`NUEVO`, `OFERTA`) e indicador de disponibilidad (`Disponible` / `Agotado`).
- **Modal Interactivo:** Al hacer clic en un producto o en "Ver Más", se abre una ventana modal con carrusel de fotos, descripción detallada y botón directo para **consultar por WhatsApp**.

### Panel de Administración (`/admin`)
- **Diseñado para usuarios no técnicos:** Interfaz gráfica limpia, amigable y en español.
- **Seguridad:** Autenticación con contraseña hasheada (`werkzeug.security`) y protección de sesión.
- **Dashboard:** Métricas en tiempo real (Total Calzado, Productos Activos, En Promoción).
- **Gestión Completa (CRUD):**
  - **Crear Producto:** Nombre, Marca, Precio, Descripción, selección múltiple de categorías (`Nuevo`, `Hombre`, `Mujer`, `Promo`) mediante casillas de verificación, y subida múltiple de imágenes.
  - **Editar Producto:** Modificar cualquier campo, subir fotos adicionales, marcar cuál es la foto principal y eliminar fotos individuales.
  - **Activar / Desactivar en 1 Clic:** Oculta o muestra el calzado en el catálogo público inmediatamente.
  - **Eliminar Producto:** Borra el producto y limpia los archivos de imagen locales asociados.

---

## 📂 Estructura del Proyecto

```text
samaria_shop/
├── app/
│   ├── __init__.py                 # Fábrica de aplicación Flask y filtros Jinja
│   ├── config.py                   # Configuración (.env, rutas, límites de subida)
│   ├── database.py                 # Conexión SQLite, row_factory y helpers SQL
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                 # Modelo y autenticación de administradores
│   │   ├── category.py             # Consultas de categorías
│   │   ├── product.py              # Operaciones CRUD, filtros y estadísticas
│   │   └── publication.py          # Arquitectura para programación WhatsApp
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── public.py               # Rutas públicas (catálogo, categorías, búsqueda)
│   │   ├── admin.py                # Rutas del panel administrativo (CRUD)
│   │   └── auth.py                 # Login y logout
│   ├── services/
│   │   ├── __init__.py
│   │   ├── image_service.py        # Validación, nombrado seguro y abstracción (Local/Drive)
│   │   └── scheduler_service.py    # Interfaz para módulo futuro de WhatsApp
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css           # Estilos públicos (Header negro, grid responsive)
│   │   │   └── admin.css           # Estilos limpios para el panel de administración
│   │   ├── js/
│   │   │   ├── main.js             # Menú móvil hamburguesa, modal AJAX
│   │   │   └── admin.js            # Previsualización de imágenes y filtro rápido
│   │   └── img/
│   │       ├── logo.png            # Logo de la marca SAMARIA
│   │       ├── banner.jpg          # Banner principal del catálogo
│   │       ├── placeholder_shoe.png# Imagen por defecto si no hay foto
│   │       └── productos/          # Almacenamiento local de fotografías subidas
│   └── templates/
│       ├── base.html               # Plantilla pública base
│       ├── catalog.html            # Catálogo con buscador, filtros y tarjetas
│       ├── product_detail.html     # Vista detallada de calzado
│       └── admin/
│           ├── base_admin.html     # Plantilla base administrativa
│           ├── login.html          # Pantalla de inicio de sesión
│           ├── dashboard.html      # Métricas y tabla de productos
│           └── product_form.html   # Formulario unificado de creación y edición
├── database/
│   └── schema.sql                  # Definición DDL normalizada de SQLite
├── instance/
│   └── samaria.db                  # Base de datos SQLite (se genera automáticamente)
├── seed_data.py                    # Script con calzado de ejemplo y usuario admin
├── run.py                          # Script de ejecución del servidor Flask
├── test_app.py                     # Suite de pruebas automatizadas
├── requirements.txt                # Dependencias del proyecto
├── .env.example                    # Plantilla de variables de entorno
└── README.md                       # Documentación del proyecto
```

---

## 🛠️ Requisitos Previos

- **Python 3.10 o superior** instalado en el sistema.
- **pip** (gestor de paquetes de Python).

---

## 🚀 Instalación y Configuración Paso a Paso

### 1. Ubicarse en la carpeta del proyecto
Abre una terminal (PowerShell, CMD o Bash) y navega al directorio del proyecto:
```bash
cd C:\Users\TL007\.gemini\antigravity\scratch\samaria_shop
```

### 2. Crear y activar el entorno virtual (Recomendado)
**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(Si usas CMD escribe `.\venv\Scripts\activate.bat`, o en Linux/macOS `source venv/bin/activate`)*

### 3. Instalar dependencias
Instala los paquetes necesarios desde `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea tu archivo `.env` a partir de `.env.example`:
```bash
copy .env.example .env
```
*(Puedes editar `.env` si deseas cambiar la contraseña o usuario del administrador)*

### 5. Inicializar la Base de Datos y cargar datos de muestra
Ejecuta el script seeder para crear las tablas, el usuario administrador y productos de calzado de ejemplo con sus imágenes:
```bash
python seed_data.py
```

---

## 💻 Ejecución de la Aplicación

Inicia el servidor web ejecutando:
```bash
python run.py
```

El servidor estará disponible en tu navegador en:
👉 **http://127.0.0.1:5000**

---

## 🌐 Acceso y Rutas

### Rutas Públicas:
| Ruta | Descripción |
| :--- | :--- |
| **`http://127.0.0.1:5000/`** | Catálogo completo ("Todos nuestros productos") con buscador |
| **`http://127.0.0.1:5000/categoria/nuevo`** | Calzado en categoría "Nuevos productos" |
| **`http://127.0.0.1:5000/categoria/hombre`** | Calzado para Hombre |
| **`http://127.0.0.1:5000/categoria/mujer`** | Calzado para Mujer |
| **`http://127.0.0.1:5000/categoria/promo`** | Calzado en Promoción / Descuento |
| **`http://127.0.0.1:5000/producto/<id>`** | Ficha completa individual del calzado |

---

## 🔐 Panel de Administración y Credenciales

Accede a la interfaz de administración en:
👉 **http://127.0.0.1:5000/admin**

### Credenciales por Defecto:
- **Usuario:** `admin`
- **Contraseña:** `admin123`

*(Estas credenciales pueden modificarse desde el archivo `.env` o la base de datos)*

---

## 📷 Gestión de Imágenes y Extensibilidad (Google Drive)

1. **Almacenamiento Local Actual:**
   - Las imágenes subidas desde el panel se guardan de forma segura en `app/static/img/productos/` con nombres únicos generados automáticamente.
   - En SQLite solo se guarda la referencia del nombre de archivo.
   - Formatos soportados: `.jpg`, `.jpeg`, `.png`, `.webp`.

2. **Arquitectura Preparada para Google Drive:**
   - La tabla `imagenes` incluye la columna `origen` (`local`, `drive`, `url`).
   - El servicio `ImageService.get_image_url(image_record)` resuelve de manera transparente URLs de Drive (`https://drive.google.com/uc?export=view&id=...`) o URLs externas sin necesidad de modificar plantillas HTML ni controladores cuando se integre la API de Google Drive.

---

## 📱 Preparación para WhatsApp / Estados

- La base de datos incluye la tabla normalizada `programacion_publicaciones` (id, titulo, mensaje, dias_semana, hora, activo, producto_id, imagen_url).
- El modelo `PublicationModel` y el servicio `SchedulerService` ya están implementados para permitir la programación de estados de WhatsApp en fases posteriores sin tocar la lógica del catálogo ni de los productos.

---

## 🧪 Ejecución de Pruebas Automatizadas

Para validar que todas las rutas, filtros, seguridad y operaciones CRUD funcionan a la perfección:
```bash
python test_app.py
```
Todas las 11 pruebas unitarias deben ejecutarse y reportar `OK`.