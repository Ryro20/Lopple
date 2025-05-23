const sidebar = document.getElementById("sidebar");
const toggle = document.getElementById("button-toggle");

toggle.addEventListener("click", () => {
  if (sidebar.classList.contains("hidden")) {
    sidebar.style.transitionDelay = "0.05s"; // Delay al abrir
    sidebar.classList.remove("hidden");
  } else {
    sidebar.style.transitionDelay = "0s"; // Sin delay al cerrar
    sidebar.classList.add("hidden");
  }

  toggle.classList.toggle("closed");
  toggle.classList.toggle("open");
});

// Soporte accesibilidad: permite activar con Enter o Espacio
toggle.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    toggle.click(); // Simula clic
  }
});
