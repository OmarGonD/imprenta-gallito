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
window.minQuantity = 1;

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
    window.minQuantity = parseInt(dataContainer.dataset.minQuantity) || 1;

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

    let quantity = parseInt(quantityInput.value, 10) || window.minQuantity;

    // Enforce minimum
    if (quantity < window.minQuantity) {
        quantity = window.minQuantity;
        quantityInput.value = quantity;
    }

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
// C. SELECCIÓN DE OPCIONES Y PRECIOS DINÁMICOS
// ====================================================================

// Almacén de surcharges por opción: { 'color': 5.00, 'size': 0.00, 'print_size': 8.50, ... }
window.optionSurcharges = {};

function calculateTotalSurcharge() {
    let total = 0;
    for (const key in window.optionSurcharges) {
        total += window.optionSurcharges[key];
    }
    return total;
}

// Sobrescribimos updatePriceAndHighlight para incluir surcharges
const originalUpdatePrice = updatePriceAndHighlight;
updatePriceAndHighlight = function () {
    // 1. Obtener precio base del tier (original logic)
    // Copiamos lógica porque necesitamos intervenir "unitPrice" antes del total

    const quantityInput = document.getElementById('quantity');
    const unitPriceDisplay = document.getElementById('unit-price');
    const discountBadge = document.getElementById('discount-badge');
    const totalPriceEl = document.getElementById('total-price');
    const tierRows = document.querySelectorAll('[data-tier-min]');

    if (!quantityInput) return;

    let quantity = parseInt(quantityInput.value, 10) || window.minQuantity;
    if (quantity < window.minQuantity) {
        quantity = window.minQuantity;
        quantityInput.value = quantity;
    }

    let tierPrice = window.basePrice;
    let discount = 0;
    let activeMinQuantity = null;

    // Buscar tier activo
    for (const tier of window.priceTiers) {
        const min = tier.min_quantity ?? tier.min ?? 0;
        const max = tier.max_quantity ?? tier.max ?? Infinity;

        if (quantity >= min && quantity <= max) {
            tierPrice = tier.price_per_unit ?? tier.unit_price ?? tier.price ?? window.basePrice;
            discount = tier.discount_percentage ?? tier.discount_percent ?? tier.discount ?? 0;
            activeMinQuantity = min.toString();
            break;
        }
    }

    // Calcular precio final unitario = Precio Tier + Surcharges
    const totalSurcharge = calculateTotalSurcharge();
    const finalUnitPrice = parseFloat(tierPrice) + totalSurcharge;

    // Resaltar fila activa Y ACTUALIZAR PRECIOS EN LA TABLA
    tierRows.forEach(row => {
        const rowMin = parseInt(row.dataset.tierMin);

        // 1. Highlight active row
        if (rowMin == activeMinQuantity) {
            row.classList.add('tier-row-active');
        } else {
            row.classList.remove('tier-row-active');
        }

        // 2. Update displayed price in table (Add surcharge to tier base price)
        const tierData = window.priceTiers.find(t => (t.min_quantity ?? t.min ?? 0) == rowMin);
        if (tierData) {
            const baseTierPrice = parseFloat(tierData.price_per_unit ?? tierData.unit_price ?? tierData.price ?? window.basePrice);
            const currentTierPrice = baseTierPrice + totalSurcharge;

            const priceCell = row.querySelector('.price-value');
            if (priceCell) {
                priceCell.textContent = `S/ ${currentTierPrice.toFixed(2)}`;
            }
        }
    });

    // Actualizar precios en pantalla
    const total = (finalUnitPrice * quantity).toFixed(2);

    if (unitPriceDisplay) unitPriceDisplay.textContent = `S/ ${finalUnitPrice.toFixed(2)}`;
    if (discountBadge) discountBadge.textContent = `${discount}%`;
    if (totalPriceEl) totalPriceEl.textContent = `S/ ${total}`;
};

function selectColor(colorSlug, colorName, surcharge = 0) {
    window.selectedColorSlug = colorSlug;
    window.optionSurcharges['color'] = parseFloat(surcharge) || 0;

    document.querySelectorAll('.color-swatch').forEach(btn => {
        const btnSlug = btn.dataset.colorSlug || btn.dataset.color;
        if (btnSlug === colorSlug) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    const display = document.getElementById('selected-color-name');
    if (display) display.textContent = colorName;

    // Actualizar input hidden
    const hiddenInput = document.getElementById('selected-color');
    if (hiddenInput) hiddenInput.value = colorSlug;

    updatePriceAndHighlight();
}
window.selectColor = selectColor;

function selectOption(optionKey, valueSlug, valueName, surcharge = 0) {
    if (optionKey === 'size') {
        window.selectedSizeSlug = valueSlug;
    }

    // Guardar surcharge
    window.optionSurcharges[optionKey] = parseFloat(surcharge) || 0;

    // Actualizar UI activa
    // Buscamos botones dentro del container de esta opción
    const container = document.querySelector(`.product-option[data-option-key="${optionKey}"]`);
    if (container) {
        container.querySelectorAll('.option-btn').forEach(btn => {
            if (btn.dataset.valueSlug === valueSlug) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Actualizar etiqueta de nombre
        const display = container.querySelector('.selected-option-name');
        if (display) display.textContent = valueName;

        // Actualizar input hidden
        const hiddenInput = container.querySelector('input.option-input');
        if (hiddenInput) hiddenInput.value = valueSlug;
    } else {
        // Fallback para legacy 'size' hardcoded html si existe
        if (optionKey === 'size') {
            document.querySelectorAll('.size-btn').forEach(btn => {
                // Ignore option-btn class buttons here to avoid double toggling if mix
                if (btn.classList.contains('option-btn')) return;

                if (btn.dataset.sizeSlug === valueSlug) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
            const display = document.getElementById('selected-size-name');
            if (display) display.textContent = valueName;
            if (hidden) hidden.value = valueSlug;
        }
    }

    updatePriceAndHighlight();
}
window.selectOption = selectOption;

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

    // Validar opciones genéricas (Talla, Tamaño, etc.)
    let missingOption = false;
    document.querySelectorAll('.product-option').forEach(optionContainer => {
        const optionKey = optionContainer.dataset.optionKey;
        const input = optionContainer.querySelector('input.option-input');
        if (input && !input.value) {
            // Highlight container or show alert
            const label = optionContainer.querySelector('label').textContent.replace('*', '').trim();
            alert(`❌ Por favor selecciona: ${label}`);
            missingOption = true;
        }
    });

    if (missingOption) return;

    // Legacy Size Validation (Fallout)
    if (window.selectedSizeSlug === '' && document.querySelector('.size-btn') && !document.querySelector('.product-option[data-option-key="size"]')) {
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

    // 4. VALIDADES ESTRICTAS (Nuevo Requerimiento)
    // ============================================

    // 4.1 Validar que se haya seleccionado un diseño (Template) O subido un archivo
    let templateInput = document.getElementById('selected-template');
    const fileInput = document.getElementById('file-upload-input');

    // Check for file from sessionStorage (uploaded via template gallery)
    const galleryData = sessionStorage.getItem('uploadedDesignData');
    const hasGalleryFile = !!(galleryData && sessionStorage.getItem('uploadedDesignName'));

    // Check for file from input
    const hasInputFile = fileInput && fileInput.files && fileInput.files.length > 0;

    // Check for template selection
    const hasTemplate = templateInput && templateInput.value;

    if (!hasTemplate && !hasInputFile && !hasGalleryFile) {
        alert('❌ Debes elegir un diseño:\n\n1. Selecciona una plantilla del catálogo.\nÓ\n2. Sube tu propio diseño listo para imprimir.');

        // Scroll to design section
        const designSection = document.getElementById('design-section') || document.querySelector('.design-choice-card');
        if (designSection) designSection.scrollIntoView({ behavior: 'smooth', block: 'center' });

        window.isAddingToCart = false; // Reset lock
        return;
    }

    // 4.2 Validar Campos de Contacto / Evento (Si existen en la página)
    let missingFields = [];

    // Lista de campos de contacto obligatorios (si existen en el DOM)
    const requiredContactFields = [
        { id: 'contact_name', label: 'Nombre completo' },
        { id: 'contact_phone', label: 'Celular / Teléfono' },
        // { id: 'contact_job_title', label: 'Cargo' }, // Opcional?
        // { id: 'contact_company', label: 'Empresa' }, // Opcional?
    ];

    requiredContactFields.forEach(field => {
        const input = document.getElementById(field.id);
        if (input && !input.value.trim()) {
            missingFields.push(field.label);
            input.classList.add('border-red-500', 'ring-1', 'ring-red-500'); // Highlight error

            // Remove error on input
            input.addEventListener('input', () => {
                input.classList.remove('border-red-500', 'ring-1', 'ring-red-500');
            }, { once: true });
        }
    });

    // Lista de campos adicionales obligatorios (Eventos, Bodas, etc.)
    // Asumimos que todos los inputs visibles con clase 'js-additional-info' son obligatorios
    // salvo los que sean explicitamente opcionales (ej: notas)
    const addInfoInputs = document.querySelectorAll('.js-additional-info');
    addInfoInputs.forEach(input => {
        // Ignorar campos opcionales (textarea de notas por ejemplo, si se desea)
        // Por ahora exigimos todo lo que no sea textarea o tenga placeholder "Opcional"
        const isOptional = input.tagName === 'TEXTAREA' || input.placeholder.toLowerCase().includes('opcional');

        if (!isOptional && !input.value.trim()) {
            // Try to find a label
            let labelText = input.name || 'Campo requerido';
            const label = input.previousElementSibling; // Asumiendo label antes del input
            if (label && label.tagName === 'LABEL') {
                labelText = label.textContent.replace('*', '').trim();
            }

            missingFields.push(labelText);
            input.classList.add('border-red-500', 'ring-1', 'ring-red-500');

            input.addEventListener('input', () => {
                input.classList.remove('border-red-500', 'ring-1', 'ring-red-500');
            }, { once: true });
        }
    });

    if (missingFields.length > 0) {
        alert(`❌ Por favor completa los siguientes datos obligatorios:\n\n- ${missingFields.join('\n- ')}`);

        // Scroll to first error
        const firstError = document.querySelector('.border-red-500');
        if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });

        window.isAddingToCart = false;
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
    templateInput = document.getElementById('selected-template');
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
        // Also send as 'color' for legacy views
        formData.append('color', window.selectedColorSlug);
    }
    if (window.selectedSizeSlug) {
        formData.append('size_slug', window.selectedSizeSlug);
    }

    // 🆕 Collect Contact Info (Tarjetas de Presentación)
    const contactFields = [
        'contact_name', 'contact_job_title', 'contact_company',
        'contact_phone', 'contact_email', 'contact_social', 'contact_address'
    ];

    contactFields.forEach(field => {
        const input = document.getElementById(field);
        if (input && input.value) {
            formData.append(field, input.value.trim());
        }
    });

    // 🆕 Collect Additional Info (Bodas, Calendarios, Banners)
    // Looking for inputs with class 'js-additional-info'
    const additionalInfoInputs = document.querySelectorAll('.js-additional-info');
    if (additionalInfoInputs.length > 0) {
        const info = {};
        additionalInfoInputs.forEach(input => {
            if (input.value && input.name) {
                info[input.name] = input.value.trim();
            }
        });

        if (Object.keys(info).length > 0) {
            formData.append('additional_info', JSON.stringify(info));
        }
    } else {
        // Fallback: Check if there is a direct additional_info input (hidden or otherwise)
        const directInfo = document.getElementById('additional_info');
        if (directInfo && directInfo.value) {
            formData.append('additional_info', directInfo.value);
        }
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
        let currentValue = parseInt(quantityInput.value) || window.minQuantity;
        if (currentValue > window.minQuantity) {
            quantityInput.value = currentValue - 1;
            updatePriceAndHighlight();
        }
    });

    increaseBtn.addEventListener('click', () => {
        let currentValue = parseInt(quantityInput.value) || window.minQuantity;
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

function resetProductForm() {
    console.log('🔄 Reseteando formulario del producto...');

    // 1. Reset quantity to default
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        quantityInput.value = quantityInput.min || 10;
        updatePriceAndHighlight();
    }

    // 2. Clear template selection
    const templateInput = document.getElementById('selected-template');
    if (templateInput) templateInput.value = '';

    const designTypeInput = document.getElementById('design-type');
    if (designTypeInput) designTypeInput.value = 'template';

    // Hide template preview if visible
    const templatePreview = document.getElementById('selected-template-preview');
    if (templatePreview) templatePreview.classList.add('hidden');

    // Remove selected class from template cards
    document.querySelectorAll('.template-card.selected').forEach(card => {
        card.classList.remove('selected');
    });

    // Reset global template variables if they exist
    if (typeof window.selectedTemplateSlug !== 'undefined') window.selectedTemplateSlug = '';
    if (typeof window.selectedTemplateName !== 'undefined') window.selectedTemplateName = '';
    if (typeof window.selectedTemplateImg !== 'undefined') window.selectedTemplateImg = '';

    // 3. Clear file input
    const fileInput = document.getElementById('file-upload-input');
    if (fileInput) {
        fileInput.value = '';
    }

    // Reset file preview UI
    const filePreviewContainer = document.getElementById('file-preview-container');
    if (filePreviewContainer) filePreviewContainer.classList.add('hidden');

    const uploadButtonContainer = document.getElementById('upload-button-container');
    if (uploadButtonContainer) uploadButtonContainer.classList.remove('hidden');

    // 4. Clear sessionStorage design data
    sessionStorage.removeItem('uploadedDesignName');
    sessionStorage.removeItem('uploadedDesignSize');
    sessionStorage.removeItem('uploadedDesignData');
    sessionStorage.removeItem('uploadedDesignType');
    window.designFromGallery = false;

    // Hide uploaded design preview (from gallery)
    const uploadedDesignPreview = document.getElementById('uploaded-design-preview');
    if (uploadedDesignPreview) uploadedDesignPreview.classList.add('hidden');

    // 5. Clear contact fields (Tarjetas de Presentación)
    const contactFields = [
        'contact_name', 'contact_job_title', 'contact_company',
        'contact_phone', 'contact_email', 'contact_social', 'contact_address'
    ];
    contactFields.forEach(fieldId => {
        const input = document.getElementById(fieldId);
        if (input) input.value = '';
    });

    // 6. Clear additional info fields (Bodas, Eventos, Banners)
    document.querySelectorAll('.js-additional-info').forEach(input => {
        input.value = '';
    });

    // 7. Reset option cards to first/default selection (bodas options)
    document.querySelectorAll('[data-option]').forEach(card => {
        const cards = document.querySelectorAll(`[data-option="${card.dataset.option}"]`);
        cards.forEach((c, index) => {
            if (index === 0) {
                c.classList.add('selected');
                const radio = c.querySelector('input[type="radio"]');
                if (radio) radio.checked = true;
            } else {
                c.classList.remove('selected');
            }
        });
    });

    // Reset color swatches to first
    const colorSwatches = document.querySelectorAll('.color-swatch');
    if (colorSwatches.length > 0) {
        colorSwatches.forEach((s, i) => {
            if (i === 0) s.classList.add('selected');
            else s.classList.remove('selected');
        });
        const hiddenColor = document.getElementById('selected-color');
        if (hiddenColor && colorSwatches[0]) {
            hiddenColor.value = colorSwatches[0].dataset.color || '';
        }
    }

    // 8. Reset Add to Cart button to disabled state
    const addToCartBtn = document.getElementById('add-to-cart');
    const fileRequiredMessage = document.getElementById('file-required-message');

    if (addToCartBtn) {
        addToCartBtn.disabled = true;
        addToCartBtn.classList.remove('bg-blue-600', 'text-white', 'hover:bg-blue-700', 'cursor-pointer');
        addToCartBtn.classList.add('bg-gray-300', 'text-gray-500', 'cursor-not-allowed');
    }
    if (fileRequiredMessage) {
        fileRequiredMessage.classList.remove('hidden');
    }

    // 9. Show design section again if hidden
    const designSection = document.getElementById('design-section');
    if (designSection) designSection.classList.remove('hidden');

    // Show design choice cards if hidden
    const designChoiceSection = document.querySelector('.design-choice-card')?.closest('.mb-6');
    if (designChoiceSection) designChoiceSection.classList.remove('hidden');

    // Show file upload section if hidden
    const fileUploadSection = document.getElementById('file-upload-section');
    if (fileUploadSection) fileUploadSection.classList.remove('hidden');

    console.log('✅ Formulario reseteado correctamente');
}

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
            // Reset the form to allow fresh product addition
            resetProductForm();
        });
    }

    // Cerrar al hacer click fuera del modal
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
            // Also reset form when closing by clicking outside
            resetProductForm();
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
            const slug = btn.dataset.colorSlug || btn.dataset.color;
            const name = btn.dataset.colorName || btn.title || slug;
            // Surcharge logic? You might need to add data-price-add to your color loop in html
            // For now assume 0 or read if available.
            // Note: My python script updated color DB, need to update HTML to output this data attr.
            const surcharge = btn.dataset.priceAdd || 0;
            window.selectColor(slug, name, surcharge);
        });
    });

    // 🆕 6.1 AUTO-DETECT SELECTED COLOR
    const defaultColorBtn = document.querySelector('.color-swatch.selected') || document.querySelector('.color-swatch.active');
    if (defaultColorBtn) {
        const slug = defaultColorBtn.dataset.colorSlug || defaultColorBtn.dataset.color;
        if (slug) {
            console.log('✅ Auto-detecting default color:', slug);
            const name = defaultColorBtn.dataset.colorName || defaultColorBtn.title || slug;
            const surcharge = defaultColorBtn.dataset.priceAdd || 0;
            // Call selectColor to init defaults and pricing
            window.selectColor(slug, name, surcharge);
        }
    }

    // 7. Botones de opción comúnes (Talla, Print Size, etc)
    document.querySelectorAll('.option-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const key = btn.dataset.optionKey; // 'size', 'print_size'
            const slug = btn.dataset.valueSlug;
            const name = btn.dataset.valueName;
            const surcharge = btn.dataset.priceAdd || 0;
            window.selectOption(key, slug, name, surcharge);
        });
    });

    // Legacy Size Buttons (if any exist not using option-btn class)
    document.querySelectorAll('.size-btn:not(.option-btn)').forEach(btn => {
        btn.addEventListener('click', () => {
            selectOption('size', btn.dataset.sizeSlug, btn.dataset.sizeName, 0);
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
