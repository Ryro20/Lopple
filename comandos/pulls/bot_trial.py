import discord
from utils.bot_instance import bot
from utils.claves import server_id as guild_id
from comandos.pulls import random_algorithm as RA
from comandos.pulls import embed_utilites as EU
from comandos.pulls.constantes_pull import(
    emote_name,
    gif_url_genshin,
)

@bot.tree.command(guild=discord.Object(id=guild_id), name="test_pull", description="10 random weapons (no limits)")
async def test_pull(interaction: discord.Interaction):
    await interaction.response.defer()

    mensaje = (
                ">>> **Generating weapons...** This may take a few seconds.\n"
                f"Please don't use the command again in the meantime. [{emote_name}]({gif_url_genshin})\n"
            )
    await interaction.followup.send(content=mensaje)

    armas_seleccionadas = RA.seleccionar_armas()

    try:
        embed, file = await EU.generar_collage_y_embed(
            armas_seleccionadas,
            embed_color=discord.Colour.purple(),
            equipo_id=interaction.user.id,
            extra_pulls=None,  
            test_mode=True
        )

        await interaction.followup.send(embed=embed, file=file)

    except Exception as e:
        await interaction.followup.send("⚠️ Error generating weapons.", ephemeral=False)
        print(f"[test_pull] Error: {e}")
