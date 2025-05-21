// Main JavaScript file for GS-Oasis

// Function to handle mobile navigation toggle
function handleMobileNav() {
    const nav = document.querySelector('nav ul');
    let hamburger = document.querySelector('.hamburger');
    
    if (!hamburger) {
        hamburger = document.createElement('div');
        hamburger.className = 'hamburger';
        hamburger.innerHTML = '☰';
        
        // Only add the hamburger menu on smaller screens
        if (window.innerWidth <= 768) {
            document.querySelector('header .container').appendChild(hamburger);
            nav.classList.add('mobile-hidden');
            
            hamburger.addEventListener('click', function() {
                nav.classList.toggle('mobile-hidden');
                hamburger.innerHTML = nav.classList.contains('mobile-hidden') ? '☰' : '✕';
                hamburger.classList.toggle('active');
            });
        }
    }
}

// Check if user has scrolled down
function handleScroll() {
    const header = document.querySelector('header');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

// Handle flash messages
function handleFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.classList.add('fade-out');
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });
}

// Add active class to current navigation item
function highlightCurrentNavItem() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('nav ul li a');
    
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.parentElement.classList.add('active');
        }
    });
}

// Initialize smooth scroll to anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return; // Skip if it's just "#"
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    handleMobileNav();
    handleScroll();
    handleFlashMessages();
    highlightCurrentNavItem();
    initSmoothScroll();
    
    // Add resize event listener for responsive behavior
    window.addEventListener('resize', function() {
        handleMobileNav();
    });
});