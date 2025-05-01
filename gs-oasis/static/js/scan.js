// JavaScript for the scan page functionality

document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Show the corresponding content
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // URL Scanner functionality
    const urlForm = document.getElementById('url-scan-btn');
    const urlInput = document.getElementById('url-input');
    const urlResult = document.getElementById('url-result');
    
    if (urlForm) {
        urlForm.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Basic validation
            if (!urlInput.value.trim()) {
                showResult(urlResult, 'warning', 'Please enter a URL to scan.');
                return;
            }
            
            // Simulate scanning (in a real app, this would call an API)
            showResult(urlResult, 'loading', 'Scanning URL...');
            
            // Simulate API delay
            setTimeout(() => {
                // Simulate different results based on URL content
                const url = urlInput.value.toLowerCase();
                
                if (url.includes('phishing') || url.includes('scam') || url.includes('free-money')) {
                    showResult(urlResult, 'danger', 
                        `<h4>⚠️ High Risk Detected!</h4>
                        <p>This URL shows strong indicators of a phishing attempt or scam.</p>
                        <p><strong>Recommendation:</strong> Do not visit this website or provide any information.</p>`
                    );
                } else if (url.includes('suspicious') || url.includes('unknown') || url.includes('redirect')) {
                    showResult(urlResult, 'warning', 
                        `<h4>⚠️ Potential Risk Detected</h4>
                        <p>This URL contains suspicious elements that may indicate risk.</p>
                        <p><strong>Recommendation:</strong> Proceed with caution or avoid this website.</p>`
                    );
                } else {
                    showResult(urlResult, 'success', 
                        `<h4>✅ No Known Threats Detected</h4>
                        <p>Our scan did not find any known security issues with this URL.</p>
                        <p><strong>Note:</strong> While no threats were detected, always remain cautious when visiting unfamiliar websites.</p>`
                    );
                }
            }, 1500);
        });
    }
    
    // File Scanner functionality
    const fileScanBtn = document.getElementById('file-scan-btn');
    const fileInput = document.getElementById('file-input');
    const fileResult = document.getElementById('file-result');
    
    if (fileScanBtn) {
        fileScanBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Basic validation
            if (!fileInput.files[0]) {
                showResult(fileResult, 'warning', 'Please select a file to scan.');
                return;
            }
            
            const file = fileInput.files[0];
            
            // Simulate scanning
            showResult(fileResult, 'loading', `Scanning file: ${file.name}...`);
            
            // Simulate API delay
            setTimeout(() => {
                // Simulate different results based on file type and name
                const fileName = file.name.toLowerCase();
                const fileType = file.type;
                
                if (fileName.includes('virus') || fileName.includes('malware') || fileName.endsWith('.exe') || fileName.endsWith('.bat')) {
                    showResult(fileResult, 'danger', 
                        `<h4>⚠️ Potentially Harmful File</h4>
                        <p>This file type or name is commonly associated with malware.</p>
                        <p><strong>File:</strong> ${file.name}</p>
                        <p><strong>Size:</strong> ${formatFileSize(file.size)}</p>
                        <p><strong>Recommendation:</strong> Do not open this file.</p>`
                    );
                } else if (fileType.includes('application') || fileName.endsWith('.zip') || fileName.endsWith('.rar')) {
                    showResult(fileResult, 'warning', 
                        `<h4>⚠️ Caution Advised</h4>
                        <p>This file type can potentially contain executable code.</p>
                        <p><strong>File:</strong> ${file.name}</p>
                        <p><strong>Size:</strong> ${formatFileSize(file.size)}</p>
                        <p><strong>Recommendation:</strong> Only open if you trust the source.</p>`
                    );
                } else {
                    showResult(fileResult, 'success', 
                        `<h4>✅ No Threats Detected</h4>
                        <p>Our scan did not find any known security issues with this file.</p>
                        <p><strong>File:</strong> ${file.name}</p>
                        <p><strong>Size:</strong> ${formatFileSize(file.size)}</p>
                        <p><strong>Note:</strong> Always verify files from trusted sources.</p>`
                    );
                }
            }, 2000);
        });
    }
    
    // Image Scanner functionality
    const imageScanBtn = document.getElementById('image-scan-btn');
    const imageInput = document.getElementById('image-input');
    const imageResult = document.getElementById('image-result');
    
    if (imageScanBtn) {
        imageScanBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Basic validation
            if (!imageInput.files[0]) {
                showResult(imageResult, 'warning', 'Please select an image to scan.');
                return;
            }
            
            const image = imageInput.files[0];
            
            // Check if file is an image
            if (!image.type.startsWith('image/')) {
                showResult(imageResult, 'warning', 'The selected file is not an image. Please select an image file.');
                return;
            }
            
            // Simulate scanning
            showResult(imageResult, 'loading', `Analyzing image: ${image.name}...`);
            
            // Simulate API delay
            setTimeout(() => {
                // Simulate different results based on image name and size
                const imageName = image.name.toLowerCase();
                
                if (imageName.includes('fake') || imageName.includes('deepfake')) {
                    showResult(imageResult, 'warning', 
                        `<h4>⚠️ Possible Manipulated Image</h4>
                        <p>Our analysis indicates this image may have been digitally altered.</p>
                        <p><strong>Image:</strong> ${image.name}</p>
                        <p><strong>Size:</strong> ${formatFileSize(image.size)}</p>
                        <p><strong>Recommendation:</strong> Verify this image with additional sources.</p>`
                    );
                } else if (image.size > 5000000) { // Large images might have hidden data
                    showResult(imageResult, 'warning', 
                        `<h4>⚠️ Large File Size</h4>
                        <p>This image has a large file size which could potentially contain hidden data.</p>
                        <p><strong>Image:</strong> ${image.name}</p>
                        <p><strong>Size:</strong> ${formatFileSize(image.size)}</p>
                        <p><strong>Recommendation:</strong> Consider scanning with specialized tools.</p>`
                    );
                } else {
                    showResult(imageResult, 'success', 
                        `<h4>✅ Image Appears Authentic</h4>
                        <p>Our analysis did not detect any signs of manipulation or hidden data.</p>
                        <p><strong>Image:</strong> ${image.name}</p>
                        <p><strong>Size:</strong> ${formatFileSize(image.size)}</p>
                        <p><strong>Note:</strong> Advanced manipulations may not be detected.</p>`
                    );
                }
            }, 2000);
        });
    }
    
    // Contact form handling (if on about page)
    const contactForm = document.getElementById('contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // In a real application, this would send the form data to a server
            const formData = new FormData(contactForm);
            const formValues = Object.fromEntries(formData.entries());
            
            // Create a success message
            const formContainer = contactForm.parentElement;
            formContainer.innerHTML = `
                <div class="form-success">
                    <h4>✅ Message Sent Successfully!</h4>
                    <p>Thank you for contacting us, ${formValues.name}. We'll respond to your inquiry about "${formValues.subject}" as soon as possible.</p>
                    <p>A confirmation has been sent to ${formValues.email}.</p>
                </div>
            `;
        });
    }
});

// Helper function to show scan results
function showResult(element, type, message) {
    // Remove any existing classes
    element.className = 'scan-result';
    
    // Add the appropriate class based on result type
    if (type === 'loading') {
        element.innerHTML = `
            <div class="loading-spinner"></div>
            <p>${message}</p>
        `;
        element.classList.add('loading');
    } else {
        element.innerHTML = message;
        element.classList.add(type);
    }
    
    // Make sure the result is visible
    element.style.display = 'block';
}

// Helper function to format file size
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' bytes';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
}