document.addEventListener('DOMContentLoaded', function() {
    const stars = document.querySelectorAll('input[name="rating"]');
    const starLabels = document.querySelectorAll('.star-label i');
  
    // Hover effect
    starLabels.forEach((star, index) => {
      star.addEventListener('mouseenter', () => {
        updateStars(index);
      });
      star.addEventListener('mouseleave', () => {
        updateStars(getCheckedIndex());
      });
    });
  
    // Click effect
    stars.forEach((star, index) => {
      star.addEventListener('click', () => {
        updateStars(index);
      });
    });
  
    // Helper function to update star colors
    function updateStars(activeIndex) {
      starLabels.forEach((star, i) => {
        star.style.color = i <= activeIndex ? '#FFD700' : '#ddd';
      });
    }
  
    // Helper to find currently checked star index
    function getCheckedIndex() {
      return Array.from(stars).findIndex(star => star.checked);
    }
  
    // Set initial state
    updateStars(getCheckedIndex());
  });
  