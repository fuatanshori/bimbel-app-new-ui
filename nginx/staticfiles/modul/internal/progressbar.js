document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload_form');
    const inputFile = document.getElementById("id_modul");
    const inputVideo = document.getElementById("id_vidio");
    const progressModalElement = document.getElementById('progressModal');
    const progressModal = new bootstrap.Modal(progressModalElement, {
        backdrop: 'static',  // This prevents the modal from closing when clicking outside
        keyboard: false  // This prevents the modal from closing when pressing ESC key
    });
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.getElementById('progressText');
    const cancelButton = document.getElementById('cancelButton');
    const feedbackMessage = document.getElementById('feedbackMessage');
    let xhr;
    let isUploading = false;

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(uploadForm);
        const file = inputFile.files[0];
        const video = inputVideo.files[0];

        // Clear previous messages and reset classes
        feedbackMessage.textContent = '';
        feedbackMessage.className = '';

        // Check file extensions before uploading
        if (!checkFileType(file, ['pdf'], 'PDF') || !checkFileType(video, ['mp4'], 'MP4')) {
            return; // Stop the function here if file types are invalid
        }

        if (file || video) {
            progressModal.show();
            isUploading = true;
            lockModal();
        }

        xhr = new XMLHttpRequest();
        xhr.open('POST', uploadForm.action, true);

        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentProgress = (e.loaded / e.total) * 100;
                progressBar.style.width = `${percentProgress}%`;
                progressBar.setAttribute('aria-valuenow', percentProgress);
                progressText.textContent = `${Math.round(percentProgress)}%`;
            }
        });

        xhr.onload = function() {
            isUploading = false;
            unlockModal();
            progressModal.hide(); // Hide the modal when the request is complete

            if (xhr.status >= 200 && xhr.status < 300) {
                const response = JSON.parse(xhr.responseText);
                
                if (response.message === "data uploaded") {
                    window.location.href = `/menu/modul/daftar-modul/${response.id_levelstudy}/${response.id_mapel}/`;
                } else {
                    handleError(response);
                }
            } else {
                handleError({ message: 'Upload failed.' });
            }
        };

        xhr.onerror = function() {
            isUploading = false;
            unlockModal();
            progressModal.hide();
            handleError({ message: 'Network error: Upload failed.' });
        };

        xhr.send(formData);
    });

    cancelButton.addEventListener('click', function() {
        if (xhr && isUploading) {
            xhr.abort();
            isUploading = false;
            unlockModal();
            progressModal.hide();
            feedbackMessage.textContent = 'Upload canceled.';
            feedbackMessage.className = 'alert alert-warning';
        }
    });

    function handleError(response) {
        let errorMessage = 'Error: ';
        if (response.errors) {
            errorMessage += 'Form errors: ' + JSON.stringify(response.errors);
        } else {
            errorMessage += response.message;
        }
        feedbackMessage.textContent = errorMessage;
        feedbackMessage.className = 'alert alert-danger';
    }

    function checkFileType(file, allowedExtensions, fileType) {
        if (file) {
            const fileExtension = file.name.split('.').pop().toLowerCase();
            if (!allowedExtensions.includes(fileExtension)) {
                feedbackMessage.textContent = `Error: Invalid file type for ${fileType}. Please upload a ${allowedExtensions.join(' or ')} file.`;
                feedbackMessage.className = 'alert alert-danger';
                return false;
            }
        }
        return true;
    }

    function lockModal() {
        progressModalElement.removeEventListener('hide.bs.modal', preventModalClose);
        progressModalElement.addEventListener('hide.bs.modal', preventModalClose);
    }

    function unlockModal() {
        progressModalElement.removeEventListener('hide.bs.modal', preventModalClose);
    }

    function preventModalClose(event) {
        if (isUploading) {
            event.preventDefault();
        }
    }
});