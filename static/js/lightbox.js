document.addEventListener('DOMContentLoaded', function() {
    const lightboxTemplate = `
        <div class="lightbox">
            <div class="lightbox-content">
                <img id="lightbox-image" src="" alt="">
            </div>
            <button class="lightbox-prev">&lt;</button>
            <button class="lightbox-next">&gt;</button>
            <button class="lightbox-close">&times;</button>
            <div class="spinner"></div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', lightboxTemplate);

    const lightbox = document.querySelector('.lightbox');
    const lightboxImage = document.querySelector('#lightbox-image');
    const prevButton = document.querySelector('.lightbox-prev');
    const nextButton = document.querySelector('.lightbox-next');
    const closeButton = document.querySelector('.lightbox-close');
    const spinner = document.querySelector('.spinner');

    let currentImageIndex = 0;
    let images = [];

    // Fonction pour ouvrir la lightbox
    function openLightbox(clickedImage) {
        images = Array.from(document.querySelectorAll('[data-lightbox="gallery"]'));
        currentImageIndex = images.indexOf(clickedImage);
        updateLightboxImage();
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    // Fonction pour fermer la lightbox
    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Fonction pour mettre à jour l'image dans la lightbox
    function updateLightboxImage() {
        const image = images[currentImageIndex];
        spinner.style.display = 'block';
        lightboxImage.style.display = 'none';
        
        lightboxImage.src = image.href;
        lightboxImage.alt = image.querySelector('img').alt;

        lightboxImage.onload = function() {
            spinner.style.display = 'none';
            lightboxImage.style.display = 'block';
        };

        // Mise à jour de la visibilité des boutons de navigation
        prevButton.style.display = currentImageIndex > 0 ? 'flex' : 'none';
        nextButton.style.display = currentImageIndex < images.length - 1 ? 'flex' : 'none';
    }

    // Gestionnaires d'événements pour la navigation
    prevButton.addEventListener('click', function() {
        if (currentImageIndex > 0) {
            currentImageIndex--;
            updateLightboxImage();
        }
    });

    nextButton.addEventListener('click', function() {
        if (currentImageIndex < images.length - 1) {
            currentImageIndex++;
            updateLightboxImage();
        }
    });

    // Fermeture de la lightbox
    closeButton.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });

    // Navigation au clavier
    document.addEventListener('keydown', function(e) {
        if (!lightbox.classList.contains('active')) return;

        switch(e.key) {
            case 'ArrowLeft':
                if (currentImageIndex > 0) {
                    currentImageIndex--;
                    updateLightboxImage();
                }
                break;
            case 'ArrowRight':
                if (currentImageIndex < images.length - 1) {
                    currentImageIndex++;
                    updateLightboxImage();
                }
                break;
            case 'Escape':
                closeLightbox();
                break;
        }
    });

    // Ajout des gestionnaires d'événements aux images de la galerie
    document.addEventListener('click', function(e) {
        const link = e.target.closest('[data-lightbox="gallery"]');
        if (link) {
            e.preventDefault();
            openLightbox(link);
        }
    });
});
