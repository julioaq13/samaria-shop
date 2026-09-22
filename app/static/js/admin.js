/**
 * SAMARIA - JavaScript de Administración
 * Previsualización de imágenes, filtrado de tabla en vivo
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Filtrado rápido de tabla de productos en dashboard
    const searchInput = document.getElementById('adminTableSearch');
    const table = document.getElementById('productsTable');

    if (searchInput && table) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const rows = table.querySelectorAll('tbody tr.product-row');

            rows.forEach(row => {
                const name = row.querySelector('.td-name')?.textContent.toLowerCase() || '';
                const brand = row.querySelector('.td-brand')?.textContent.toLowerCase() || '';
                
                if (name.includes(query) || brand.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // 2. Previsualización de imágenes subidas en el formulario
    const fileInput = document.getElementById('imageFileInput');
    const previewContainer = document.getElementById('imagePreviewContainer');

    if (fileInput && previewContainer) {
        fileInput.addEventListener('change', () => {
            previewContainer.innerHTML = '';
            const files = fileInput.files;

            if (files && files.length > 0) {
                Array.from(files).forEach((file, index) => {
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = (e) => {
                            const wrap = document.createElement('div');
                            wrap.className = 'preview-item';
                            wrap.style.position = 'relative';

                            const img = document.createElement('img');
                            img.src = e.target.result;
                            img.className = 'preview-thumb';
                            img.title = file.name;

                            wrap.appendChild(img);
                            previewContainer.appendChild(wrap);
                        };
                        reader.readAsDataURL(file);
                    }
                });
            }
        });
    }
});