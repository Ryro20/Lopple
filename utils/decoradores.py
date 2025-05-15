import discord
from discord import app_commands
from discord.app_commands import CheckFailure
from discord import Interaction
from utils.claves import ROL_ID_PERMITIDO

def tiene_rol_permitido():
    async def predicate(interaction: Interaction):
        # Verificar si el usuario tiene el rol permitido
        if any(role.id == ROL_ID_PERMITIDO for role in interaction.user.roles):
            return True
        raise CheckFailure("You do not have permission to use this command.")
    
    return predicate
