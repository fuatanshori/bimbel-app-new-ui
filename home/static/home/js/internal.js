const buttons = document.querySelectorAll('.btn-code');

    buttons.forEach(button => {
        button.addEventListener('click', function() {
            // Ambil teks di dalam tombol yang diklik
            const textToCopy = this.innerText;

            // Buat elemen textarea sementara untuk menyalin teks
            const tempInput = document.createElement('textarea');
            tempInput.value = textToCopy;
            document.body.appendChild(tempInput);

            // Pilih teks dan salin
            tempInput.select();
            document.execCommand('copy');

            // Hapus elemen sementara
            document.body.removeChild(tempInput);

            // Tampilkan pesan sukses
            const feedback = document.getElementById('feedbackMessage');
            feedback.style.display = 'block';

            // Sembunyikan pesan setelah beberapa detik
            setTimeout(() => {
                feedback.style.display = 'none';
            }, 4000);
        });
    });
    function showFeedbackMessage() {
      const feedbackMessage = document.getElementById('feedbackMessage');
      feedbackMessage.style.display = 'block'; // Show the alert
      setTimeout(() => {
          feedbackMessage.style.display = 'none'; // Hide after 3 seconds
      }, 3000); // Adjust the duration as needed
  }
  
  // Example usage: Call this function when the discount code is copied
  document.querySelectorAll('.btn-code').forEach(button => {
      button.addEventListener('click', () => {
          showFeedbackMessage();
      });
  });