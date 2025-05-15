import discord
from utils.bot_instance import bot
import comandos.pulls.random_algorithm as RA
import comandos.registers.register_utilities as RU
import comandos.pulls.embed_utilites as EU
import tareas.task_copiar_registro_duro as TCRD
from utils.claves import (
    server_id as guild_id,
    CANAL_DE_REGISTROS_ID,
    MESSAGE_ID_REGISTRO_DURO,
)
from comandos.pulls.constantes_pull import (
    emote_name,
    gif_url_honkai
)

@bot.tree.command(guild=discord.Object(id=guild_id), description="10 random weapons")
async def extra_pull(interaction: discord.Interaction):
    await interaction.response.defer()

    lock = await RU.get_guild_lock(interaction.guild.id)

    async with lock:

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

        if await RU.verificar_extra_pulls(interaction, equipo_usuario):
            return

        try:

            mensaje = (
                ">>> **Generating weapons...** This may take a few seconds.\n"
                f"Please don't use the command again in the meantime. [{emote_name}]({gif_url_honkai})\n"
            )

            await interaction.followup.send(content=mensaje)

            armas_seleccionadas = RA.seleccionar_armas()
            await RU.modificar_extra_pulls_equipo(equipo_usuario, delta=-1)  # resta 1
            extra_pulls = await RU.obtener_extra_pulls_actualizados(equipo_usuario)
            embed, file = await EU.generar_collage_y_embed(armas_seleccionadas, discord.Colour.orange(), equipo_usuario, extra_pulls)

            await interaction.followup.send(embed=embed, file=file)
            

        except Exception as e:
            await interaction.followup.send(
                "⚠️ An error occurred while generating weapons. Please try again later.",
                ephemeral=False
            )
            print(f"Error en round_pull: {e}")
    
    await TCRD.sincronizar_registro()



