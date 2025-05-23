document.querySelectorAll('.faq-question').forEach(btn => {
  btn.addEventListener('click', debounce(() => {
    const expanded = btn.getAttribute('aria-expanded') === 'true';
    const answer = btn.nextElementSibling;

    // Ignorar si está en transición (abriendo o cerrando)
    if (answer.dataset.transitioning === 'true') return;

    // Cerrar otros abiertos
    document.querySelectorAll('.faq-question[aria-expanded="true"]').forEach(openBtn => {
      if (openBtn !== btn) {
        openBtn.setAttribute('aria-expanded', 'false');
        closeAnswer(openBtn.nextElementSibling);
      }
    });

    if (expanded) {
      btn.setAttribute('aria-expanded', 'false');
      closeAnswer(answer);
    } else {
      btn.setAttribute('aria-expanded', 'true');
      openAnswer(answer);
    }
  }, 250));
});

function openAnswer(el) {
  el.dataset.transitioning = 'true';
  el.hidden = false;
  void el.offsetHeight; // Forzar reflow
  el.style.maxHeight = el.scrollHeight + 'px';
  el.classList.add('open');
  el.addEventListener('transitionend', function handler() {
    el.dataset.transitioning = 'false';
    el.removeEventListener('transitionend', handler);
  });
}

function closeAnswer(el) {
  el.dataset.transitioning = 'true';
  el.style.maxHeight = '0px';
  el.classList.remove('open');
  el.addEventListener('transitionend', function handler() {
    el.hidden = true;
    el.dataset.transitioning = 'false';
    el.removeEventListener('transitionend', handler);
  });
}

// Función debounce para limitar frecuencia de ejecuciones rápidas
function debounce(fn, delay) {
  let timeoutId;
  return function(...args) {
    if (timeoutId) return; // Ignorar si ya hay llamada pendiente
    fn.apply(this, args);
    timeoutId = setTimeout(() => {
      timeoutId = null;
    }, delay);
  };
}
