import discord
from utils.bot_instance import bot
from discord import app_commands
from utils.decoradores import tiene_rol_permitido
import tareas.task_copiar_registro_duro as TCRD
import re
from utils.claves import (
    CANAL_DE_REGISTROS_ID, 
    MESSAGE_ID_REGISTRO_DURO,
    server_id as guild_id
)

@bot.tree.command(guild=discord.Object(id=guild_id), description="(Admin Only) Changes the amount of extra pulls for a team.")
@app_commands.check(tiene_rol_permitido())
@app_commands.describe(team="Team to modify", operation="Operation (add/subtract/replace/reset)", cuantity="Number of extra pulls (only if not reset)")
async def change_extrapulls(interaction: discord.Interaction, team: str, operation: str, cuantity: int = None):

    OPERACIONES_VALIDAS = {"replace", "add", "subtract", "reset"}

    if operation not in OPERACIONES_VALIDAS:
        await interaction.response.send_message("❌ The operation must be 'replace', 'add', 'subtract' or 'reset'.", ephemeral=False)
        return

    if operation == "reset" and cuantity is not None:
        await interaction.response.send_message("❌ The quantity does not need to be specified for the 'reset' operation.", ephemeral=False)
        return

    if operation != "reset" and cuantity is None:
        await interaction.response.send_message("❌ You must specify the quantity for this operation.", ephemeral=False)
        return

    await interaction.response.defer(ephemeral=False)

    canal = await bot.fetch_channel(CANAL_DE_REGISTROS_ID)
    msg_duro = await canal.fetch_message(MESSAGE_ID_REGISTRO_DURO)

    embed = msg_duro.embeds[0]
    contenido = embed.description or ""
    guild = interaction.guild

    rol = discord.utils.get(guild.roles, name=team)
    if not rol:
        await interaction.followup.send(f"❌ The role with the name **{team}** was not found.")
        return

    patron = rf"(# Team: <@&{rol.id}>\nPlayers: [^\n]+\n)Extra pulls: (\d+)"
    match = re.search(patron, contenido)

    if not match:
        await interaction.followup.send("❌ The team was not found in the registry")
        return

    cantidad_actual = int(match.group(2))

    if operation == "reset":
        cantidad_nueva = 0
    elif operation == "replace":
        cantidad_nueva = cuantity
    elif operation == "add":
        cantidad_nueva = cantidad_actual + cuantity
    elif operation == "subtract":
        cantidad_nueva = cantidad_actual - cuantity

    nuevo_bloque = rf"\1Extra pulls: {cantidad_nueva}"
    nuevo_contenido, reemplazos = re.subn(patron, nuevo_bloque, contenido)

    if reemplazos == 0:
        await interaction.followup.send("❌ The team was not found in the registry")
        return

    embed.description = nuevo_contenido
    await msg_duro.edit(embed=embed)

    if operation == "reset":
        await interaction.followup.send(f"🔄 **{team}** team's extra pulls reset to **0**.")
    else:
        await interaction.followup.send(f"✅ **{team}** team's extra pulls updated to **{cantidad_nueva}**.")

    await TCRD.sincronizar_registro()


# Autocompletado para nombres de equipos
@change_extrapulls.autocomplete("team")
async def equipo_autocomplete(interaction: discord.Interaction, current: str):
    try:
        canal = await bot.fetch_channel(CANAL_DE_REGISTROS_ID)
        msg_duro = await canal.fetch_message(MESSAGE_ID_REGISTRO_DURO)
        guild = interaction.guild

        texto = msg_duro.embeds[0].description or ""
        role_ids = re.findall(r"# Team: <@&(\d+)>", texto)

        sugerencias = []
        for rid in role_ids:
            rol = discord.utils.get(guild.roles, id=int(rid))
            if rol and current.lower() in rol.name.lower():
                sugerencias.append(app_commands.Choice(name=rol.name, value=rol.name))

        return sugerencias[:25]  # Discord permite máximo 25 opciones
    except Exception as e:
        print(f"Error en autocompletar equipos: {e}")
        return []

@change_extrapulls.autocomplete("operation")
async def operacion_autocomplete(interaction: discord.Interaction, current: str):
    try:
        opciones = ["replace", "add", "subtract", "reset"]
        resultados = [
            app_commands.Choice(name=opcion, value=opcion)
            for opcion in opciones if current.lower() in opcion.lower()
        ]
        return resultados[:25]
    
    except Exception as e:
        print(f"Error en autocompletar equipos: {e}")
        return []

@change_extrapulls.autocomplete("cuantity")
async def cantidad_autocomplete(interaction: discord.Interaction, current: str):
    try:

        if "reset" in interaction.data["options"]:
            return []  # No mostrar la cantidad si es resetear

        try:
            current_str = str(current)
        except Exception:
            current_str = ""

        opciones = [str(i) for i in range(0, 11)]  # De 0 a 10
        resultados = [
            app_commands.Choice(name=opcion, value=int(opcion))
            for opcion in opciones if current_str in opcion
        ]
        return resultados[:25]
    
    except Exception as e:
        print(f"Error en autocompletar equipos: {e}")
        return []
