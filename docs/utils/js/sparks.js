

function createSparksOnElement(container) {
  if (!container) return;

  const minSparks = 40;
  const maxSparks = 50;
  const count = Math.floor(Math.random() * (maxSparks - minSparks + 1)) + minSparks;

  container.querySelectorAll('.spark').forEach(s => s.remove());

  const width = container.clientWidth;
  const height = container.clientHeight;
  const margin = 20;

  for (let i = 0; i < count; i++) {
    const spark = document.createElement('span');
    spark.classList.add('spark');

    const x = Math.random() * (width - margin * 2) + margin;
    const y = Math.random() * (height - margin * 2) + margin;

    spark.style.left = `${x}px`;
    spark.style.top = `${y}px`;
    spark.style.animationDelay = `${Math.random() * 2}s`;

    container.appendChild(spark);
    animateSpark(spark, margin);
  }
}

function animateSpark(el, margin = 20) {
  let posX = parseFloat(el.style.left);
  let posY = parseFloat(el.style.top);

  let directionX = (Math.random() - 0.5) * 0.5;
  let directionY = (Math.random() - 0.5) * 0.5;

  function move() {
    const parentWidth = el.parentElement.clientWidth;
    const parentHeight = el.parentElement.clientHeight;

    posX += directionX;
    posY += directionY;

    if (posX < margin) {
      posX = margin;
      directionX = Math.abs(directionX);
    }
    if (posX > parentWidth - margin) {
      posX = parentWidth - margin;
      directionX = -Math.abs(directionX);
    }
    if (posY < margin) {
      posY = margin;
      directionY = Math.abs(directionY);
    }
    if (posY > parentHeight - margin) {
      posY = parentHeight - margin;
      directionY = -Math.abs(directionY);
    }

    el.style.left = posX + 'px';
    el.style.top = posY + 'px';

    requestAnimationFrame(move);
  }

  move();
}

// Para todas las .card-title
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('.card').forEach(card => {
    createSparksOnElement(card);
  });
});

// Para otras secciones individuales
createSparksOnElement(document.querySelector('.cta-section'));

createSparksOnElement(document.getElementById('banner'));