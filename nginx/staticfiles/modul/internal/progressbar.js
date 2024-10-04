document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload_form');
    const inputFile = document.getElementById("id_modul");
    const progressModal = new bootstrap.Modal(document.getElementById('progressModal')); 
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.getElementById('progressText');
    const cancelButton = document.getElementById('cancelButton');
    const feedbackMessage = document.getElementById('feedbackMessage');
    let xhr;

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(uploadForm);
        const file = inputFile.files[0];

        // Validasi file: pastikan hanya PDF yang diizinkan
        if (file != null) {
            const fileType = file.type;
            if (fileType !== 'application/pdf') {
                feedbackMessage.textContent = 'Error: Hanya file PDF yang diizinkan.';
                feedbackMessage.classList.add('alert', 'alert-danger');
                return; // Hentikan eksekusi jika file bukan PDF
            }

            progressModal.show();
            feedbackMessage.textContent = ''; // Clear previous messages
            feedbackMessage.classList.remove('alert', 'alert-success', 'alert-danger', 'alert-warning');
        }

        xhr = new XMLHttpRequest();
        xhr.open('POST', uploadForm.action, true);

        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentProgress = (e.loaded / e.total) * 100;
                progressBar.style.width = `${percentProgress}%`;
                progressBar.setAttribute('aria-valuenow', percentProgress);
                progressText.textContent = `${Math.round(percentProgress)}%`; // Update percentage text
            }
        });

        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                const response = JSON.parse(xhr.responseText);
                
                if (response.message === "data uploaded") {
                    feedbackMessage.textContent = 'Modul berhasil ditambahkan.'; // Feedback on success
                    feedbackMessage.classList.add('alert', 'alert-success');
                    window.location.href = `/menu/modul/daftar-modul/${response.id_levelstudy}/${response.id_mapel}/`;
                } else {
                    feedbackMessage.textContent = 'Error: ' + response.message;
                    feedbackMessage.classList.add('alert', 'alert-danger');
                }
            } else {
                feedbackMessage.textContent = 'Error: Upload failed.';
                feedbackMessage.classList.add('alert', 'alert-danger');
            }
            progressModal.hide(); // Close the modal here for both success and error
        };

        xhr.onerror = function() {
            feedbackMessage.textContent = 'Network error: Upload failed.';
            feedbackMessage.classList.add('alert', 'alert-danger');
            progressModal.hide(); // Close the modal on network error
        };

        xhr.send(formData);
    });

    cancelButton.addEventListener('click', function() {
        if (xhr) {
            xhr.abort(); // Abort the request
        }
        progressModal.hide(); // Hide the modal
        feedbackMessage.textContent = 'Upload canceled.';
        feedbackMessage.classList.add('alert', 'alert-warning');
    });
});
