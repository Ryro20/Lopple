const cards = document.querySelectorAll('.card');
const states = new WeakMap();

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    const el = entry.target;
    const currentState = states.get(el) || null;

    if (entry.isIntersecting) {
      if (currentState === 'animatingOut') {
        el.removeEventListener('transitionend', onOutEnd);
        states.set(el, null);
      }
      if (!el.classList.contains('visible') && currentState !== 'animatingIn') {
        el.classList.add('visible');
        states.set(el, 'animatingIn');
        el.addEventListener('transitionend', onInEnd);
      }

    } else {

      if (!el.classList.contains('visible') || currentState === 'animatingOut') return;

      if (currentState === 'animatingIn') {
        el.addEventListener('transitionend', onOutStartOnce);
      } else {

        startExit(el);
      }
    }
  });
}, { threshold: 0.5 });

cards.forEach(card => observer.observe(card));

function onInEnd(e) {
  if (e.propertyName !== 'transform' && e.propertyName !== 'opacity') return;
  const el = e.currentTarget;
  el.removeEventListener('transitionend', onInEnd);
  states.set(el, null);
}

function onOutStartOnce(e) {
  if (e.propertyName !== 'transform' && e.propertyName !== 'opacity') return;
  const el = e.currentTarget;
  el.removeEventListener('transitionend', onOutStartOnce);
  startExit(el);
}

function startExit(el) {
  el.classList.remove('visible');
  states.set(el, 'animatingOut');
  el.addEventListener('transitionend', onOutEnd);
}

function onOutEnd(e) {
  if (e.propertyName !== 'transform' && e.propertyName !== 'opacity') return;
  const el = e.currentTarget;
  el.removeEventListener('transitionend', onOutEnd);
  states.set(el, null);
}
