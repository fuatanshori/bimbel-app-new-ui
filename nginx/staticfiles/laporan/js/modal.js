document.addEventListener('DOMContentLoaded', function() {
    // Get the export form and the modal
    const exportForm = document.querySelector('#excelModal form');
    const excelModal = new bootstrap.Modal(document.getElementById('excelModal'));

    // Add a submit event listener to the form
    exportForm.addEventListener('submit', function(event) {
        // Close the modal after submission
        excelModal.hide();
    });
});