document.addEventListener('DOMContentLoaded', () => {
  const scrollable = document.querySelector('.scrollable');

  document.addEventListener('wheel', (e) => {
    const isHovered = scrollable.matches(':hover');

    if (isHovered) {
      const atTop = scrollable.scrollTop === 0 && e.deltaY < 0;
      const atBottom = (scrollable.scrollTop + scrollable.clientHeight >= scrollable.scrollHeight - 1) && e.deltaY > 0;

      console.log('Scroll en scrollable', scrollable.scrollTop, e.deltaY);

      if (atTop || atBottom) {
        e.preventDefault(); // Evita que el scroll "escape"
        console.log('Scroll prevenido');
      }
    }
  }, { passive: false });
});
