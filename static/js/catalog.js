/**
 * Catalog JavaScript
 * Funcionalidad general para el sistema de catálogo
 */

(function() {
    'use strict';

    /**
     * Initialize catalog functionality
     */
    function init() {
        // Set up search functionality
        setupSearch();
        
        // Set up filter forms
        setupFilters();
        
        // Set up image lazy loading
        setupLazyLoading();
        
        // Set up animations
        setupAnimations();
    }

    /**
     * Setup search functionality
     */
    function setupSearch() {
        const searchForms = document.querySelectorAll('.search-form');
        
        searchForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const input = form.querySelector('input[name="q"]');
                if (input && input.value.trim().length < 3) {
                    e.preventDefault();
                    showNotification('Por favor ingrese al menos 3 caracteres', 'warning');
                }
            });
        });
    }

    /**
     * Setup filter forms
     */
    function setupFilters() {
        const filterForm = document.getElementById('filtersForm');
        if (!filterForm) return;

        // Auto-submit on radio button change
        const radioInputs = filterForm.querySelectorAll('input[type="radio"]');
        radioInputs.forEach(input => {
            input.addEventListener('change', function() {
                filterForm.submit();
            });
        });

        // Clear filters button
        const clearButton = filterForm.querySelector('[href*="?"]');
        if (clearButton) {
            clearButton.addEventListener('click', function(e) {
                e.preventDefault();
                window.location.href = this.href;
            });
        }
    }

    /**
     * Setup lazy loading for images
     */
    function setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                        }
                        observer.unobserve(img);
                    }
                });
            });

            const lazyImages = document.querySelectorAll('img[data-src]');
            lazyImages.forEach(img => imageObserver.observe(img));
        }
    }

    /**
     * Setup scroll animations
     */
    function setupAnimations() {
        if ('IntersectionObserver' in window) {
            const animationObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                    }
                });
            }, {
                threshold: 0.1
            });

            const animatedElements = document.querySelectorAll('.product-card, .category-card, .info-card');
            animatedElements.forEach(el => {
                el.style.opacity = '0';
                el.style.transform = 'translateY(20px)';
                el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                animationObserver.observe(el);
            });

            // Add CSS for animation
            const style = document.createElement('style');
            style.textContent = `
                .animate-in {
                    opacity: 1 !important;
                    transform: translateY(0) !important;
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * Show notification message
     */
    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `catalog-notification catalog-notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${getIconForType(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${getColorForType(type)};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;

        // Add animation
        const styleSheet = document.createElement('style');
        styleSheet.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
            .notification-content {
                display: flex;
                align-items: center;
                gap: 10px;
            }
        `;
        document.head.appendChild(styleSheet);

        // Append to body
        document.body.appendChild(notification);

        // Auto-remove after 4 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 4000);
    }

    /**
     * Get icon for notification type
     */
    function getIconForType(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || icons.info;
    }

    /**
     * Get color for notification type
     */
    function getColorForType(type) {
        const colors = {
            'success': '#28a745',
            'error': '#dc3545',
            'warning': '#ffc107',
            'info': '#007bff'
        };
        return colors[type] || colors.info;
    }

    /**
     * Smooth scroll to element
     */
    function scrollToElement(element, offset = 100) {
        const top = element.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({
            top: top,
            behavior: 'smooth'
        });
    }

    /**
     * Format currency
     */
    function formatCurrency(amount) {
        return new Intl.NumberFormat('es-PE', {
            style: 'currency',
            currency: 'PEN'
        }).format(amount);
    }

    // Expose utility functions globally
    window.CatalogUtils = {
        showNotification,
        scrollToElement,
        formatCurrency
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
