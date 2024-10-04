document.getElementById('uploadForm').addEventListener('submit', function (event) {
    event.preventDefault(); // Mencegah form dari pengiriman default

    const form = event.target;
    const formData = new FormData(form); // Membuat FormData untuk AJAX upload
    const progressModal = new bootstrap.Modal(document.getElementById('progressModal')); // Inisialisasi Bootstrap Modal
    const progressBar = document.getElementById('progressBar'); // Progress bar element
    const feedbackMessage = document.getElementById('feedbackMessage'); // Feedback message element

    // Reset feedback message and progress bar
    feedbackMessage.textContent = '';
    feedbackMessage.classList.remove('alert', 'alert-danger', 'alert-success');
    progressBar.style.width = '0%'; // Reset width progress bar

    // Tampilkan modal progress
    progressModal.show();

    const xhr = new XMLHttpRequest();
    xhr.open('POST', form.action, true); // Mengirim form data ke endpoint

    // Event listener untuk mengupdate progress bar
    xhr.upload.addEventListener('progress', function (e) {
        if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            progressBar.style.width = percentComplete + '%';
            progressBar.textContent = Math.round(percentComplete) + '%';
        }
    });

    // Event listener untuk menangani response dari server
    xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 300) {
            const response = JSON.parse(xhr.responseText);

            if (response.message === "data uploaded") {
                // Redirect ke halaman daftar modul jika upload berhasil
                window.location.href = `/menu/modul/daftar-modul/${response.id_levelstudy}/${response.id_mapel}/`;
            } else if (response.message === "cant upload") {
                progressModal.hide();
                // Menampilkan pesan kesalahan dari server (contoh: file ekstensi salah)
                let errorMessage = 'Error: ';
                if (response.errors) {
                    // Tampilkan kesalahan validasi form
                    errorMessage += 'Form errors: ' + JSON.stringify(response.errors);
                } else {
                    errorMessage += response.message;
                }
                feedbackMessage.textContent = errorMessage;
                feedbackMessage.classList.add('alert', 'alert-danger');
            } else {
                // Untuk case lainnya (general error)
                progressModal.hide();
                feedbackMessage.textContent = 'Error: ' + response.message;
                feedbackMessage.classList.add('alert', 'alert-danger');
            }
        } else {
            // Jika terjadi error pada status HTTP
            progressModal.hide();
            feedbackMessage.textContent = 'Error: Upload failed.';
            feedbackMessage.classList.add('alert', 'alert-danger');
        }
    };

    // Event listener untuk menangani error jaringan
    xhr.onerror = function () {
        // Tutup modal jika ada error jaringan
        progressModal.hide();
        feedbackMessage.textContent = 'Error: Network Error. Please try again.';
        feedbackMessage.classList.add('alert', 'alert-danger');
    };

    // Mengirim FormData dengan file yang diupload
    xhr.send(formData);
});
