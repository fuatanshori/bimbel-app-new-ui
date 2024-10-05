document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload_form');
    const inputFileModul = document.getElementById("id_modul");
    const inputFileVidio = document.getElementById("id_vidio");
    const progressModalElement = document.getElementById('progressModal');
    const progressModal = new bootstrap.Modal(progressModalElement, {
        backdrop: 'static',
        keyboard: false
    });
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.getElementById('progressText');
    const cancelButton = document.getElementById('cancelButton');
    const feedbackMessage = document.getElementById('feedbackMessage');
    let xhr;

    function validateFiles() {
        const fileModul = inputFileModul.files[0];
        const fileVidio = inputFileVidio.files[0];

        if (fileModul && fileModul.size > 100 * 1024 * 1024) {
            feedbackMessage.textContent = 'Error: File modul tidak boleh lebih dari 100MB.';
            feedbackMessage.classList.add('alert', 'alert-danger');
            return false;
        }

        if (fileModul && !fileModul.name.endsWith('.pdf')) {
            feedbackMessage.textContent = 'Error: File modul harus berformat PDF.';
            feedbackMessage.classList.add('alert', 'alert-danger');
            return false;
        }

        if (fileVidio && fileVidio.size > 300 * 1024 * 1024) {
            feedbackMessage.textContent = 'Error: Video tidak boleh lebih dari 300MB.';
            feedbackMessage.classList.add('alert', 'alert-danger');
            return false;
        }

        if (fileVidio && !fileVidio.name.endsWith('.mp4')) {
            feedbackMessage.textContent = 'Error: File video harus berformat MP4.';
            feedbackMessage.classList.add('alert', 'alert-danger');
            return false;
        }

        return true;
    }

    function uploadFiles() {
        const formData = new FormData(uploadForm);
        xhr = new XMLHttpRequest();
        xhr.open('POST', uploadForm.action, true);

        progressModal.show();
        feedbackMessage.textContent = '';
        feedbackMessage.classList.remove('alert-danger', 'alert-warning', 'alert-success');

        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentProgress = (e.loaded / e.total) * 100;
                progressBar.style.width = `${percentProgress}%`;
                progressBar.setAttribute('aria-valuenow', percentProgress);
                progressText.textContent = `${Math.round(percentProgress)}%`;
            }
        });

        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                const response = JSON.parse(xhr.responseText);
                if (response.message === "data uploaded") {
                    window.location.href = `/menu/modul/daftar-modul/${response.id_levelstudy}/${response.id_mapel}/`;
                } else if (response.data === "cant upload") {
                    progressModal.hide();
                    feedbackMessage.textContent = 'Error: ' + (response.errors ? JSON.stringify(response.errors) : response.message);
                    feedbackMessage.classList.add('alert', 'alert-danger');
                } else {
                    progressModal.hide();
                    feedbackMessage.textContent = 'Error: ' + response.message;
                    feedbackMessage.classList.add('alert', 'alert-danger');
                }
            } else {
                progressModal.hide();
                feedbackMessage.textContent = 'Error: Upload failed.';
                feedbackMessage.classList.add('text-danger');
            }
        };

        xhr.onerror = function() {
            progressModal.hide();
            feedbackMessage.textContent = 'Network error: Upload failed.';
            feedbackMessage.classList.add('text-danger');
        };

        xhr.send(formData);
    }

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (validateFiles()) {
            uploadFiles();
        }
    });

    cancelButton.addEventListener('click', function() {
        if (xhr) {
            xhr.abort();
        }
        progressModal.hide();
        feedbackMessage.textContent = 'Upload canceled.';
        feedbackMessage.classList.add('alert', 'alert-warning');
    });

    // Prevent modal from closing when clicking outside
    progressModalElement.addEventListener('click', function(event) {
        if (event.target === progressModalElement) {
            event.stopPropagation();
        }
    });
});