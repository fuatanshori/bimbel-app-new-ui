// static/ujian/js/forms.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const requiredFields = ['soal', 'jawaban_1', 'jawaban_2', 'jawaban_3', 'jawaban_4'];
    
    if (!form) return;

    form.addEventListener('submit', function(e) {
        let hasError = false;
        
        requiredFields.forEach(fieldName => {
            const editorElement = document.querySelector(`#id_${fieldName}`);
            if (!editorElement || !editorElement.ckeditor) return;

            const content = editorElement.ckeditor.getData().trim();
            const formGroup = editorElement.closest('.row.mb-3');
            const errorElement = formGroup.querySelector('small.text-muted');
            
            // Check if empty or only contains HTML spaces
            if (!content || 
                content === '<p>&nbsp;</p>' || 
                content === '<p></p>' || 
                content === '<p> </p>') {
                e.preventDefault();
                hasError = true;
                
                // Add error styling
                const editorContainer = editorElement.closest('.django_ckeditor_5');
                if (editorContainer) {
                    editorContainer.style.border = '2px solid #dc3545';
                }
                
                if (errorElement) {
                    errorElement.className = 'text-danger small';
                    errorElement.textContent = `${fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} wajib diisi`;
                }
            }
        });
        
        if (hasError) {
            const firstError = document.querySelector('.django_ckeditor_5[style*="border"]');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            return false;
        }
    });

    // Remove error styling when typing
    requiredFields.forEach(fieldName => {
        const editorElement = document.querySelector(`#id_${fieldName}`);
        if (!editorElement || !editorElement.ckeditor) return;

        editorElement.ckeditor.model.document.on('change:data', () => {
            const content = editorElement.ckeditor.getData().trim();
            const formGroup = editorElement.closest('.row.mb-3');
            const errorElement = formGroup.querySelector('small.text-muted');
            
            if (content && 
                content !== '<p>&nbsp;</p>' && 
                content !== '<p></p>' && 
                content !== '<p> </p>') {
                const editorContainer = editorElement.closest('.django_ckeditor_5');
                if (editorContainer) {
                    editorContainer.style.border = '';
                }
                
                if (errorElement) {
                    errorElement.className = 'text-muted small';
                    errorElement.textContent = '';
                }
            }
        });
    });
});