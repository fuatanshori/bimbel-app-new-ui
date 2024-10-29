document.addEventListener('DOMContentLoaded', function() {
    // Handle star rating
    const stars = document.querySelectorAll('input[name="rating"]');
    
    stars.forEach((star, index) => {
      star.addEventListener('click', () => {
        stars.forEach((s, i) => {
          const label = s.nextElementSibling;
          if (i <= index) {
            s.checked = true;
            label.querySelector('i').style.color = '#FFD700';
          } else {
            s.checked = false;
            label.querySelector('i').style.color = '#ddd';
          }
        });
      });
    });
  
    const initialRating = document.querySelector('input[name="rating"]:checked');
    if (initialRating) {
      const index = Array.from(stars).indexOf(initialRating);
      stars.forEach((s, i) => {
        const label = s.nextElementSibling;
        if (i <= index) {
          label.querySelector('i').style.color = '#FFD700';
        }
      });
    }
  
    const textarea = document.getElementById('testimonial');
    const charCount = document.getElementById('charCount');
  
    function updateCharCount() {
      const count = textarea.value.length;
      charCount.textContent = count;
      
      if (count >= 55) {
        charCount.style.color = '#dc3545';
      } else {
        charCount.style.color = '#666';
      }
    }
  
    textarea.addEventListener('input', updateCharCount);
    updateCharCount();
  });