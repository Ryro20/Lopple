import discord
import asyncio
import re
from utils.bot_instance import bot
from utils.claves import (
    CANAL_DE_REGISTROS_ID,
    MESSAGE_ID_REGISTRO_DURO,
    CATEGORY_ID
)
from comandos.pulls.constantes_pull import guild_locks

def limpiar_desc(texto):
    lineas_validas = []
    for linea in texto.splitlines():
        linea_sin_simbolos = re.sub(r"^[^A-Za-z]*", "", linea)
        if linea_sin_simbolos.startswith(("Team", "Players", "Extra pulls")):
            lineas_validas.append(linea)
    return "\n".join(lineas_validas)

async def get_guild_lock(guild_id: int) -> asyncio.Lock:
    if guild_id not in guild_locks:
        guild_locks[guild_id] = asyncio.Lock()
    return guild_locks[guild_id]

async def create_team_role(guild: discord.Guild, team_name: str):
    # Crear el rol para el equipo
    rol_equipo = await guild.create_role(name=team_name, hoist=True)
    return rol_equipo

async def assign_players_to_role(guild, players, role):
    miembros_asignados = []
    for player in players:
        member = await guild.fetch_member(player.id)
        if member:
            await member.add_roles(role)
            miembros_asignados.append(member)
        else:
            raise ValueError(f"{player.display_name} could not be found")
    return miembros_asignados


async def create_team_channel(guild: discord.Guild, team_name: str, rol_equipo: discord.Role, miembros: list[discord.Member]):
    category = discord.utils.get(guild.categories, id=CATEGORY_ID)
    if category is None:
        raise ValueError(f"Category with ID {CATEGORY_ID} was not found.")

    channel_name = team_name.lower().replace(" ", "-")

    canal_existente = discord.utils.get(
        guild.text_channels,
        name=channel_name,
        category_id=CATEGORY_ID
    )
    if canal_existente:
        print(f"⚠️ Canal ya existía: {canal_existente.name}")
        return canal_existente

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=False,
            use_application_commands=False
        ),
        rol_equipo: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            use_application_commands=True
        )
    }

    canal = await guild.create_text_channel(
        name=channel_name,
        category=category,
        overwrites=overwrites
    )
    print(f"✅ Canal creado: {canal.name}")

    if miembros:
        jugadores_listados = "\n".join(member.mention for member in miembros)
        mensaje = (
            f"Welcome to your team channel, {rol_equipo.mention}!\n"
            f"{jugadores_listados}\n🎉\nOnly members of this team can write and use commands here."
        )
    else:
        mensaje = (
            f"Welcome to your team channel, {rol_equipo.mention}!\n"
            f"No players assigned yet.\n🎉\nOnly members of this team can write and use commands here."
        )

    await canal.send(mensaje)

def parse_embed_description(embed: discord.Embed) -> dict[str, dict[str, list[int] | int]]:

    equipos: dict[str, dict[str, list[int] | int]] = {}
    current_team: str | None = None
    import re

    for line in (embed.description or "").splitlines():
        line = line.strip()

        if line.startswith("# Team:"):
            match = re.search(r"# Team:\s*<@&(\d+)>", line)
            if match:
                current_team = match.group(1)
                equipos[current_team] = {"players": [], "extra_pulls": 0}

        elif line.startswith("Players:") and current_team:
            player_ids = [int(m) for m in re.findall(r"<@!?(\d+)>", line)]
            equipos[current_team]["players"].extend(player_ids)

        elif line.startswith("Extra pulls:") and current_team:
            match = re.search(r"Extra pulls:\s*(\d+)", line)
            if match:
                equipos[current_team]["extra_pulls"] = int(match.group(1))

    return equipos

async def obtener_embed(channel_id: int, message_id: int) -> discord.Embed:

    channel = bot.get_channel(channel_id)
    if not channel:
        raise ValueError("The channel could not be found.")
    
    message = await channel.fetch_message(message_id)
    if not message:
        raise ValueError("The message could not be found.")

    embed = message.embeds[0] if message.embeds else None
    if not embed:
        raise ValueError("The message does not contain an embed.")
    
    return embed

async def modificar_extra_pulls_equipo(equipo_id: str, delta: int):
    canal = bot.get_channel(CANAL_DE_REGISTROS_ID)
    guild = canal.guild
    mensaje = await canal.fetch_message(MESSAGE_ID_REGISTRO_DURO)
    embed_original = mensaje.embeds[0]

    equipos = parse_embed_description(embed_original)

    if equipo_id not in equipos:
        raise ValueError("❌ The team was not found in the registry.")

    equipos[equipo_id]["extra_pulls"] += delta
    equipos[equipo_id]["extra_pulls"] = max(0, equipos[equipo_id]["extra_pulls"])  # No permitir valores negativos

    nuevas_lineas = []
    for eid, info in equipos.items():
        nuevas_lineas.append(f"# Team: <@&{eid}>")
        jugadores_str = " ".join(f"<@{pid}>" for pid in info["players"])
        nuevas_lineas.append(f"Players: {jugadores_str}")
        nuevas_lineas.append(f"Extra pulls: {info['extra_pulls']}")


    nueva_descripcion = "\n".join(nuevas_lineas).strip()

    nuevo_embed = embed_original.copy()
    nuevo_embed.description = nueva_descripcion
    
    for team_id, info in equipos.items():
        role = guild.get_role(int(team_id))
        role_name = role.name if role else "❓Rol no encontrado"
        print(f"Equipo: {role_name} - ID: {team_id}")

        nombres_jugadores = []
        for pid in info['players']:
            miembro = guild.get_member(pid)
            if miembro:
                nombres_jugadores.append(f"{miembro.display_name} ({pid})")
            else:
                try:
                    user = await bot.fetch_user(pid)
                    nombres_jugadores.append(f"{user.name}, ")
                except:
                    nombres_jugadores.append(f"❓Desconocido ({pid})")

        print(f"  Jugadores: {nombres_jugadores}")
        print(f"  Extra pulls: {info['extra_pulls']}")

    await mensaje.edit(embed=nuevo_embed)

async def obtener_extra_pulls_actualizados(equipo_id: str) -> int:
    canal = bot.get_channel(CANAL_DE_REGISTROS_ID)
    mensaje = await canal.fetch_message(MESSAGE_ID_REGISTRO_DURO)
    embed = mensaje.embeds[0]

    equipos = parse_embed_description(embed)

    if equipo_id not in equipos:
        raise ValueError("❌ The team was not found in the registry.")

    return equipos[equipo_id]["extra_pulls"]

async def verificar_extra_pulls(interaction: discord.Interaction, equipo_id: str | None) -> bool:
    """
    Verifica si el equipo tiene extra pulls disponibles.
    Devuelve True si NO puede continuar (por falta de pulls).
    """
    if equipo_id is None:
        await interaction.followup.send("❌ Your team could not be determined.", ephemeral=False)
        return True

    canal = bot.get_channel(CANAL_DE_REGISTROS_ID)
    mensaje = await canal.fetch_message(MESSAGE_ID_REGISTRO_DURO)
    embed = mensaje.embeds[0]
    equipos = parse_embed_description(embed)

    if equipo_id not in equipos:
        await interaction.followup.send("❌ Your team is not registered.", ephemeral=False)
        return True

    extra_pulls = equipos[equipo_id]["extra_pulls"]
    if extra_pulls <= 0:
        await interaction.followup.send(f"❌ Your team <@&{equipo_id}> has no extra pulls available.", ephemeral=False)
        return True

    return False