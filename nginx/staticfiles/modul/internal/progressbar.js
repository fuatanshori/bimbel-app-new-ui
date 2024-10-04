document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload_form');
    const progressModal = new bootstrap.Modal(document.getElementById('progressModal'));
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.getElementById('progressText');
    const cancelButton = document.getElementById('cancelButton');
    const closeButton = document.getElementById('closeButton');
    let xhr = null;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show progress modal
        progressModal.show();
        closeButton.style.display = 'none';
        cancelButton.style.display = 'block';
        
        // Reset progress
        progressBar.style.width = '0%';
        progressBar.setAttribute('aria-valuenow', 0);
        progressText.textContent = '0%';

        // Create FormData
        const formData = new FormData(form);
        
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
                    closeButton.style.display = 'block';
                    
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

    // Cancel button handler
    cancelButton.addEventListener('click', function() {
        if (xhr) {
            xhr.abort();
            progressBar.classList.add('bg-danger');
            progressText.textContent = 'Upload Cancelled';
            cancelButton.style.display = 'none';
            closeButton.style.display = 'block';
        }
    });

    // Close button handler
    closeButton.addEventListener('click', function() {
        progressModal.hide();
        // Reset progress bar
        progressBar.style.width = '0%';
        progressBar.setAttribute('aria-valuenow', 0);
        progressText.textContent = '0%';
        progressBar.classList.remove('bg-danger', 'bg-success');
    });

    function showError(message) {
        progressBar.classList.add('bg-danger');
        progressText.textContent = 'Error: ' + message;
        cancelButton.style.display = 'none';
        closeButton.style.display = 'block';
        
        // Show feedback message
        const feedbackMessage = document.getElementById('feedbackMessage');
        feedbackMessage.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    }
});