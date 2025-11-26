/**
 * Product Configurator JavaScript
 * Maneja la configuración de productos personalizables en tiempo real
 */

(function() {
    'use strict';

    // Configuration and State
    let productData = {};
    let currentConfig = {
        quantity: 1,
        selectedOptions: []
    };
    let debounceTimer = null;

    /**
     * Initialize the configurator
     */
    function init() {
        // Load product data from the script tag
        loadProductData();
        
        // Set up event listeners
        setupEventListeners();
        
        // Calculate initial price
        calculatePrice();
    }

    /**
     * Load product data from the embedded JSON script
     */
    function loadProductData() {
        const dataElement = document.getElementById('productData');
        if (dataElement) {
            try {
                productData = JSON.parse(dataElement.textContent);
                currentConfig.quantity = productData.min_quantity || 1;
                
                // Initialize selected options with defaults
                if (productData.variants) {
                    productData.variants.forEach(variant => {
                        const defaultOption = variant.options.find(opt => opt.is_default);
                        if (defaultOption) {
                            currentConfig.selectedOptions.push({
                                variant_type_id: variant.id,
                                option_id: defaultOption.id
                            });
                        }
                    });
                }
            } catch (e) {
                console.error('Error parsing product data:', e);
            }
        }
    }

    /**
     * Set up all event listeners
     */
    function setupEventListeners() {
        // Quantity buttons
        const decreaseBtn = document.getElementById('qtyDecrease');
        const increaseBtn = document.getElementById('qtyIncrease');
        const quantityInput = document.getElementById('quantityInput');

        if (decreaseBtn) {
            decreaseBtn.addEventListener('click', () => adjustQuantity(-1));
        }

        if (increaseBtn) {
            increaseBtn.addEventListener('click', () => adjustQuantity(1));
        }

        if (quantityInput) {
            quantityInput.addEventListener('input', handleQuantityInput);
            quantityInput.addEventListener('blur', validateQuantity);
        }

        // Variant option selections
        const variantInputs = document.querySelectorAll('.variant-option input[type="radio"]');
        variantInputs.forEach(input => {
            input.addEventListener('change', handleVariantChange);
        });

        // Add to cart button
        const addToCartBtn = document.getElementById('addToCartBtn');
        if (addToCartBtn) {
            addToCartBtn.addEventListener('click', handleAddToCart);
        }

        // Image thumbnails
        const thumbnails = document.querySelectorAll('.thumbnail');
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', handleThumbnailClick);
        });
    }

    /**
     * Adjust quantity by a delta value
     */
    function adjustQuantity(delta) {
        const input = document.getElementById('quantityInput');
        if (!input) return;

        const currentQty = parseInt(input.value) || productData.min_quantity;
        const newQty = Math.max(productData.min_quantity, currentQty + delta);
        
        input.value = newQty;
        currentConfig.quantity = newQty;
        
        debouncedCalculatePrice();
    }

    /**
     * Handle manual quantity input
     */
    function handleQuantityInput(event) {
        const value = parseInt(event.target.value);
        if (!isNaN(value)) {
            currentConfig.quantity = value;
            debouncedCalculatePrice();
        }
    }

    /**
     * Validate quantity on blur
     */
    function validateQuantity(event) {
        const input = event.target;
        let value = parseInt(input.value);
        
        if (isNaN(value) || value < productData.min_quantity) {
            value = productData.min_quantity;
        }
        
        input.value = value;
        currentConfig.quantity = value;
        calculatePrice();
    }

    /**
     * Handle variant option change
     */
    function handleVariantChange(event) {
        const input = event.target;
        const variantTypeId = parseInt(input.dataset.variantType);
        const optionId = parseInt(input.dataset.optionId);

        // Update selected options
        const existingIndex = currentConfig.selectedOptions.findIndex(
            opt => opt.variant_type_id === variantTypeId
        );

        if (existingIndex >= 0) {
            currentConfig.selectedOptions[existingIndex].option_id = optionId;
        } else {
            currentConfig.selectedOptions.push({
                variant_type_id: variantTypeId,
                option_id: optionId
            });
        }

        // Update visual state
        const parentOption = input.closest('.variant-option');
        const allOptions = input.closest('.variant-options').querySelectorAll('.variant-option');
        allOptions.forEach(opt => opt.classList.remove('selected'));
        if (parentOption) {
            parentOption.classList.add('selected');
        }

        calculatePrice();
    }

    /**
     * Debounced price calculation
     */
    function debouncedCalculatePrice() {
        if (debounceTimer) {
            clearTimeout(debounceTimer);
        }
        debounceTimer = setTimeout(calculatePrice, 300);
    }

    /**
     * Calculate price via AJAX
     */
    async function calculatePrice() {
        const configurator = document.getElementById('productConfigurator');
        if (!configurator) return;

        // Show loading state
        configurator.classList.add('loading');

        try {
            const response = await fetch(productData.calculate_price_url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    product_slug: productData.product_slug,
                    quantity: currentConfig.quantity,
                    selected_options: currentConfig.selectedOptions
                })
            });

            const data = await response.json();

            if (data.success && data.price_info) {
                updatePriceDisplay(data.price_info);
                highlightActiveTier(currentConfig.quantity);
            } else {
                showError(data.error || 'Error al calcular el precio');
            }
        } catch (error) {
            console.error('Error calculating price:', error);
            showError('Error de conexión al calcular el precio');
        } finally {
            configurator.classList.remove('loading');
        }
    }

    /**
     * Update price display with calculated values
     */
    function updatePriceDisplay(priceInfo) {
        // Update all price elements
        updateElement('basePriceDisplay', formatPrice(priceInfo.base_price));
        updateElement('additionalCostDisplay', formatPrice(priceInfo.additional_cost));
        updateElement('unitPriceDisplay', formatPrice(priceInfo.unit_price));
        updateElement('quantityDisplay', currentConfig.quantity);
        updateElement('subtotalDisplay', formatPrice(priceInfo.subtotal));
        updateElement('totalPriceDisplay', formatPrice(priceInfo.total_price));

        // Show/hide savings row
        const savingsRow = document.getElementById('savingsRow');
        if (savingsRow && priceInfo.savings > 0) {
            savingsRow.style.display = 'flex';
            updateElement('savingsDisplay', formatPrice(priceInfo.savings));
        } else if (savingsRow) {
            savingsRow.style.display = 'none';
        }
    }

    /**
     * Highlight the active price tier based on quantity
     */
    function highlightActiveTier(quantity) {
        const tierItems = document.querySelectorAll('.tier-item');
        tierItems.forEach(item => {
            const min = parseInt(item.dataset.min);
            const max = item.dataset.max ? parseInt(item.dataset.max) : Infinity;
            
            if (quantity >= min && quantity <= max) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }

    /**
     * Handle add to cart button click
     */
    async function handleAddToCart() {
        const btn = document.getElementById('addToCartBtn');
        if (!btn) return;

        // Validate configuration first
        const isValid = await validateConfiguration();
        if (!isValid) return;

        // Disable button and show loading
        btn.disabled = true;
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Agregando...';

        try {
            // Prepare cart item data
            const cartData = {
                product_slug: productData.product_slug,
                quantity: currentConfig.quantity,
                selected_options: currentConfig.selectedOptions
            };

            // Here you would make the actual add to cart request
            // For now, we'll simulate success
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Show success message
            showSuccess('¡Producto agregado al carrito!');
            
            // Optionally redirect to cart or update cart counter
            // window.location.href = '/carrito_de_compras/';
        } catch (error) {
            console.error('Error adding to cart:', error);
            showError('Error al agregar al carrito. Por favor intenta nuevamente.');
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }

    /**
     * Validate product configuration
     */
    async function validateConfiguration() {
        try {
            const response = await fetch(productData.validate_config_url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    product_slug: productData.product_slug,
                    selected_options: currentConfig.selectedOptions
                })
            });

            const data = await response.json();

            if (data.success && data.validation) {
                if (data.validation.is_valid) {
                    hideValidationMessages();
                    return true;
                } else {
                    showValidationErrors(data.validation.errors);
                    return false;
                }
            } else {
                showError(data.error || 'Error al validar la configuración');
                return false;
            }
        } catch (error) {
            console.error('Error validating configuration:', error);
            showError('Error de conexión al validar la configuración');
            return false;
        }
    }

    /**
     * Show validation errors
     */
    function showValidationErrors(errors) {
        const container = document.getElementById('validationMessages');
        if (!container) return;

        container.className = 'validation-messages error';
        container.style.display = 'block';
        
        let html = '<ul>';
        errors.forEach(error => {
            html += `<li>${error}</li>`;
        });
        html += '</ul>';
        
        container.innerHTML = html;

        // Scroll to errors
        container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Hide validation messages
     */
    function hideValidationMessages() {
        const container = document.getElementById('validationMessages');
        if (container) {
            container.style.display = 'none';
        }
    }

    /**
     * Show success message
     */
    function showSuccess(message) {
        const container = document.getElementById('validationMessages');
        if (!container) return;

        container.className = 'validation-messages success';
        container.style.display = 'block';
        container.innerHTML = `<p><i class="fas fa-check-circle"></i> ${message}</p>`;

        // Hide after 3 seconds
        setTimeout(() => {
            container.style.display = 'none';
        }, 3000);
    }

    /**
     * Show error message
     */
    function showError(message) {
        const container = document.getElementById('validationMessages');
        if (!container) {
            alert(message);
            return;
        }

        container.className = 'validation-messages error';
        container.style.display = 'block';
        container.innerHTML = `<p><i class="fas fa-exclamation-circle"></i> ${message}</p>`;
    }

    /**
     * Handle thumbnail click to change main image
     */
    function handleThumbnailClick(event) {
        const thumbnail = event.currentTarget;
        const img = thumbnail.querySelector('img');
        if (!img) return;

        // Update main image
        const mainImage = document.getElementById('mainProductImage');
        if (mainImage) {
            mainImage.src = img.src;
        }

        // Update active state
        const thumbnails = document.querySelectorAll('.thumbnail');
        thumbnails.forEach(t => t.classList.remove('active'));
        thumbnail.classList.add('active');
    }

    /**
     * Helper: Update element text content
     */
    function updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * Helper: Format price
     */
    function formatPrice(price) {
        return new Intl.NumberFormat('es-PE', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(price);
    }

    /**
     * Helper: Get CSRF token from cookies
     */
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

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
