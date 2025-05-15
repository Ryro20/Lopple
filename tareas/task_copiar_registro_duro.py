import discord
from discord.ext import tasks
from utils.bot_instance import bot
from utils.claves import (
    CANAL_DE_REGISTROS_ID,
    MESSAGE_ID_REGISTRO_DURO,
    CANAL_DE_REGISTROS_INFORMATIVO_ID,
    MESSAGE_ID_REGISTRO_INFORMATIVO,
    bot_version,
    url_avatar,
    server_id as guild_id
)
from comandos.registers import register_utilities as RU


def crear_embed_registro_informativo(descripcion: str) -> discord.Embed:
    embed = discord.Embed(
        title="Registered Teams",
        description=descripcion,
        color=discord.Color(int("0xFF007A", 16))
    )
    embed.set_footer(text=f"Version {bot_version}", icon_url=url_avatar)
    return embed


@tasks.loop(seconds=60)
async def llamar_copiado():
    await sincronizar_registro()

async def sincronizar_registro():
    await bot.wait_until_ready()

    lock = await RU.get_guild_lock(guild_id)
    async with lock:
        try:
            canal_duro = await bot.fetch_channel(CANAL_DE_REGISTROS_ID)
            canal_info = await bot.fetch_channel(CANAL_DE_REGISTROS_INFORMATIVO_ID)

            msg_duro = await canal_duro.fetch_message(MESSAGE_ID_REGISTRO_DURO)
            contenido_duro = (msg_duro.embeds[0].description or "").strip()

            if not contenido_duro:
                contenido_duro = "There are no registered teams"

            try:
                msg_info = await canal_info.fetch_message(MESSAGE_ID_REGISTRO_INFORMATIVO)
            except discord.NotFound:
                msg_info = None

            if msg_info:
                embed_info = msg_info.embeds[0] if msg_info.embeds else None
                contenido_info = (embed_info.description or "").strip() if embed_info else ""

                if contenido_duro != contenido_info:
                    nuevo_embed = crear_embed_registro_informativo(contenido_duro)
                    await msg_info.edit(embed=nuevo_embed)
                    print("🟢 Registro informativo actualizado.")
            else:
                nuevo_embed = crear_embed_registro_informativo(contenido_duro)
                await canal_info.send(embed=nuevo_embed)
                print("🆕 Registro informativo creado.")

        except Exception as e:
            print(f"🚨 Error en sincronizar_registro: {e}")


@llamar_copiado.before_loop
async def before_sync():
    await bot.wait_until_ready()
