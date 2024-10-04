document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload_form');
    const progressModal = new bootstrap.Modal(document.getElementById('progressModal'), {
        backdrop: 'static',
        keyboard: false
    });
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.getElementById('progressText');
    const cancelButton = document.getElementById('cancelButton');
    const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB in bytes
    let xhr = null;

    // Function to format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Function to validate file size
    function validateFileSize(formData) {
        const modulFile = formData.get('modul');
        const videoFile = formData.get('vidio');
        let totalSize = 0;
        let errorMessage = '';

        if (modulFile && modulFile.size) {
            totalSize += modulFile.size;
            if (modulFile.size > MAX_FILE_SIZE) {
                errorMessage += `Modul file size (${formatFileSize(modulFile.size)}) exceeds 50MB limit.\n`;
            }
        }

        if (videoFile && videoFile.size) {
            totalSize += videoFile.size;
            if (videoFile.size > MAX_FILE_SIZE) {
                errorMessage += `Video file size (${formatFileSize(videoFile.size)}) exceeds 50MB limit.\n`;
            }
        }

        return {
            isValid: errorMessage === '',
            errorMessage: errorMessage.trim()
        };
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Create FormData
        const formData = new FormData(form);

        // Validate file size before proceeding
        const validation = validateFileSize(formData);
        if (!validation.isValid) {
            showError(validation.errorMessage);
            return;
        }
        
        // Show progress modal
        progressModal.show();
        cancelButton.style.display = 'block';
        
        // Reset progress
        progressBar.style.width = '0%';
        progressBar.setAttribute('aria-valuenow', 0);
        progressText.textContent = '0%';
        progressBar.classList.remove('bg-danger', 'bg-success');

        // Create and configure XHR
        xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = percentComplete + '%';
                progressBar.setAttribute('aria-valuenow', percentComplete);
                progressText.textContent = percentComplete + '%';
            }
        });

        xhr.addEventListener('load', function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.message === 'data uploaded') {
                    // Success
                    progressBar.classList.remove('bg-danger');
                    progressBar.classList.add('bg-success');
                    progressText.textContent = 'Upload Complete!';
                    cancelButton.style.display = 'none';
                    
                    // Redirect after successful upload
                    setTimeout(() => {
                        window.location.href = `/menu/daftar-modul/${response.id_levelstudy}/${response.id_mapel}`;
                    }, 1500);
                } else {
                    // Error with validation or other issues
                    showError(response.message);
                }
            } else {
                showError('Upload failed. Please try again.');
            }
        });

        xhr.addEventListener('error', function() {
            showError('Network error occurred. Please try again.');
        });

        // Send the request
        xhr.open('POST', form.action, true);
        xhr.setRequestHeader('X-CSRFToken', formData.get('csrfmiddlewaretoken'));
        xhr.send(formData);
    });

    // Add file input change listeners for instant validation
    const fileInputs = form.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (file.size > MAX_FILE_SIZE) {
                    showError(`File "${file.name}" (${formatFileSize(file.size)}) exceeds 50MB limit`);
                    e.target.value = ''; // Clear the file input
                }
            }
        });
    });

    // Cancel button handler
    cancelButton.addEventListener('click', function() {
        if (xhr) {
            xhr.abort();
            progressBar.classList.add('bg-danger');
            progressText.textContent = 'Upload Cancelled';
            cancelButton.style.display = 'none';
            
            // Automatically hide modal and reset form after cancellation
            setTimeout(() => {
                progressModal.hide();
                resetProgress();
            }, 1500);
        }
    });

    function showError(message) {
        // If modal is shown, hide it
        if (progressModal._isShown) {
            progressModal.hide();
        }

        // Show feedback message
        const feedbackMessage = document.getElementById('feedbackMessage');
        feedbackMessage.innerHTML = `<div class="alert alert-danger">${message}</div>`;
        
        // Scroll to error message
        feedbackMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        resetProgress();
    }

    function resetProgress() {
        progressBar.style.width = '0%';
        progressBar.setAttribute('aria-valuenow', 0);
        progressText.textContent = '0%';
        progressBar.classList.remove('bg-danger', 'bg-success');
        cancelButton.style.display = 'block';
    }
});