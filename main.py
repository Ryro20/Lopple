import discord
from discord.ext import commands
from comandos import (
    purge,
    delete_team_roles,
    change_extra_pulls,
)
from comandos.pulls import round_pull, extra_pull, bot_trial
from comandos.registers import register_team, edit_registered_teams, add_member_team
import tareas.task_ajustar_registros as TAR
import tareas.task_copiar_registro_duro as TCRD
from utils.bot_instance import bot
import utils.claves as claves

@bot.event
async def on_ready():
    print(f'{bot.user} ha iniciado sesión')
    await bot.change_presence(activity=discord.Game(name="ranked with Nautilus"))

    guild = discord.Object(id= claves.server_id)
    synced = await bot.tree.sync(guild = guild)
    print(f"✅ Comandos sincronizados localmente: {[cmd.name for cmd in synced]}")
    TAR.llamar_sincronizacion.start()
    TCRD.llamar_copiado.start()

@bot.command()
@commands.is_owner()
async def sync(ctx):
    guild = discord.Object(id= claves.server_id)
    synced = await bot.tree.sync(guild = guild)
    await ctx.send(f"Synced {len(synced)} command(s).")

# TOKEN DEL BOT
bot.run( claves.token_discord)
    