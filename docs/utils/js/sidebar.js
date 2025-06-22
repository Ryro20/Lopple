const sidebar = document.getElementById("sidebar");
const toggle = document.getElementById("button-toggle");

// === Al cargar la página, recuperar estado ===
document.addEventListener("DOMContentLoaded", () => {
  const isSidebarHidden = localStorage.getItem("sidebarHidden") === "true";

  if (isSidebarHidden) {
    sidebar.classList.add("hidden");
    toggle.classList.add("closed");
    toggle.classList.remove("open");
  } else {
    sidebar.classList.remove("hidden");
    toggle.classList.add("open");
    toggle.classList.remove("closed");
  }
});

toggle.addEventListener("click", () => {
  const isHidden = sidebar.classList.contains("hidden");

  if (isHidden) {
    sidebar.style.transitionDelay = "0.05s"; // Delay al abrir
    sidebar.classList.remove("hidden");
  } else {
    sidebar.style.transitionDelay = "0s"; // Sin delay al cerrar
    sidebar.classList.add("hidden");
  }

  toggle.classList.toggle("closed");
  toggle.classList.toggle("open");

  // === Guardar estado en localStorage ===
  localStorage.setItem("sidebarHidden", !isHidden);
});

// Soporte accesibilidad: permite activar con Enter o Espacio
toggle.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    toggle.click(); // Simula clic
  }
});
