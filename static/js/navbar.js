// VistaPrint-Style Navbar JavaScript
// Mobile menu, dropdowns, and interactivity

document.addEventListener('DOMContentLoaded', function() {
    // Mobile Menu Elements
    const mobileToggle = document.getElementById('mobileToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileClose = document.getElementById('mobileClose');
    const mobileExpandButtons = document.querySelectorAll('.mobile-expand');
    
    // Create overlay element
    const overlay = document.createElement('div');
    overlay.className = 'mobile-overlay';
    document.body.appendChild(overlay);
    
    // Toggle Mobile Menu
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            mobileMenu.classList.add('active');
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }
    
    // Close Mobile Menu
    function closeMobileMenu() {
        mobileMenu.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    if (mobileClose) {
        mobileClose.addEventListener('click', closeMobileMenu);
    }
    
    // Close on overlay click
    overlay.addEventListener('click', closeMobileMenu);
    
    // Handle Mobile Submenu Expansion
    mobileExpandButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const targetId = this.getAttribute('data-target');
            const submenu = document.getElementById(targetId);
            
            // Toggle active state
            this.classList.toggle('active');
            submenu.classList.toggle('active');
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.nav-item')) {
            // Close any open desktop dropdowns if needed
        }
    });
    
    // Allow links to work inside dropdowns
    const dropdowns = document.querySelectorAll('.mega-dropdown');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            // Only stop propagation if NOT clicking on a link
            if (!e.target.closest('a')) {
                e.stopPropagation();
            }
        });
    });
    
    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth > 992) {
                closeMobileMenu();
            }
        }, 250);
    });
    
    // Keyboard navigation for accessibility
    document.addEventListener('keydown', function(e) {
        // Close mobile menu on Escape key
        if (e.key === 'Escape' && mobileMenu.classList.contains('active')) {
            closeMobileMenu();
        }
    });
    
    // Smooth scroll to top when clicking logo
    const logoLink = document.querySelector('.logo-link');
    if (logoLink) {
        logoLink.addEventListener('click', function(e) {
            if (window.location.pathname === this.pathname) {
                e.preventDefault();
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            }
        });
    }
    
    // Add active state to current page nav item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Search input enhancements
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        // Clear button functionality
        searchInput.addEventListener('input', function() {
            if (this.value.length > 0) {
                this.classList.add('has-text');
            } else {
                this.classList.remove('has-text');
            }
        });
        
        // Submit on Enter key
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                this.closest('form').submit();
            }
        });
    }
    
    // Account dropdown toggle for mobile
    const accountDropdown = document.querySelector('.account-dropdown');
    if (accountDropdown && window.innerWidth <= 768) {
        const accountLink = accountDropdown.querySelector('.account-link');
        accountLink.addEventListener('click', function(e) {
            e.preventDefault();
            accountDropdown.classList.toggle('active');
        });
    }
    
    // Navbar scroll behavior - add shadow on scroll
    let lastScroll = 0;
    const navbar = document.querySelector('.vistaprint-navbar');
    
    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        lastScroll = currentScroll;
    });
    
    // Mega dropdown position adjustment for edge cases
    const navItems = document.querySelectorAll('.nav-item.has-dropdown');
    navItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            const dropdown = this.querySelector('.mega-dropdown');
            if (dropdown) {
                const rect = dropdown.getBoundingClientRect();
                const viewportWidth = window.innerWidth;
                
                // Adjust if dropdown goes off-screen
                if (rect.right > viewportWidth) {
                    dropdown.style.left = 'auto';
                    dropdown.style.right = '0';
                    dropdown.style.transform = 'none';
                } else if (rect.left < 0) {
                    dropdown.style.left = '0';
                    dropdown.style.transform = 'none';
                }
            }
        });
    });
    
    // Lazy load dropdown content if needed
    // This can be expanded for dynamic content loading
    
    console.log('VistaPrint Navbar initialized');
});

// Utility function to debounce events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        closeMobileMenu: function() {
            const mobileMenu = document.getElementById('mobileMenu');
            const overlay = document.querySelector('.mobile-overlay');
            if (mobileMenu) mobileMenu.classList.remove('active');
            if (overlay) overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    };
}
