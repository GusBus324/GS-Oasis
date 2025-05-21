/**
 * GS-Oasis Dashboard JavaScript
 * Handles interactive elements in the dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile sidebar toggle
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.querySelector('.dashboard-sidebar').classList.toggle('active');
        });
    }
    
    // Navigation highlight
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.dashboard-nav a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.parentElement.classList.add('active');
        }
        
        // Add click handler for internal tabs
        link.addEventListener('click', function(e) {
            // Only handle internal section links
            if (link.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                
                // Remove active class from all links
                navLinks.forEach(innerLink => {
                    innerLink.parentElement.classList.remove('active');
                });
                
                // Add active class to clicked link
                this.parentElement.classList.add('active');
                
                // Scroll to section
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    // Smooth scroll to element
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Security tips carousel
    let currentTip = 0;
    const tips = document.querySelectorAll('.tip-item');
    
    if (tips.length > 0) {
        setInterval(() => {
            // Hide current tip
            tips[currentTip].classList.remove('active');
            
            // Move to next tip
            currentTip = (currentTip + 1) % tips.length;
            
            // Show new tip
            tips[currentTip].classList.add('active');
        }, 5000);
        
        // Set first tip as active
        tips[0].classList.add('active');
    }
    
    // Add event listeners to action buttons
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.classList.add('pulse');
        });
        
        btn.addEventListener('mouseleave', function() {
            this.classList.remove('pulse');
        });
    });
});
