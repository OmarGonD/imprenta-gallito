/**
 * product_logic.js
 * Lógica compartida para página de detalle de producto
 * Versión definitiva usando <script type="application/json"> (método oficial de Django)
 */

window.priceTiers = [];
window.basePrice = 0;
window.selectedColorSlug = '';
window.selectedSizeSlug = '';

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

    // 2. Tiers desde <script type="application/json"> (método infalible)
    const scriptId = dataContainer.dataset.tiersId;
    const scriptEl = document.getElementById(scriptId);

    if (scriptEl) {
        try {
            // textContent ya viene como JSON válido gracias a |json_script
            window.priceTiers = JSON.parse(scriptEl.textContent.trim());
            console.log(`Tiers cargados correctamente (${window.priceTiers.length} niveles)`);
        } catch (e) {
            console.error('Error al parsear JSON de tiers:', e);
            console.error('Contenido problemático:', scriptEl.textContent.substring(0, 200));
            window.priceTiers = [];
        }
    } else {
        console.warn('No se encontró <script id="' + scriptId + '">. Usando tiers vacíos.');
        window.priceTiers = [];
    }
}

// ====================================================================
// B. ACTUALIZAR PRECIO Y RESALTAR TIER ACTIVO
// ====================================================================

function updatePriceAndHighlight() {
    const quantityInput = document.getElementById('quantity');
    const unitPriceDisplay = document.getElementById('unit-price');
    const discountPercentEl = document.getElementById('discount-percent') || document.getElementById('discountPercentEl');
    const totalPriceEl = document.getElementById('total-price') || document.getElementById('totalPriceEl');
    const tierRows = document.querySelectorAll('.tier-row');

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
            unitPrice = tier.unit_price ?? tier.price ?? window.basePrice;
            discount = tier.discount_percent ?? tier.discount ?? 0;
            activeMinQuantity = min.toString();
            break;
        }
    }

    // Resaltar fila activa
    tierRows.forEach(row => {
        const rowMin = row.dataset.min;
        if (rowMin === activeMinQuantity) {
            row.classList.add('tier-row-active');
        } else {
            row.classList.remove('tier-row-active');
        }
    });

    // Actualizar precios en pantalla
    const total = (unitPrice * quantity).toFixed(2);

    if (unitPriceDisplay) unitPriceDisplay.textContent = unitPrice.toFixed(2);
    if (discountPercentEl) discountPercentEl.textContent = discount;
    if (totalPriceEl) totalPriceEl.textContent = total;
}

// ====================================================================
// C. SELECCIÓN DE COLOR Y TALLA (ropa, etc.)
// ====================================================================

function selectColor(colorSlug, colorName) {
    window.selectedColorSlug = colorSlug;

    document.querySelectorAll('.color-swatch').forEach(btn => {
        if (btn.dataset.colorSlug === colorSlug) {
            btn.classList.add('ring-2', 'ring-offset-2', 'ring-blue-500');
        } else {
            btn.classList.remove('ring-2', 'ring-offset-2', 'ring-blue-500');
        }
    });

    const display = document.getElementById('selected-color-name');
    if (display) display.textContent = colorName;

    updateThumbnails(colorSlug);
}

function selectSize(sizeSlug, sizeName) {
    window.selectedSizeSlug = sizeSlug;

    document.querySelectorAll('.size-btn').forEach(btn => {
        if (btn.dataset.sizeSlug === sizeSlug) {
            btn.classList.add('bg-gray-900', 'text-white');
            btn.classList.remove('bg-white', 'text-gray-900', 'hover:bg-gray-50');
        } else {
            btn.classList.remove('bg-gray-900', 'text-white');
            btn.classList.add('bg-white', 'text-gray-900', 'hover:bg-gray-50');
        }
    });

    const display = document.getElementById('selected-size-name');
    if (display) display.textContent = sizeName;
}

function updateThumbnails(colorSlug) {
    // Aquí puedes añadir lógica futura para cambiar miniaturas por color
    // Por ahora solo deja el placeholder
}

// ====================================================================
// D. SUBIDA DE ARCHIVOS (drag & drop)
// ====================================================================

function setupFileUpload() {
    const uploadZone = document.getElementById('file-upload-section');
    const fileInput = document.getElementById('file-upload-input');
    if (!uploadZone || !fileInput) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => uploadZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => uploadZone.classList.remove('dragover'), false);
    });

    uploadZone.addEventListener('drop', e => {
        const files = e.dataTransfer.files;
        if (files.length) handleFiles(files);
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) handleFiles(fileInput.files);
    });

    uploadZone.addEventListener('click', () => fileInput.click());

    function handleFiles(files) {
        const preview = document.getElementById('file-preview-container');
        if (!preview) return;

        if (files.length > 0) {
            preview.innerHTML = `<p class="text-sm text-gray-700 font-medium">Archivo seleccionado: ${files[0].name}</p>`;
        } else {
            preview.innerHTML = `<p class="text-sm text-gray-400">Ningún archivo seleccionado</p>`;
        }
    }
}

// ====================================================================
// E. INICIALIZACIÓN AL CARGAR LA PÁGINA
// ====================================================================

document.addEventListener('DOMContentLoaded', () => {
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
                const addBtn = document.getElementById('add-to-cart-btn') || document.getElementById('add-to-cart');
                if (addBtn) addBtn.focus();
            }
        });

        // Precio inicial
        updatePriceAndHighlight();
    }

    // 3. Botones de color
    document.querySelectorAll('.color-swatch').forEach(btn => {
        btn.addEventListener('click', () => {
            selectColor(btn.dataset.colorSlug, btn.dataset.colorName);
        });
    });

    // 4. Botones de talla
    document.querySelectorAll('.size-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            selectSize(btn.dataset.sizeSlug, btn.dataset.sizeName);
        });
    });

    // 5. Drag & drop de archivos
    setupFileUpload();

    console.log('Lógica de producto inicializada correctamente');
});