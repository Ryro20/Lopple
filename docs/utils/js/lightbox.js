document.addEventListener('DOMContentLoaded', () => {
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightbox-img');
  const closeBtn = document.getElementById('lightbox-close');

  const previewImages = document.querySelectorAll('.card-gif img');

  previewImages.forEach(img => {
    img.style.cursor = 'pointer';
    img.addEventListener('click', () => {
      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt || 'Vista ampliada';

      lightbox.removeAttribute('hidden');
      // Forzar reflow para activar la transición
      void lightbox.offsetWidth;

      lightbox.classList.add('visible');
      document.body.style.overflow = 'hidden';
      lightbox.focus();
    });
  });

  function closeLightbox() {
    lightbox.classList.remove('visible');
    document.body.style.overflow = '';

    // Esperar a que termine la transición para ocultar el lightbox
    lightbox.addEventListener('transitionend', function handler(e) {
      if (e.propertyName === 'opacity' && !lightbox.classList.contains('visible')) {
        lightbox.setAttribute('hidden', '');
        lightboxImg.src = '';
        lightbox.removeEventListener('transitionend', handler);
      }
    });
  }

  closeBtn.addEventListener('click', closeLightbox);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !lightbox.hasAttribute('hidden')) {
      closeLightbox();
    }
  });

  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) {
      closeLightbox();
    }
  });
});
