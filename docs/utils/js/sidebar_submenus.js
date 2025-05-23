
document.addEventListener("DOMContentLoaded", async () => {
  const containers = document.querySelectorAll('.submenu-container');

  containers.forEach(async (container) => {
    const toggle = container.querySelector('.submenu-toggle');
    const sublist = container.querySelector('.submenu-list');
    const link = container.querySelector('.submenu-link a');

    if (!toggle || !sublist || !link) return;

    // Inicializar aria-expanded en false
    toggle.setAttribute('aria-expanded', 'false');

    // Mostrar/ocultar el submenú al hacer clic
    toggle.addEventListener('click', (e) => {
      e.preventDefault();
      const isVisible = sublist.classList.toggle('visible');
      
      // Actualizar aria-expanded según estado
      toggle.setAttribute('aria-expanded', isVisible ? 'true' : 'false');

      // Rotar icono
      toggle.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(-90deg)';
    });

    // Si es el menú de Commands, cargar dinámicamente los comandos
    const isCommands = link.getAttribute('href') === 'comandos.html#commands';

    if (isCommands) {
      try {
        const response = await fetch('./comandos.html');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const text = await response.text();
        const doc = new DOMParser().parseFromString(text, 'text/html');

        const comandos = doc.querySelectorAll('h3 code');
        comandos.forEach(cmd => {
          const nombre = cmd.textContent.replace('/', '');
          const li = document.createElement('li');
          li.innerHTML = `<a href="comandos.html#${nombre}">${cmd.textContent}</a>`;
          sublist.appendChild(li);
        });
      } catch (error) {
        console.error('Error cargando comandos:', error);
      }
    }
  });
});
