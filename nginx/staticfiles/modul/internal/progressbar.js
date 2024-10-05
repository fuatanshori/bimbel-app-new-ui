document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload_form');
    const inputFileModul = document.getElementById("id_modul");
    const inputFileVidio = document.getElementById("id_vidio");
    const progressModal = new bootstrap.Modal(document.getElementById('progressModal'));
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.getElementById('progressText');
    const cancelButton = document.getElementById('cancelButton');
    const feedbackMessage = document.getElementById('feedbackMessage');
    const submitButton = document.getElementById('submitButton'); // Assuming you have a submit button
    let xhr;

    // Function untuk validasi ukuran file dan tipe file
    function validateFiles() {
        const fileModul = inputFileModul.files[0];
        const fileVidio = inputFileVidio.files[0];

        // Cek ukuran file modul (maks 100MB)
        if (fileModul && fileModul.size > 100 * 1024 * 1024) {
            feedbackMessage.textContent = 'Error: File modul tidak boleh lebih dari 100MB.';
            feedbackMessage.classList.add('alert', 'alert-danger');
            return false; // Tidak valid
        }

        // Cek tipe file modul (hanya .pdf)
        if (fileModul && !fileModul.name.endsWith('.pdf')) {
            feedbackMessage.textContent = 'Error: File modul harus berformat PDF.';
            feedbackMessage.classList.add('alert', 'alert-danger');
            return false; // Tidak valid
        }

        // Cek ukuran file vidio (maks 300MB)
        if (fileVidio && fileVidio.size > 300 * 1024 * 1024) {
            feedbackMessage.textContent = 'Error: Video tidak boleh lebih dari 300MB.';
            feedbackMessage.classList.add('alert', 'alert-danger');
            return false; // Tidak valid
        }

        // Cek tipe file vidio (hanya .mp4)
        if (fileVidio && !fileVidio.name.endsWith('.mp4')) {
            feedbackMessage.textContent = 'Error: File video harus berformat MP4.';
            feedbackMessage.classList.add('alert', 'alert-danger');
            return false; // Tidak valid
        }

        return true; // Valid
    }

    // Function untuk melakukan upload file jika valid
    function uploadFiles() {
        const formData = new FormData(uploadForm);
        xhr = new XMLHttpRequest();
        xhr.open('POST', uploadForm.action, true);

        // Tampilkan modal progress
        progressModal.show();
        feedbackMessage.textContent = ''; // Hapus pesan sebelumnya
        feedbackMessage.classList.remove('alert-danger', 'alert-warning', 'alert-success');
        
        // Reset progress bar
        progressBar.style.width = '0%';
        progressBar.setAttribute('aria-valuenow', 0);
        progressText.textContent = '0%';

        // Disable the submit button to prevent multiple uploads
        submitButton.disabled = true;

        // Update progress bar
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentProgress = (e.loaded / e.total) * 100;
                progressBar.style.width = `${percentProgress}%`;
                progressBar.setAttribute('aria-valuenow', percentProgress);
                progressText.textContent = `${Math.round(percentProgress)}%`; // Update percentage text
            }
        });

        // Handle response dari server
        xhr.onload = function() {
            submitButton.disabled = false; // Enable the submit button after upload is done
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
            submitButton.disabled = false; // Enable the submit button on error
            progressModal.hide();
            feedbackMessage.textContent = 'Network error: Upload failed.';
            feedbackMessage.classList.add('text-danger');
        };

        xhr.send(formData); // Kirim form jika validasi sukses
    }

    // Event listener pada form submit
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault(); // Stop submit form default behavior

        // Lakukan validasi
        if (validateFiles()) {
            // Jika validasi berhasil, lakukan upload
            uploadFiles();
        }
    });

    // Event listener untuk membatalkan upload
    cancelButton.addEventListener('click', function() {
        if (xhr) {
            xhr.abort(); // Batalkan request jika ada
        }
        progressModal.hide();
        feedbackMessage.textContent = 'Upload canceled.';
        feedbackMessage.classList.add('alert', 'alert-warning');
        submitButton.disabled = false; // Enable the submit button on cancel
    });
});
