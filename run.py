"""
Punto de Entrada de la Aplicación SAMARIA.
Ejecuta el servidor de desarrollo Flask.
"""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"==================================================")
    print(f"  SAMARIA - Tienda y Catálogo de Calzado")
    print(f"  Servidor iniciado en: http://127.0.0.1:{port}")
    print(f"  Panel de Administración: http://127.0.0.1:{port}/admin")
    print(f"  Credenciales: admin / admin123")
    print(f"==================================================")
    app.run(host='127.0.0.1', port=port, debug=False)