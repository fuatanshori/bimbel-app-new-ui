document.addEventListener('DOMContentLoaded', function () {
    var messages = document.querySelectorAll('#message');
    messages.forEach(function (message) {
        var duration = message.getAttribute('data-duration');
        setTimeout(function () {
            message.style.transition = 'opacity 0.5s';
            message.style.opacity = 0;
            setTimeout(function () {
                message.remove();
            }, 500); // Tunggu sampai transisi selesai sebelum menghapus elemen
        }, duration);
    });
});