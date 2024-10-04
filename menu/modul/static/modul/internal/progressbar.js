document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload_form');
    const inputFileModul = document.getElementById("id_modul");
    const inputFileVidio = document.getElementById("id_vidio"); // Ganti ini sesuai dengan id field untuk video
    const progressModal = new bootstrap.Modal(document.getElementById('progressModal'));
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.getElementById('progressText');
    const cancelButton = document.getElementById('cancelButton');
    const feedbackMessage = document.getElementById('feedbackMessage');
    let xhr;

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(uploadForm);
        const fileModul = inputFileModul.files[0];
        const fileVidio = inputFileVidio ? inputFileVidio.files[0] : null; // Jika ada file video

        // Cek ukuran file modul (maks 20MB)
        if (fileModul && fileModul.size > 20 * 1024 * 1024) {
            feedbackMessage.textContent = 'Error: File modul tidak boleh lebih dari 20MB.';
            feedbackMessage.classList.add('alert', 'alert-danger');
            progressModal.hide();
            return; // Stop the process if the file is too large
        }

        // Cek ukuran file vidio (maks 200MB)
        if (fileVidio && fileVidio.size > 200 * 1024 * 1024) {
            feedbackMessage.textContent = 'Error: Video tidak boleh lebih dari 200MB.';
            feedbackMessage.classList.add('alert', 'alert-danger');
            progressModal.hide();
            return; // Stop the process if the file is too large
        }

        // Jika semua ukuran file valid, lanjutkan dengan upload
        if (fileModul || fileVidio) {
            progressModal.show();
            feedbackMessage.textContent = ''; // Hapus pesan sebelumnya
            feedbackMessage.classList.remove('text-success', 'text-danger', 'text-warning');
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
                    window.location.href = `/menu/modul/daftar-modul/${response.id_levelstudy}/${response.id_mapel}/`;
                } else if (response.data === "cant upload") {
                    let errorMessage = 'Error: ';
                    if (response.errors) {
                        errorMessage += 'Form errors: ' + JSON.stringify(response.errors);
                    } else {
                        errorMessage += response.message;
                    }
                    progressModal.hide();
                    feedbackMessage.textContent = errorMessage;
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
    });

    cancelButton.addEventListener('click', function() {
        if (xhr) {
            xhr.abort();
        }
        progressModal.hide();
        feedbackMessage.textContent = 'Upload canceled.';
        feedbackMessage.classList.add('alert', 'alert-warning');
    });
});
