from discord import app_commands
import discord
from utils.bot_instance import bot
from utils.claves import (
    server_id as guild_id,
    CANAL_DE_REGISTROS_ID,
    MESSAGE_ID_REGISTRO_EDITABLE
)
from comandos.registers.register_utilities import get_guild_lock , limpiar_desc
from comandos.registers.register_team import create_collage
import tareas.task_ajustar_registros as TAR
import tareas.task_copiar_registro_duro as TCRD
import re

@bot.tree.command(
    description="Add a new member to your registered team.",
    guild=discord.Object(id=guild_id)
)
@app_commands.describe(team="Name of the team you belong to", nuevo_jugador="User you want to add")
async def add_member_team(
    interaction: discord.Interaction,
    team: str,
    nuevo_jugador: discord.User
):
    await interaction.response.defer()

    guild = interaction.guild
    miembro = interaction.user
    rol_equipo = discord.utils.get(guild.roles, name=team)

    if not rol_equipo or rol_equipo not in miembro.roles:
        return await interaction.followup.send("❌ You can only add players to your own team.", ephemeral=False)

    lock = await get_guild_lock(guild.id)

    async with lock:
        canal = await bot.fetch_channel(CANAL_DE_REGISTROS_ID)
        mensaje_editable = await canal.fetch_message(MESSAGE_ID_REGISTRO_EDITABLE)
        embed = mensaje_editable.embeds[0]
        descripcion = embed.description or ""

        # Encontrar bloque del equipo
        patron = re.compile(
            rf"""
            \#\ Team:\ {re.escape(team)}     # Encabezado del equipo exacto
            \nPlayers:\ (.+?)                # Lista de jugadores, capturada
            (\n\#\ Team:|\Z)                 # Hasta el siguiente equipo o el final del texto
            """,
            re.DOTALL | re.VERBOSE
        )
        match = patron.search(descripcion)


        if not match:
            return await interaction.followup.send("❌ Your team was not found in the registry", ephemeral=False)

        jugadores_linea = match.group(1).strip()
        jugadores_ids = re.findall(r"<@!?(\d+)>", jugadores_linea)

        # Verificar si ya está en otro equipo
        bloques = re.findall(r"# Team: (.+?)\nPlayers: (.+?)(?=\n# Team:|\Z)", descripcion, re.DOTALL)
        for nombre_equipo, jugadores_str in bloques:
            if str(nuevo_jugador.id) in re.findall(r"<@!?(\d+)>", jugadores_str):
                rol_conflictivo = discord.utils.get(guild.roles, name=nombre_equipo)
                return await interaction.followup.send(
                    f"🚫 {nuevo_jugador.mention} is already registered on another team: {rol_conflictivo.mention if rol_conflictivo else nombre_equipo}",
                    ephemeral=False
                )

        if nuevo_jugador.id in map(int, jugadores_ids):
            return await interaction.followup.send(f"⚠️ {nuevo_jugador.mention} is already on your team.", ephemeral=False)

        if len(jugadores_ids) >= 6:
            return await interaction.followup.send("🚫 Your team already has 6 registered players.", ephemeral=False)

        jugadores_ids.append(str(nuevo_jugador.id))
        jugadores_menciones = [f"<@{uid}>" for uid in jugadores_ids]

        nuevo_bloque = f"# Team: {team}\nPlayers: {', '.join(jugadores_menciones)}"

        nueva_desc = patron.sub(nuevo_bloque + r"\2", descripcion)

        embed.description = limpiar_desc(nueva_desc)
        await mensaje_editable.edit(embed=embed)

        try:
            miembro_nuevo = await guild.fetch_member(nuevo_jugador.id)
            await miembro_nuevo.add_roles(rol_equipo)
        except discord.NotFound:
            pass  # El usuario no está en el servidor

        jugadores_objs = [await guild.fetch_member(int(uid)) for uid in jugadores_ids]
        collage_buffer = await create_collage(jugadores_objs)

        file = discord.File(collage_buffer, filename="updated_collage.png")
        response_embed = discord.Embed(
            title=f"{team} - Updated Team",
            description="Player successfully added.",
            color=discord.Color.green()
        )
        response_embed.set_image(url="attachment://updated_collage.png")

        await interaction.followup.send(embed=response_embed, file=file)
        
    await TAR.sync_team_registers()
    await TCRD.sincronizar_registro()

@add_member_team.autocomplete("team")
async def obtener_equipos_autocomplete(interaction: discord.Interaction, current: str):
    canal = await bot.fetch_channel(CANAL_DE_REGISTROS_ID)
    mensaje_editable = await canal.fetch_message(MESSAGE_ID_REGISTRO_EDITABLE)
    embed = mensaje_editable.embeds[0]
    descripcion = embed.description or ""

    equipos = re.findall(r"# Team: (.+)", descripcion)
    equipos = [e for e in equipos if current.lower() in e.lower()]
    return [app_commands.Choice(name=eq, value=eq) for eq in equipos[:25]]