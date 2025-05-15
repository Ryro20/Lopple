import discord
from discord import app_commands
from utils.bot_instance import bot
from utils.decoradores import tiene_rol_permitido
from comandos.registers import register_utilities as RU
import tareas.task_ajustar_registros as TAR
from utils.claves import (
    server_id as guild_id,
    CANAL_DE_REGISTROS_ID,
    MESSAGE_ID_REGISTRO_EDITABLE,
)

@bot.tree.command(
    guild=discord.Object(id=guild_id),
    description="(Admin Only) Reset the log."
)
@app_commands.check(tiene_rol_permitido())
async def delete_registers(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    
    lock = await RU.get_guild_lock(interaction.guild.id)

    async with lock:
        try:
            canal = await bot.fetch_channel(CANAL_DE_REGISTROS_ID)
            msg_editable = await canal.fetch_message(MESSAGE_ID_REGISTRO_EDITABLE)

            embed_editable = msg_editable.embeds[0]
            embed_editable.description = "There are no registered teams"
            await msg_editable.edit(embed=embed_editable)

            await interaction.followup.send("✅ The log message has been reset.", ephemeral=False)
            print("✅ Registro editable vaciado correctamente.")
            

        except Exception as e:
            print(f"🚨 Error al vaciar registros: {e}")
            await interaction.followup.send("❌ Error emptying log message.", ephemeral=False)

    await TAR.sync_team_registers()
