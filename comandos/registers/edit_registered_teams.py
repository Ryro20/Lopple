import discord
from discord import app_commands
from utils.bot_instance import bot
from utils.decoradores import tiene_rol_permitido
from utils.claves import (
    server_id as guild_id,
    MESSAGE_ID_REGISTRO_EDITABLE as mensaje_a_editar,
    CANAL_DE_REGISTROS_ID                     
)
import tareas.task_ajustar_registros as TAR
import tareas.task_copiar_registro_duro as TCRD

class EditModal(discord.ui.Modal, title="Edit Registry"):
    def __init__(self, current_content):
        super().__init__()
        self.contenido = discord.ui.TextInput(
            label="New content",
            style=discord.TextStyle.paragraph,
            default=current_content,
            max_length=2000
        )
        self.add_item(self.contenido)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel = await bot.fetch_channel(CANAL_DE_REGISTROS_ID)
            message = await channel.fetch_message(mensaje_a_editar)
            old_embed = message.embeds[0] if message.embeds else discord.Embed(title="Equipo registrado")

            new_embed = discord.Embed(
                title=old_embed.title,
                description=self.contenido.value,
                color=discord.Color.orange()
            )

            await message.edit(embed=new_embed)
            await interaction.response.send_message("Updated message.", ephemeral=True)

        except discord.NotFound:
            await interaction.response.send_message("Message not found.", ephemeral=True)

@bot.tree.command(guild=discord.Object(id=guild_id), name="edit_registered_teams", description="(Admin Only) Edit the main message of registered teams")
@app_commands.check(tiene_rol_permitido())
async def edit_registered_teams(interaction: discord.Interaction):
    
    try:
        channel = await bot.fetch_channel(CANAL_DE_REGISTROS_ID)
        message = await channel.fetch_message(mensaje_a_editar)
    except discord.NotFound:
        return await interaction.response.send_message("No message found to edit.", ephemeral=True)

    # Tomar la descripción del primer embed
    current_description = message.embeds[0].description if message.embeds else ""
    await interaction.response.send_modal(EditModal(current_description))
    await TAR.sync_team_registers()
    await TCRD.sincronizar_registro()

'''
@bot.tree.command(guild=discord.Object(id=guild_id), name="send_editable_message", description="Envía el mensaje editable (solo una vez)")
async def send_editable_message(interaction: discord.Interaction):
    embed = discord.Embed(title="Registro Editable", description="Aquí se mostrarán los jugadores.")
    message = await interaction.channel.send(embed=embed)
    await interaction.response.send_message(f"Mensaje enviado con ID: `{message.id}`", ephemeral=True)
'''
