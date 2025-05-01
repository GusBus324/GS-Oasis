// Main JavaScript file for GS-Oasis

// Function to handle mobile navigation toggle
function handleMobileNav() {
    const nav = document.querySelector('nav ul');
    const hamburger = document.createElement('div');
    hamburger.className = 'hamburger';
    hamburger.innerHTML = '☰';
    
    // Only add the hamburger menu on smaller screens
    if (window.innerWidth <= 768) {
        document.querySelector('header').appendChild(hamburger);
        nav.classList.add('mobile-hidden');
        
        hamburger.addEventListener('click', function() {
            nav.classList.toggle('mobile-hidden');
        });
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    handleMobileNav();
    handleScroll();
    
    // Add resize event listener for responsive behavior
    window.addEventListener('resize', function() {
        handleMobileNav();
    });
});