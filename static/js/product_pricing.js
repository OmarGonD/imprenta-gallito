// 1. Al cargar la página o cambiar cantidad
document.getElementById('quantity').addEventListener('input', function(e) {
    const quantity = parseInt(e.target.value);
    const productSlug = '{{ product.slug }}'; // Desde Django template
    
    // Llamar a la API o función local
    updatePricing(productSlug, quantity);
});

// 2. Función para actualizar precios
async function updatePricing(productSlug, quantity) {
    // Opción A: Llamada AJAX
    const response = await fetch(`/api/product-pricing/${productSlug}/${quantity}/`);
    const data = await response.json();
    
    // O Opción B: Cálculo local si pasaste todos los tiers en el contexto
    // const data = calculatePricing(allTiers, quantity);
    
    // Actualizar DOM
    document.getElementById('unit-price').textContent = data.unit_price.toFixed(2);
    document.getElementById('discount-percent').textContent = data.discount_percent;
    document.getElementById('total-price').textContent = data.total_price.toFixed(2);
    
    // Actualizar tabla de tiers (resaltar tier actual)
    updateTiersTable(data.all_tiers, data.current_tier);
    
    // Mostrar/ocultar sugerencia
    updateSuggestion(data.next_tier);
}

// 3. Actualizar tabla de tiers
function updateTiersTable(allTiers, currentTier) {
    const tbody = document.getElementById('tiers-table');
    tbody.innerHTML = '';
    
    allTiers.forEach(tier => {
        const row = document.createElement('tr');
        const isActive = tier.min_quan === currentTier.min_quan;
        
        // Aplicar estilos si es el tier actual
        if (isActive) {
            row.className = 'bg-blue-100 border-l-4 border-blue-600';
        }
        
        const rangeText = tier.max_quan === 999999 
            ? `${tier.min_quan}+` 
            : `${tier.min_quan}-${tier.max_quan}`;
        
        const basePrice = allTiers[0].unit_price;
        const savings = (basePrice - tier.unit_price).toFixed(2);
        
        row.innerHTML = `
            <td class="px-4 py-2">${rangeText}</td>
            <td class="px-4 py-2 font-semibold">S/ ${tier.unit_price.toFixed(2)}</td>
            <td class="px-4 py-2 text-green-600">${tier.discount_percent}%</td>
            <td class="px-4 py-2">S/ ${savings}</td>
        `;
        
        tbody.appendChild(row);
    });
}

// 4. Mostrar sugerencia inteligente
function updateSuggestion(nextTier) {
    const suggestionBox = document.getElementById('suggestion-box');
    const suggestionText = document.getElementById('suggestion-text');
    
    if (nextTier && nextTier.units_needed > 0) {
        suggestionText.textContent = 
            `Compra ${nextTier.units_needed} unidades más (${nextTier.min_quan} total) ` +
            `y ahorra S/ ${nextTier.savings.toFixed(2)} adicionales`;
        suggestionBox.classList.remove('hidden');
    } else {
        suggestionBox.classList.add('hidden');
    }
}

// Ejecutar al cargar
document.addEventListener('DOMContentLoaded', function() {
    const initialQuantity = parseInt(document.getElementById('quantity').value);
    const productSlug = '{{ product.slug }}';
    updatePricing(productSlug, initialQuantity);
});
