document.addEventListener('DOMContentLoaded', function() {
    const emailInput = document.getElementById('email');
    const suggestionsDiv = document.getElementById('email-suggestions');
    const protocol = window.location.protocol
    emailInput.addEventListener('input', async function(e) {
        const query = e.target.value;
        
        try {
            const response = await fetch(`${protocol}//${window.location.host}/menu/autocomplete-email/?term=${encodeURIComponent(query)}`);
            const emails = await response.json();
            
            // Bersihkan suggestions yang ada
            suggestionsDiv.innerHTML = '';
            
            if (emails.length > 0) {
                // Buat dan tampilkan suggestions
                const ul = document.createElement('ul');
                ul.className = 'list-group w-100';
                
                emails.forEach(email => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item list-group-item-action';
                    li.style.cursor = 'pointer';
                    
                    // Highlight bagian yang cocok dengan query
                    const regex = new RegExp(`(${query})`, 'gi');
                    const highlightedEmail = email.replace(regex, '<strong>$1</strong>');
                    li.innerHTML = highlightedEmail;
                    
                    // Event ketika suggestion diklik
                    li.addEventListener('click', function() {
                        emailInput.value = email;
                        suggestionsDiv.innerHTML = ''; // Tutup suggestion
                    });
                    
                    ul.appendChild(li);
                });
                
                suggestionsDiv.appendChild(ul);
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    });

    // Tutup suggestions ketika klik di luar
    document.addEventListener('click', function(e) {
        if (!emailInput.contains(e.target) && !suggestionsDiv.contains(e.target)) {
            suggestionsDiv.innerHTML = '';
        }
    });

    // Navigasi dengan keyboard
    emailInput.addEventListener('keydown', function(e) {
        const suggestions = suggestionsDiv.querySelectorAll('li');
        let currentFocus = -1;

        if (suggestions.length > 0) {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                
                // Remove active class from current item
                if (currentFocus >= 0) {
                    suggestions[currentFocus].classList.remove('active');
                }

                // Move focus up or down
                if (e.key === 'ArrowDown') {
                    currentFocus = (currentFocus + 1) % suggestions.length;
                } else {
                    currentFocus = currentFocus <= 0 ? suggestions.length - 1 : currentFocus - 1;
                }

                // Add active class to new focused item
                suggestions[currentFocus].classList.add('active');
                emailInput.value = suggestions[currentFocus].textContent;
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (currentFocus > -1) {
                    suggestions[currentFocus].click();
                }
            }
        }
    });
});