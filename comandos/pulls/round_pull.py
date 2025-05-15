import discord
from utils.bot_instance import bot
import time
from comandos.pulls import random_algorithm as RA
from comandos.pulls import embed_utilites as EU
from comandos.pulls import cooldown as C
from comandos.registers import register_utilities as RU
import tareas.task_copiar_registro_duro as TCRD
from comandos.pulls.constantes_pull import(
    equipos_en_uso,
    emote_name,
    gif_url_genshin,
)
from utils.claves import( 
    server_id as guild_id,
    CANAL_DE_REGISTROS_ID , 
    MESSAGE_ID_REGISTRO_DURO , 
)

@bot.tree.command(guild=discord.Object(id=guild_id), name="round_pull", description="10 random weapons")
async def round_pull(interaction: discord.Interaction):
    await interaction.response.defer()

    embed = await RU.obtener_embed(CANAL_DE_REGISTROS_ID, MESSAGE_ID_REGISTRO_DURO)
    parsed_embed = RU.parse_embed_description(embed)

    user_id = interaction.user.id
    equipo_usuario = None
    for team_id, info in parsed_embed.items():
        if user_id in info["players"]:
            equipo_usuario = team_id
            break

    if equipo_usuario is None:
        await interaction.followup.send("❌ You are not registered on any team.", ephemeral=False)
        return

    if equipo_usuario in equipos_en_uso:
        await interaction.followup.send("⏳ You're already using this command. Wait for it to finish.", ephemeral=False)
        return

    en_cooldown = await C.verificar_cooldown(interaction, equipo_usuario)
    if en_cooldown:
        return

    equipos_en_uso.add(equipo_usuario)

    mensaje = (
                ">>> **Generating weapons...** This may take a few seconds.\n"
                f"Please don't use the command again in the meantime. [{emote_name}]({gif_url_genshin})\n"
            )
    await interaction.followup.send(content=mensaje)

    armas_seleccionadas = RA.seleccionar_armas()

    lock = await RU.get_guild_lock(interaction.guild.id)

    async with lock:
        try:
        
            await RU.modificar_extra_pulls_equipo(equipo_usuario, delta=1)
            extra_pulls = await RU.obtener_extra_pulls_actualizados(equipo_usuario)

            embed, file = await EU.generar_collage_y_embed(
                armas_seleccionadas, discord.Colour.blue(), equipo_usuario, extra_pulls
            )

            await interaction.followup.send(embed=embed, file=file)
            C.ultimo_pull[equipo_usuario] = time.time()  # Aplicar cooldown al final

        except Exception as e:
            await interaction.followup.send(
                "⚠️ An error occurred while generating weapons. Please try again later.",
                ephemeral=False
            )
            print(f"Error en round_pull: {e}")

        finally:
            equipos_en_uso.discard(equipo_usuario)
    
    await TCRD.sincronizar_registro()
