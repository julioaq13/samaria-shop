/**
 * SAMARIA - JavaScript Oficial
 * Carrusel de Banners Automático, Menú Móvil y Modal de Calzado Interactivo
 */

document.addEventListener('DOMContentLoaded', () => {
    
    // -------------------------------------------------------------
    // 1. Menú Móvil Hamburguesa
    // -------------------------------------------------------------
    const menuToggle = document.getElementById('mobileMenuToggle');
    const mainNav = document.getElementById('mainNavigation');

    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            mainNav.classList.toggle('show');
            const icon = menuToggle.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-xmark');
            }
        });

        // Cerrar menú al hacer clic en enlaces o fuera
        document.addEventListener('click', (e) => {
            if (!mainNav.contains(e.target) && !menuToggle.contains(e.target)) {
                mainNav.classList.remove('show');
                const icon = menuToggle.querySelector('i');
                if (icon) {
                    icon.classList.add('fa-bars');
                    icon.classList.remove('fa-xmark');
                }
            }
        });
    }

    // -------------------------------------------------------------
    // 2. Carrusel de Banners Rotativo Automático
    // -------------------------------------------------------------
    const slides = document.querySelectorAll('.hero-slide');
    const prevBtn = document.getElementById('carouselPrevBtn');
    const nextBtn = document.getElementById('carouselNextBtn');
    const dots = document.querySelectorAll('.carousel-dots .dot');
    const carouselContainer = document.getElementById('heroCarouselSection');

    let currentSlide = 0;
    let slideInterval = null;
    const slideDelay = 5000; // 5 segundos

    function showSlide(index) {
        if (!slides || slides.length === 0) return;
        
        slides.forEach(s => s.classList.remove('active'));
        if (dots && dots.length > 0) {
            dots.forEach(d => d.classList.remove('active'));
        }

        currentSlide = (index + slides.length) % slides.length;
        
        slides[currentSlide].classList.add('active');
        if (dots && dots[currentSlide]) {
            dots[currentSlide].classList.add('active');
        }
    }

    function startAutoSlide() {
        if (slides.length <= 1) return;
        stopAutoSlide();
        slideInterval = setInterval(() => {
            showSlide(currentSlide + 1);
        }, slideDelay);
    }

    function stopAutoSlide() {
        if (slideInterval) {
            clearInterval(slideInterval);
            slideInterval = null;
        }
    }

    if (slides.length > 1) {
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                showSlide(currentSlide + 1);
                startAutoSlide();
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                showSlide(currentSlide - 1);
                startAutoSlide();
            });
        }

        dots.forEach((dot, idx) => {
            dot.addEventListener('click', () => {
                showSlide(idx);
                startAutoSlide();
            });
        });

        // Pausar al pasar el mouse por encima
        if (carouselContainer) {
            carouselContainer.addEventListener('mouseenter', stopAutoSlide);
            carouselContainer.addEventListener('mouseleave', startAutoSlide);

            // Soporte gestos táctiles (Swipe en móviles)
            let touchStartX = 0;
            let touchEndX = 0;

            carouselContainer.addEventListener('touchstart', (e) => {
                touchStartX = e.changedTouches[0].screenX;
                stopAutoSlide();
            }, { passive: true });

            carouselContainer.addEventListener('touchend', (e) => {
                touchEndX = e.changedTouches[0].screenX;
                const diff = touchStartX - touchEndX;
                if (Math.abs(diff) > 45) {
                    if (diff > 0) {
                        showSlide(currentSlide + 1); // Swipe izquierda -> siguiente
                    } else {
                        showSlide(currentSlide - 1); // Swipe derecha -> anterior
                    }
                }
                startAutoSlide();
            }, { passive: true });
        }

        // Iniciar rotación automática
        startAutoSlide();
    }

    // -------------------------------------------------------------
    // 3. Modal Interactivo de Calzado
    // -------------------------------------------------------------
    const modal = document.getElementById('productDetailModal');
    const closeBtn = document.getElementById('modalCloseBtn');
    const modalBody = document.getElementById('modalContentBody');

    // Delegación de eventos para abrir modal desde las tarjetas
    document.addEventListener('click', (e) => {
        const trigger = e.target.closest('.open-detail-modal, .card-image-wrap, .card-title');
        if (trigger) {
            const card = trigger.closest('.product-card');
            if (card) {
                const prodId = card.dataset.id;
                if (prodId) {
                    openProductModal(prodId);
                }
            }
        }
    });

    if (closeBtn && modal) {
        closeBtn.addEventListener('click', closeProductModal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeProductModal();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                closeProductModal();
            }
        });
    }

    function openProductModal(productId) {
        if (!modal || !modalBody) return;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';

        modalBody.innerHTML = `
            <div class="modal-loader">
                <i class="fa-solid fa-spinner fa-spin fa-2x"></i>
                <p style="margin-top: 12px; font-weight: 500;">Cargando información del calzado...</p>
            </div>
        `;

        fetch(`/producto/${productId}?format=json`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => {
            if (!res.ok) throw new Error('Error al cargar datos');
            return res.json();
        })
        .then(prod => {
            renderModalContent(prod);
        })
        .catch(err => {
            console.error(err);
            modalBody.innerHTML = `
                <div style="text-align: center; padding: 40px 20px;">
                    <i class="fa-solid fa-circle-exclamation fa-2x" style="color: #e63946; margin-bottom: 12px;"></i>
                    <p>No se pudo cargar la información del producto. Inténtelo nuevamente.</p>
                </div>
            `;
        });
    }

    function renderModalContent(prod) {
        const precioFormatted = new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            maximumFractionDigits: 0
        }).format(prod.precio);

        // Resolver fotos
        let mainImgUrl = '/static/img/placeholder_shoe.png';
        if (prod.imagenes && prod.imagenes.length > 0) {
            const mainImg = prod.imagenes.find(i => i.es_principal === 1) || prod.imagenes[0];
            mainImgUrl = resolveImgUrl(mainImg);
        }

        let thumbsHtml = '';
        if (prod.imagenes && prod.imagenes.length > 1) {
            thumbsHtml = `
                <div class="modal-gallery-thumbs">
                    ${prod.imagenes.map((img, idx) => {
                        const u = resolveImgUrl(img);
                        return `
                            <button class="modal-thumb-btn ${idx === 0 ? 'active' : ''}" onclick="changeModalThumb('${u}', this)">
                                <img src="${u}" alt="Foto ${idx+1}">
                            </button>
                        `;
                    }).join('')}
                </div>
            `;
        }

        const tagsHtml = (prod.categorias || []).map(cat => `
            <span class="cat-tag">${cat.nombre}</span>
        `).join('');

        const waText = encodeURIComponent(`Hola SAMARIA, me interesa consultar sobre el calzado: ${prod.nombre} (${prod.marca}) por valor de ${precioFormatted}`);
        const waUrl = `https://wa.me/?text=${waText}`;

        modalBody.innerHTML = `
            <div class="modal-product-grid">
                <div class="modal-gallery-col">
                    <div class="modal-gallery-main">
                        <img src="${mainImgUrl}" id="modalMainImg" alt="${prod.nombre}">
                    </div>
                    ${thumbsHtml}
                </div>
                <div class="modal-info-col">
                    <span class="modal-brand">${prod.marca}</span>
                    <h2 class="modal-title">${prod.nombre}</h2>
                    <div class="modal-price">${precioFormatted}</div>
                    
                    <div class="card-categories-tags">
                        ${tagsHtml}
                    </div>

                    <div class="modal-desc">
                        <p>${prod.descripcion || 'Calzado de alta calidad con acabados finos y confort superior.'}</p>
                    </div>

                    <div style="display:flex; flex-direction:column; gap:12px; margin-top: 20px;">
                        <a href="${waUrl}" target="_blank" class="btn-whatsapp">
                            <i class="fa-brands fa-whatsapp"></i> Consultar por WhatsApp
                        </a>
                        <a href="/producto/${prod.id}" class="btn btn-secondary" style="text-align:center;">
                            Ver Ficha Individual
                        </a>
                    </div>
                </div>
            </div>
        `;
    }

    function resolveImgUrl(imgObj) {
        if (!imgObj || !imgObj.ruta_o_url) return '/static/img/placeholder_shoe.png';
        if (imgObj.origen === 'drive' || imgObj.ruta_o_url.includes('drive.google.com')) {
            const match = imgObj.ruta_o_url.match(/\/file\/d\/([a-zA-Z0-9_-]+)/) || 
                          imgObj.ruta_o_url.match(/[?&]id=([a-zA-Z0-9_-]+)/) ||
                          imgObj.ruta_o_url.match(/\/d\/([a-zA-Z0-9_-]+)/);
            const driveId = match ? match[1] : imgObj.ruta_o_url;
            return `https://lh3.googleusercontent.com/d/${driveId}`;
        }
        if (imgObj.origen === 'url' || imgObj.ruta_o_url.startsWith('http')) {
            return imgObj.ruta_o_url;
        }
        return `/static/img/productos/${imgObj.ruta_o_url}`;
    }

    window.changeModalThumb = function(url, btn) {
        const mainImg = document.getElementById('modalMainImg');
        if (mainImg) mainImg.src = url;
        document.querySelectorAll('.modal-thumb-btn').forEach(b => b.classList.remove('active'));
        if (btn) btn.classList.add('active');
    };

    function closeProductModal() {
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

});