document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.querySelector(".selector-toggle");
  const optionsList = document.querySelector(".selector-options");
  const selectedText = document.querySelector(".selected-language");
  const items = document.querySelectorAll(".selector-options li");
  const elements = document.querySelectorAll("[data-i18n]");

  const savedLang = localStorage.getItem("language") || (navigator.language.startsWith("es") ? "es" : "en");

  // Función para acceder a una clave anidada: getNested(data, 'home.welcome_message')
  function getNested(obj, path) {
    return path.split('.').reduce((acc, part) => acc && acc[part], obj);
  }

  function loadLanguage(lang) {
    fetch(`translations/${lang}.json`)
      .then(res => res.json())
      .then(data => {
        elements.forEach(el => {
          // Construir prefijo acumulando desde todos los ancestros
          let prefix = '';
          let current = el.parentElement;
          while (current) {
            if (current.hasAttribute('data-i18n-prefix')) {
              prefix = current.getAttribute('data-i18n-prefix') + (prefix ? '.' + prefix : '');
            }
            current = current.parentElement;
          }

          const key = prefix ? prefix + '.' + el.getAttribute("data-i18n") : el.getAttribute("data-i18n");
          const value = getNested(data, key);
          if (value) {
            el.innerHTML = value;
          } else {
            console.warn(`Traducción no encontrada: ${key}`);
          }
        });
        
      })
      .catch(err => console.error("Error cargando idioma:", err));
  }

  function updateLocalizedTime(lang) {
    const timeEl = document.querySelector(".stellaris-phantasm__time");
    if (!timeEl) return; // No hace nada si el elemento no está

    const eventInMadrid = new Date(Date.UTC(2025, 3, 27, 17, 0, 0));

    const formatter = new Intl.DateTimeFormat(lang, {
      weekday: "long",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      hour12: false
    });

    const formatted = formatter.format(eventInMadrid);
    const text = lang === "es"
      ? `Todos los ${formatted} (hora local)`
      : `Every ${formatted} (your local time)`;

    timeEl.textContent = text;
  }



  function setLanguage(lang) {
    localStorage.setItem("language", lang);
    selectedText.textContent = lang === "es" ? "Español" : "English";
    document.documentElement.setAttribute("lang", lang); // <- esta línea es esencial
    loadLanguage(lang);
    updateLocalizedTime(lang);
  }

  setLanguage(savedLang);

  toggleBtn.addEventListener("click", () => {
    const isOpen = optionsList.classList.toggle("open");
    toggleBtn.setAttribute("aria-expanded", isOpen);
  });

  items.forEach(item => {
    item.addEventListener("click", () => {
      const lang = item.dataset.lang;
      setLanguage(lang);
      toggleBtn.setAttribute("aria-expanded", "false");
      optionsList.classList.remove("open");
    });
  });

  document.addEventListener("click", e => {
    if (!e.target.closest(".custom-language-selector")) {
      toggleBtn.setAttribute("aria-expanded", "false");
      optionsList.classList.remove("open");
    }
  });
});
