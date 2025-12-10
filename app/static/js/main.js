// Adding Image preview functionality to view image before submitting and ensure correct file was uploaded

document.addEventListener('DOMContentLoaded', function() {
    
    // Image preview functionality
    const fileInput = document.getElementById('label_image');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('preview');
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            if (file) {
                // Check if image
                if (!file.type.startsWith('image/')) {
                    alert('Please select an image file');
                    fileInput.value = '';
                    imagePreview.style.display = 'none';
                    return;
                }
                
                // Check file size (max set is 16MB)
                const maxSize = 16 * 1024 * 1024; // 16MB
                if (file.size > maxSize) {
                    alert('File is too large. Maximum size is 16MB.');
                    fileInput.value = '';
                    imagePreview.style.display = 'none';
                    return;
                }
                
                // Show preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                imagePreview.style.display = 'none';
            }
        });
    }
    
    // Form submission loading state
    const form = document.getElementById('verificationForm');
    if (form) {
        form.addEventListener('submit', function() {
            document.body.classList.add('loading');
            
            // Disable the submit button to prevent double submission
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Processing...';
            }
        });
    }
    
    // Form validation 
    const alcoholContent = document.getElementById('alcohol_content');
    if (alcoholContent) {
        alcoholContent.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value < 0 || value > 100) {
                this.setCustomValidity('Alcohol content must be between 0 and 100');
            } else {
                this.setCustomValidity('');
            }
        });
    }
});