<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Lopple Bot - Documentación</title>
  <link rel="stylesheet" href="assets/style.css" />
</head>
<body>
  <div class="sidebar">
    <h1>Lopple</h1>
    <a href="#inicio">Inicio</a>
    <a href="#comandos">Comandos</a>
    <a href="#acerca">Acerca del bot</a>
    <a href="#documentacion">Documentación extra</a>
  </div>
  <div class="main">
    <section id="inicio">
      <h2>Inicio</h2>
      <img src="assets/banner.png" alt="Banner del bot" />
      <p>Bienvenido a la documentación oficial del bot <strong>Lopple</strong>. Aquí podrás encontrar información detallada sobre su funcionamiento y comandos disponibles.</p>
    </section>

    <section id="comandos">
      <h2>Comandos disponibles</h2>
      <div class="comando">
        <h3><code>/purgeall</code></h3>
        <p>Elimina todos los mensajes del canal actual. Solo los usuarios con permisos adecuados pueden utilizarlo.</p>
        <ul>
          <li><strong>Uso:</strong> <code>/purgeall</code></li>
          <li><strong>Permisos necesarios:</strong> Administrador o Gestionar mensajes</li>
        </ul>
      </div>
      <div class="comando">
        <h3><code>/delete_registers</code></h3>
        <p>Elimina todos los registros guardados previamente por el bot.</p>
        <ul>
          <li><strong>Uso:</strong> <code>/delete_registers</code></li>
          <li><strong>Permisos necesarios:</strong> Administrador</li>
        </ul>
      </div>
      <div class="comando">
        <h3><code>/change_extrapulls</code></h3>
        <p>Modifica el número de extra pulls disponibles para un equipo o usuario.</p>
        <ul>
          <li><strong>Uso:</strong> <code>/change_extrapulls cantidad: 5</code></li>
          <li><strong>Permisos necesarios:</strong> Administrador</li>
        </ul>
      </div>
      <div class="comando">
        <h3><code>/round_pull</code></h3>
        <p>Ejecuta una ronda de pulls para todos los equipos registrados.</p>
        <ul>
          <li><strong>Uso:</strong> <code>/round_pull</code></li>
          <li><strong>Permisos necesarios:</strong> Administrador</li>
        </ul>
      </div>
      <div class="comando">
        <h3><code>/extra_pull</code></h3>
        <p>Realiza un pull adicional para un equipo que tenga extra pulls disponibles.</p>
        <ul>
          <li><strong>Uso:</strong> <code>/extra_pull equipo: Nombre</code></li>
          <li><strong>Permisos necesarios:</strong> Administrador</li>
        </ul>
      </div>
      <div class="comando">
        <h3><code>/test_pull</code></h3>
        <p>Realiza un pull de prueba para simular resultados sin afectar los registros.</p>
        <ul>
          <li><strong>Uso:</strong> <code>/test_pull</code></li>
          <li><strong>Permisos necesarios:</strong> Cualquiera</li>
        </ul>
      </div>
      <div class="comando">
        <h3><code>/register_team</code></h3>
        <p>Registra un nuevo equipo en el sistema del bot.</p>
        <ul>
          <li><strong>Uso:</strong> <code>/register_team nombre: "Nombre del equipo"</code></li>
          <li><strong>Permisos necesarios:</strong> Administrador</li>
        </ul>
      </div>
      <div class="comando">
        <h3><code>/edit_registered_teams</code></h3>
        <p>Edita la información de los equipos ya registrados.</p>
        <ul>
          <li><strong>Uso:</strong> <code>/edit_registered_teams equipo: "Nombre" campo: "valor nuevo"</code></li>
          <li><strong>Permisos necesarios:</strong> Administrador</li>
        </ul>
      </div>
      <div class="comando">
        <h3><code>/add_member_team</code></h3>
        <p>Añade un nuevo miembro a un equipo ya registrado.</p>
        <ul>
          <li><strong>Uso:</strong> <code>/add_member_team equipo: "Nombre" usuario: @usuario</code></li>
          <li><strong>Permisos necesarios:</strong> Administrador</li>
        </ul>
      </div>
    </section>

    <section id="acerca">
      <h2>Acerca del bot</h2>
      <p>Lopple es un bot de Discord diseñado para gestionar equipos y sorteos. Su objetivo principal es ofrecer una experiencia automatizada, flexible y visualmente atractiva. Incluye comandos de gestión, utilidades de sorteo y soporte visual mediante embeds y reacciones.</p>
    </section>

    <section id="documentacion">
      <h2>Documentación extra</h2>
      <p>Aquí se mostrarán ejemplos visuales del funcionamiento del bot, cómo configurar un equipo, usar comandos y aprovechar al máximo sus funcionalidades.</p>
      <img src="assets/ejemplo-collage.png" alt="Ejemplo de uso del bot" />
    </section>
  </div>
</body>
</html>
