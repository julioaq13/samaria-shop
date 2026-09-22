-- Esquema Normalizado SQLite para SAMARIA Tienda de Calzado

-- Tabla de Usuarios Administradores
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nombre TEXT,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Categorías
CREATE TABLE IF NOT EXISTS categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    descripcion TEXT
);

-- Tabla de Productos
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    marca TEXT NOT NULL,
    precio REAL NOT NULL,
    descripcion TEXT,
    disponible INTEGER NOT NULL DEFAULT 1,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Relación N a M entre Productos y Categorías
CREATE TABLE IF NOT EXISTS producto_categoria (
    producto_id INTEGER NOT NULL,
    categoria_id INTEGER NOT NULL,
    PRIMARY KEY (producto_id, categoria_id),
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE CASCADE
);

-- Tabla de Imágenes de Productos (Soporta Local, Google Drive y URLs externas)
CREATE TABLE IF NOT EXISTS imagenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    ruta_o_url TEXT NOT NULL,
    origen TEXT NOT NULL DEFAULT 'local', -- 'local', 'drive', 'url'
    es_principal INTEGER NOT NULL DEFAULT 0,
    orden INTEGER NOT NULL DEFAULT 0,
    fecha_subida DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
);

-- Tabla de Banners Rotativos del Catálogo
CREATE TABLE IF NOT EXISTS banners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    subtitulo TEXT,
    texto_boton TEXT DEFAULT 'Explorar Colección',
    enlace_url TEXT DEFAULT '#catalogo-seccion',
    imagen_url TEXT NOT NULL,
    origen TEXT NOT NULL DEFAULT 'local', -- 'local', 'drive', 'url'
    orden INTEGER NOT NULL DEFAULT 0,
    activo INTEGER NOT NULL DEFAULT 1,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Preparación para Publicaciones / Estados WhatsApp (Módulo futuro)
CREATE TABLE IF NOT EXISTS programacion_publicaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    mensaje TEXT,
    dias_semana TEXT NOT NULL, -- Ej: 'Lunes,Miércoles,Viernes'
    hora TEXT NOT NULL,        -- Ej: '10:00'
    activo INTEGER NOT NULL DEFAULT 1,
    producto_id INTEGER,
    imagen_url TEXT,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE SET NULL
);

-- Índices de consulta rápida
CREATE INDEX IF NOT EXISTS idx_productos_disponible ON productos(disponible);
CREATE INDEX IF NOT EXISTS idx_productos_marca ON productos(marca);
CREATE INDEX IF NOT EXISTS idx_imagenes_producto ON imagenes(producto_id);
CREATE INDEX IF NOT EXISTS idx_prod_cat_cat ON producto_categoria(categoria_id);
CREATE INDEX IF NOT EXISTS idx_banners_activo ON banners(activo, orden);