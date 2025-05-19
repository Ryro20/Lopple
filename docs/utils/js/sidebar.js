document.addEventListener('DOMContentLoaded', function () {
  const toggleButton = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');

  toggleButton.addEventListener('click', function () {
    sidebar.classList.toggle('hidden');   // Oculta o muestra la sidebar
    this.classList.toggle('open');        // Activa la animación del botón
  });
});
