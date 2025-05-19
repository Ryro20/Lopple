document.addEventListener("DOMContentLoaded", async () => {
  const toggle = document.querySelector('.comandos-toggle');
  const sublist = document.querySelector('.subcomandos-list');

  if (!toggle || !sublist) {
    console.warn("Toggle o sublist no encontrados.");
    return;
  }

  toggle.addEventListener('click', (e) => {
    e.preventDefault();
    sublist.classList.toggle('visible');
    toggle.style.transform = sublist.classList.contains('visible') ? 'rotate(0deg)' : 'rotate(-90deg)';
  });

  try {
    const pageRoot = location.pathname.includes('comandos') ? './comandos.html' : './comandos.html';
    const response = await fetch(pageRoot);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const text = await response.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(text, 'text/html');

    const comandos = doc.querySelectorAll('.comando h3 code');
    console.log(`Comandos encontrados: ${comandos.length}`);

    if (comandos.length === 0) {
      console.warn("No se detectaron comandos. ¿Está bien la estructura HTML?");
    }

    comandos.forEach((cmd) => {
      const nombre = cmd.textContent.replace('/', '');
      const li = document.createElement('li');
      li.innerHTML = `<a href="comandos.html#${nombre}">${cmd.textContent}</a>`;
      sublist.appendChild(li);
    });

    console.log("Comandos añadidos.");
  } catch (error) {
    console.error('Error cargando comandos:', error);
  }
});
