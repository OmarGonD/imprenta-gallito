/**
 * product_pricing.js
 * * Lógica compartida para cálculo y resaltado de niveles de precio (tiers).
 * Depende de que las variables globales `window.priceTiers` y `window.basePrice` 
 * sean definidas en la plantilla HTML antes de la carga de este script.
 */

function updatePriceAndHighlight() {
    const quantityInput = document.getElementById('quantity');
    const subtotalDisplay = document.getElementById('subtotal-price');
    const unitPriceDisplay = document.getElementById('unit-price');
    const tierRows = document.querySelectorAll('#tiers-table .tier-row'); 
    
    // Elementos específicos que pueden existir en product_detail.html (ej. el precio total y descuento separados)
    const totalPriceEl = document.getElementById('totalPriceEl') || document.getElementById('total-price'); 
    const discountPercentEl = document.getElementById('discountPercentEl') || document.getElementById('discount-percent');

    // Usar las variables globales definidas en el template
    const priceTiers = window.priceTiers || []; 
    const basePrice = window.basePrice || 0;

    if (!quantityInput || !subtotalDisplay) return;

    const quantity = parseInt(quantityInput.value) || 1;
    let unitPrice = basePrice;
    let discount = 0;
    let activeMinQuantity = null; 

    // 1. Encontrar el Tier Activo y el Precio
    for (const tier of priceTiers) {
        // Usamos min_quantity y unit_price, asumiendo que son las propiedades estándar.
        const min = tier.min_quantity || tier.min; 
        const max = tier.max_quantity || tier.max; 

        if (quantity >= min && quantity <= max) {
            unitPrice = tier.unit_price || tier.price;
            discount = tier.discount_percent || tier.discount || 0;
            activeMinQuantity = min.toString();
            break;
        }
    }
    
    // 2. Aplicar el Highlight
    tierRows.forEach(row => {
        const rowMin = row.dataset.min;
        
        // El resaltado funciona comparando el min_quantity activo con el data-min de la fila
        if (rowMin === activeMinQuantity) {
            row.classList.add('tier-row-active');
        } else {
            row.classList.remove('tier-row-active');
        }
    });

    // 3. Actualizar Precios en la UI
    const subtotal = unitPrice * quantity;

    subtotalDisplay.textContent = `S/ ${subtotal.toFixed(2)}`;
    
    // Actualizar elementos específicos si existen
    if (totalPriceEl) {
        // En algunos casos, subtotalDisplay y totalPriceEl podrían ser el mismo, ajusta según tu HTML
        totalPriceEl.textContent = subtotal.toFixed(2);
    }
    if (discountPercentEl) {
         discountPercentEl.textContent = discount;
    }

    // Actualizar precio por unidad
    if (unitPriceDisplay) {
        unitPriceDisplay.textContent = `S/ ${unitPrice.toFixed(2)}`;
    }
}

// ====================================================================
// INICIALIZACIÓN Y EVENT LISTENERS COMPARTIDOS
// ====================================================================

document.addEventListener('DOMContentLoaded', function () {
    const quantityInput = document.getElementById('quantity');
    
    if (quantityInput) {
        // Event listeners para cálculo y highlight
        quantityInput.addEventListener('input', updatePriceAndHighlight);
        quantityInput.addEventListener('change', updatePriceAndHighlight);
        
        // Manejo de la tecla Enter para evitar la recarga de la página
        quantityInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault(); 
                updatePriceAndHighlight(); 
                
                // Enfoca el botón de agregar al carrito (adaptado para diferentes IDs)
                const addBtn = document.getElementById('add-to-cart-btn') || document.getElementById('add-to-cart');
                if (addBtn) addBtn.focus();
            }
        });

        // Calcular precio inicial
        updatePriceAndHighlight();
    }
});