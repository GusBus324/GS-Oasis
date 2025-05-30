/* JavaScript for drag-and-drop file upload */
document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.querySelector('.drop-zone');
    const fileInput = document.getElementById('image-input');
    const fileNameDisplay = document.getElementById('selected-file-name');
    
    if (dropZone && fileInput) {
        // Handle drag enter
        dropZone.addEventListener('dragenter', function(e) {
            e.preventDefault();
            this.classList.add('active');
        });
        
        // Handle drag over
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('active');
        });
        
        // Handle drag leave
        dropZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('active');
        });
        
        // Handle drop
        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('active');
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateFileName(fileInput.files[0].name);
            }
        });
        
        // Handle click to select
        dropZone.addEventListener('click', function() {
            fileInput.click();
        });
        
        // Handle file selection
        fileInput.addEventListener('change', function() {
            if (this.files.length) {
                updateFileName(this.files[0].name);
            } else {
                updateFileName('No image selected');
            }
        });
        
        // Update file name display
        function updateFileName(name) {
            fileNameDisplay.textContent = name;
            if (name !== 'No image selected') {
                fileNameDisplay.classList.add('file-selected');
                dropZone.classList.add('has-file');
            } else {
                fileNameDisplay.classList.remove('file-selected');
                dropZone.classList.remove('has-file');
            }
        }
    }
});
