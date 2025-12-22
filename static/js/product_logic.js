/**
 * product_logic.js
 * Lógica compartida para página de detalle de producto
 * Versión sin manejo de preview - eso lo hace el HTML
 */

window.priceTiers = [];
window.basePrice = 0;
window.selectedColorSlug = '';
window.selectedSizeSlug = '';
window.categorySlug = '';
window.productSlug = '';
window.addToCartUrl = '';

// ====================================================================
// A. CARGAR DATOS DEL PRODUCTO DE FORMA SEGURA
// ====================================================================

function loadProductData() {
    const dataContainer = document.getElementById('product-data');
    if (!dataContainer) {
        console.error('Contenedor de datos (#product-data) no encontrado.');
        return;
    }

    // 1. Precio base
    const basePriceStr = dataContainer.dataset.basePrice;
    window.basePrice = parseFloat(basePriceStr) || 0;

    // 2. Product data y URL del carrito
    window.categorySlug = dataContainer.dataset.categorySlug || '';
    window.productSlug = dataContainer.dataset.productSlug || '';
    window.addToCartUrl = dataContainer.dataset.addToCartUrl || '';

    console.log('✅ Category slug:', window.categorySlug);
    console.log('✅ Product slug:', window.productSlug);
    console.log('✅ Add to cart URL:', window.addToCartUrl);

    // 3. Tiers desde <script type="application/json"> (método infalible)
    const scriptId = dataContainer.dataset.tiersId;
    const scriptEl = document.getElementById(scriptId);

    if (scriptEl) {
        try {
            window.priceTiers = JSON.parse(scriptEl.textContent.trim());
            console.log(`Tiers cargados correctamente (${window.priceTiers.length} niveles)`);
        } catch (e) {
            console.error('Error al parsear JSON de tiers:', e);
            window.priceTiers = [];
        }
    } else {
        console.warn('No se encontró script de tiers. Usando tiers vacíos.');
        window.priceTiers = [];
    }
}

// ====================================================================
// B. ACTUALIZAR PRECIO Y RESALTAR TIER ACTIVO
// ====================================================================

function updatePriceAndHighlight() {
    const quantityInput = document.getElementById('quantity');
    const unitPriceDisplay = document.getElementById('unit-price');
    const discountBadge = document.getElementById('discount-badge');
    const totalPriceEl = document.getElementById('total-price');
    const tierRows = document.querySelectorAll('[data-tier-min]');

    if (!quantityInput) return;

    const quantity = parseInt(quantityInput.value, 10) || 1;
    let unitPrice = window.basePrice;
    let discount = 0;
    let activeMinQuantity = null;

    // Buscar tier activo
    for (const tier of window.priceTiers) {
        const min = tier.min_quantity ?? tier.min ?? 0;
        const max = tier.max_quantity ?? tier.max ?? Infinity;

        if (quantity >= min && quantity <= max) {
            unitPrice = tier.price_per_unit ?? tier.unit_price ?? tier.price ?? window.basePrice;
            discount = tier.discount_percentage ?? tier.discount_percent ?? tier.discount ?? 0;
            activeMinQuantity = min.toString();
            break;
        }
    }

    // Resaltar fila activa
    tierRows.forEach(row => {
        const rowMin = row.dataset.tierMin;
        if (rowMin === activeMinQuantity) {
            row.classList.add('tier-row-active');
        } else {
            row.classList.remove('tier-row-active');
        }
    });

    // Actualizar precios en pantalla
    const total = (unitPrice * quantity).toFixed(2);

    if (unitPriceDisplay) unitPriceDisplay.textContent = `S/ ${unitPrice.toFixed(2)}`;
    if (discountBadge) discountBadge.textContent = `${discount}%`;
    if (totalPriceEl) totalPriceEl.textContent = `S/ ${total}`;
}

// ====================================================================
// C. SELECCIÓN DE COLOR Y TALLA (ropa, etc.)
// ====================================================================

function selectColor(colorSlug, colorName) {
    window.selectedColorSlug = colorSlug;

    document.querySelectorAll('.color-swatch').forEach(btn => {
        if (btn.dataset.colorSlug === colorSlug) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    const display = document.getElementById('selected-color-name');
    if (display) display.textContent = colorName;
}

function selectSize(sizeSlug, sizeName) {
    window.selectedSizeSlug = sizeSlug;

    document.querySelectorAll('.size-btn').forEach(btn => {
        if (btn.dataset.sizeSlug === sizeSlug) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    const display = document.getElementById('selected-size-name');
    if (display) display.textContent = sizeName;
}

// ====================================================================
// D. AÑADIR AL CARRITO
// ====================================================================

// Flag global para prevenir clics múltiples
if (typeof window.isAddingToCart === 'undefined') {
    window.isAddingToCart = false;
}

async function addToCart() {
    // Prevenir ejecuciones múltiples
    if (window.isAddingToCart) {
        console.log('⚠️ Ya se está agregando al carrito, espera...');
        return;
    }

    console.log('🛒 addToCart llamado');

    // Validar que tengamos la URL
    if (!window.addToCartUrl) {
        alert('❌ Error: URL del carrito no disponible');
        console.error('addToCartUrl no está definida');
        return;
    }

    // Validar category y product slugs
    if (!window.categorySlug || !window.productSlug) {
        alert('❌ Error: Información del producto no disponible');
        console.error('Category o Product slug no definidos');
        return;
    }

    // Validar color (si aplica)
    if (window.selectedColorSlug === '' && document.querySelector('.color-swatch')) {
        alert('❌ Por favor selecciona un color');
        return;
    }

    // Validar talla (si aplica)
    if (window.selectedSizeSlug === '' && document.querySelector('.size-btn')) {
        alert('❌ Por favor selecciona una talla');
        return;
    }

    // Validar cantidad
    const quantityInput = document.getElementById('quantity');
    const quantity = parseInt(quantityInput.value);

    if (!quantity || quantity < 1) {
        alert('❌ Por favor ingresa una cantidad válida');
        return;
    }

    // Validar archivo (si se requiere)
    const fileInput = document.getElementById('file-upload-input');
    const fileRequired = fileInput && fileInput.hasAttribute('required');

    if (fileRequired && (!fileInput.files || fileInput.files.length === 0)) {
        alert('❌ Por favor sube tu diseño para continuar');
        return;
    }

    // Marcar que estamos agregando al carrito
    window.isAddingToCart = true;

    // Deshabilitar botón
    const addBtn = document.getElementById('add-to-cart-btn') || document.getElementById('add-to-cart');
    if (!addBtn) {
        window.isAddingToCart = false;
        return;
    }

    const originalText = addBtn.innerHTML;
    addBtn.disabled = true;
    addBtn.innerHTML = '⏳ Agregando...';

    // Preparar FormData para enviar archivos
    const formData = new FormData();
    formData.append('category_slug', window.categorySlug);
    formData.append('product_slug', window.productSlug);
    formData.append('quantity', quantity.toString());

    // Check for template slug from hidden input (set by inline template selector)
    const templateInput = document.getElementById('selected-template');
    const designTypeInput = document.getElementById('design-type');

    if (templateInput && templateInput.value) {
        formData.append('template_slug', templateInput.value);
        formData.append('design_type', designTypeInput ? designTypeInput.value : 'template');
    } else {
        formData.append('design_type', 'custom');
    }

    // Check for file from sessionStorage (uploaded via template gallery)
    const designDataFromGallery = sessionStorage.getItem('uploadedDesignData');
    const designNameFromGallery = sessionStorage.getItem('uploadedDesignName');
    const designTypeFromGallery = sessionStorage.getItem('uploadedDesignType');

    // Agregar archivo - priorizar sessionStorage, luego input file
    if (designDataFromGallery && designNameFromGallery) {
        // Convert base64 data URL to Blob/File
        try {
            const base64Response = await fetch(designDataFromGallery);
            const blob = await base64Response.blob();
            const file = new File([blob], designNameFromGallery, { type: designTypeFromGallery || 'application/octet-stream' });
            formData.append('design_file', file);
            console.log('📎 Archivo del template gallery adjuntado:', designNameFromGallery);
        } catch (e) {
            console.error('Error convirtiendo archivo de sessionStorage:', e);
        }
    } else if (fileInput && fileInput.files && fileInput.files.length > 0) {
        formData.append('design_file', fileInput.files[0]);
    }

    // Agregar color y talla solo si fueron seleccionados
    if (window.selectedColorSlug) {
        formData.append('color_slug', window.selectedColorSlug);
    }
    if (window.selectedSizeSlug) {
        formData.append('size_slug', window.selectedSizeSlug);
    }

    console.log('📦 Enviando al servidor:', {
        category_slug: window.categorySlug,
        product_slug: window.productSlug,
        quantity: quantity,
        color: window.selectedColorSlug,
        size: window.selectedSizeSlug,
        has_file_input: fileInput && fileInput.files && fileInput.files.length > 0,
        has_file_from_gallery: !!(designDataFromGallery && designNameFromGallery)
    });

    // Hacer petición al servidor
    fetch(window.addToCartUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log('📥 Respuesta del servidor:', data);

            if (data.success) {
                // Clear sessionStorage design data
                sessionStorage.removeItem('uploadedDesignName');
                sessionStorage.removeItem('uploadedDesignSize');
                sessionStorage.removeItem('uploadedDesignData');
                sessionStorage.removeItem('uploadedDesignType');

                // Mostrar modal o mensaje de éxito
                const modal = document.getElementById('cart-success-modal');
                if (modal) {
                    modal.classList.remove('hidden');
                } else {
                    alert(`✅ ${data.message}`);
                }

                // Actualizar contador del carrito
                const cartCounter = document.getElementById('cart-count');
                if (cartCounter && data.cart_count) {
                    cartCounter.textContent = data.cart_count;
                }
            } else {
                alert('❌ Error: ' + (data.error || 'No se pudo agregar al carrito'));
            }
        })
        .catch(error => {
            console.error('❌ Error:', error);
            alert('❌ Error al agregar al carrito. Por favor intenta de nuevo.');
        })
        .finally(() => {
            // Rehabilitar botón y resetear flag
            addBtn.disabled = false;
            addBtn.innerHTML = originalText;
            window.isAddingToCart = false;
        });
}

// Función auxiliar para obtener el CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ====================================================================
// E. CONTROL DE CANTIDAD (incrementar/decrementar)
// ====================================================================

function setupQuantityControls() {
    const quantityInput = document.getElementById('quantity');
    const decreaseBtn = document.getElementById('qty-decrease');
    const increaseBtn = document.getElementById('qty-increase');

    if (!quantityInput || !decreaseBtn || !increaseBtn) return;

    decreaseBtn.addEventListener('click', () => {
        let currentValue = parseInt(quantityInput.value) || 10;
        if (currentValue > 10) {
            quantityInput.value = currentValue - 1;
            updatePriceAndHighlight();
        }
    });

    increaseBtn.addEventListener('click', () => {
        let currentValue = parseInt(quantityInput.value) || 10;
        if (currentValue < 10000) {
            quantityInput.value = currentValue + 1;
            updatePriceAndHighlight();
        }
    });
}

// ====================================================================
// F. TOGGLE DE TABLA DE TIERS
// ====================================================================

function setupTiersToggle() {
    const toggleBtn = document.getElementById('toggle-tiers-btn');
    const tiersTable = document.getElementById('tiers-table');
    const chevron = document.getElementById('tiers-chevron');

    if (!toggleBtn || !tiersTable) return;

    toggleBtn.addEventListener('click', () => {
        tiersTable.classList.toggle('hidden');
        if (chevron) {
            chevron.style.transform = tiersTable.classList.contains('hidden')
                ? 'rotate(0deg)'
                : 'rotate(180deg)';
        }
    });
}

// ====================================================================
// G. MODAL DE ÉXITO
// ====================================================================

function setupSuccessModal() {
    const modal = document.getElementById('cart-success-modal');
    const goToCartBtn = document.getElementById('modal-go-to-cart');
    const continueShoppingBtn = document.getElementById('modal-continue-shopping');

    if (!modal) return;

    if (goToCartBtn) {
        goToCartBtn.addEventListener('click', () => {
            window.location.href = '/carrito-de-compras/';
        });
    }

    if (continueShoppingBtn) {
        continueShoppingBtn.addEventListener('click', () => {
            modal.classList.add('hidden');
        });
    }

    // Cerrar al hacer click fuera del modal
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });
}

// ====================================================================
// H. INICIALIZACIÓN AL CARGAR LA PÁGINA
// ====================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Inicializando product_logic.js...');

    // 1. Cargar datos críticos primero
    loadProductData();

    // 2. Input de cantidad
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        quantityInput.addEventListener('input', updatePriceAndHighlight);
        quantityInput.addEventListener('change', updatePriceAndHighlight);

        quantityInput.addEventListener('keypress', e => {
            if (e.key === 'Enter') {
                e.preventDefault();
                updatePriceAndHighlight();
            }
        });

        // Precio inicial
        updatePriceAndHighlight();
    }

    // 3. Controles de cantidad (+/-)
    setupQuantityControls();

    // 4. Toggle de tabla de tiers
    setupTiersToggle();

    // 5. Modal de éxito
    setupSuccessModal();

    // 6. Botones de color
    document.querySelectorAll('.color-swatch').forEach(btn => {
        btn.addEventListener('click', () => {
            selectColor(btn.dataset.colorSlug, btn.dataset.colorName);
        });
    });

    // 7. Botones de talla
    document.querySelectorAll('.size-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            selectSize(btn.dataset.sizeSlug, btn.dataset.sizeName);
        });
    });

    // 8. Botón de agregar al carrito
    const addToCartBtn = document.getElementById('add-to-cart');
    if (addToCartBtn) {
        // Solo agregar listener sin clonar (el flag window.isAddingToCart previene ejecuciones múltiples)
        addToCartBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopImmediatePropagation();
            addToCart();
        }, { once: false }); // No usar {once: true} para permitir múltiples compras
    }

    console.log('✅ Lógica de producto inicializada correctamente');
});
