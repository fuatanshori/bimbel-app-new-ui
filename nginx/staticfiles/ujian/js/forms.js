document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    
    form.addEventListener('submit', function(e) {
        const editors = document.querySelectorAll('.django_ckeditor_5');
        let hasError = false;
        
        editors.forEach(editor => {
            const editorInstance = editor.ckeditor;
            if (editorInstance) {
                const content = editorInstance.getData().trim();
                const field = editor.closest('.form-group');
                const errorDiv = field.querySelector('.invalid-feedback') || document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                
                // Check if content is empty or just HTML spaces
                if (!content || content === '<p>&nbsp;</p>' || content === '<p></p>' || content === '<p> </p>') {
                    e.preventDefault();
                    hasError = true;
                    editor.style.border = '2px solid #dc3545';
                    errorDiv.textContent = 'Field ini tidak boleh kosong';
                    errorDiv.style.display = 'block';
                    if (!field.querySelector('.invalid-feedback')) {
                        field.appendChild(errorDiv);
                    }
                } else {
                    editor.style.border = '';
                    errorDiv.style.display = 'none';
                }
            }
        });
        
        if (hasError) {
            // Scroll to first error
            const firstError = document.querySelector('.django_ckeditor_5[style*="border"]');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    });
    
    // Remove error styling when user starts typing
    document.addEventListener('keyup', function(e) {
        const editor = e.target.closest('.django_ckeditor_5');
        if (editor) {
            editor.style.border = '';
            const errorDiv = editor.closest('.form-group').querySelector('.invalid-feedback');
            if (errorDiv) {
                errorDiv.style.display = 'none';
            }
        }
    });
});