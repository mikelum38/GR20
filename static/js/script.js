document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.galleries-grid');
    const prevBtn = document.querySelector('.nav-prev');
    const nextBtn = document.querySelector('.nav-next');
    const cardWidth = 242; // 240px width + 2px gap

    if (!container || !prevBtn || !nextBtn) return;

    let currentPosition = 0;
    const maxScroll = container.scrollWidth - container.clientWidth;

    function updateNavigation() {
        // Toujours afficher les flèches pour l'instant
        prevBtn.style.display = 'flex';
        nextBtn.style.display = 'flex';
        
        // Désactiver les flèches si nécessaire
        prevBtn.disabled = currentPosition <= 0;
        nextBtn.disabled = currentPosition >= maxScroll;
    }

    function scrollGalleries(direction) {
        const scrollAmount = cardWidth;
        if (direction === 'prev') {
            currentPosition = Math.max(0, currentPosition - scrollAmount);
        } else {
            currentPosition = Math.min(maxScroll, currentPosition + scrollAmount);
        }
        
        container.style.transform = `translateX(-${currentPosition}px)`;
        updateNavigation();
    }

    prevBtn.addEventListener('click', () => scrollGalleries('prev'));
    nextBtn.addEventListener('click', () => scrollGalleries('next'));

    // Initial state
    updateNavigation();
});
