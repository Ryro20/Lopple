import discord
from discord import app_commands
from utils.bot_instance import bot
from utils.claves import server_id as guild_id
from utils.decoradores import tiene_rol_permitido


@bot.tree.command(guild=discord.Object(id=guild_id), description="(Admin Only) Deletes all messages from the current channel.")
@app_commands.check(tiene_rol_permitido())
async def purgeall(interaction: discord.Interaction):
    try:

        await interaction.response.send_message("🧹 Cleaning the channel... This may take a few seconds.", ephemeral=True)

        # Elimina mensajes recientes (hasta 14 días)
        deleted = await interaction.channel.purge(limit=None)

        await interaction.followup.send(f"✅ {len(deleted)} messages were deleted from the channel.", ephemeral=True)

    except Exception as e:
        await interaction.followup.send("⚠️ An error occurred while purging the channel.", ephemeral=True)
        print(f"Error en purgeall: {e}")
