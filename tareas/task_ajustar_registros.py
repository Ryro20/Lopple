import discord
from discord.ext import tasks
from utils.bot_instance import bot
import re
from utils.claves import(
    CANAL_DE_REGISTROS_ID,
    MESSAGE_ID_REGISTRO_DURO,
    MESSAGE_ID_REGISTRO_EDITABLE,
    server_id as guild_id,
    CATEGORY_ID,
)
from comandos.registers import register_utilities as RU

@tasks.loop(minutes=5)
async def llamar_sincronizacion():
    await sync_team_registers()


async def sync_team_registers():
    lock = await RU.get_guild_lock(guild_id)
    async with lock:
        try:
            canal = await bot.fetch_channel(CANAL_DE_REGISTROS_ID)
            msg_editable = await canal.fetch_message(MESSAGE_ID_REGISTRO_EDITABLE)
            msg_duro = await canal.fetch_message(MESSAGE_ID_REGISTRO_DURO)

            original_description = msg_duro.embeds[0].description or ""
            guild = msg_editable.guild

            equipos_editable = parse_embed(msg_editable.embeds[0], guild, incluir_extra_pulls=False)
            equipos_duro = parse_embed(msg_duro.embeds[0], guild, incluir_extra_pulls=True)

            if msg_duro.embeds[0].description is None:
                msg_duro.embeds[0].description = ""

            for nombre, jugadores in equipos_editable.items():
                rol = discord.utils.get(guild.roles, name=nombre)
                if not rol:
                    rol = await RU.create_team_role(guild, nombre)
                    print(f"✅ Rol creado: {rol.name}")

                    jugadores_objs = []
                    for uid in jugadores:
                        try:
                            member = await guild.fetch_member(uid)
                            jugadores_objs.append(member)
                        except discord.NotFound:
                            continue

                    await RU.assign_players_to_role(guild, jugadores_objs, rol)
                    await RU.create_team_channel(guild, nombre, rol, jugadores_objs)

                    for member in jugadores_objs:
                        print(f"🎯 Rol {rol.name} asignado a: {member.display_name}")

                canal_equipo = discord.utils.get(
                    guild.text_channels,
                    name=nombre.lower().replace(" ", "-"),
                    category_id=CATEGORY_ID
                )

                if canal_equipo is None:
                    try:
                        await RU.create_team_channel(guild, nombre, rol)
                        print(f"✅ Canal creado para equipo existente: {nombre}")
                    except Exception as e:
                        print(f"🚨 Error al crear canal para {nombre}: {e}")

                if nombre not in equipos_duro:
                    msg_duro.embeds[0].description += (
                        f"\n# Team: <@&{rol.id}>\n"
                        f"Players: {', '.join(f'<@{uid}>' for uid in jugadores)}\n"
                        f"Extra pulls: 0"
                    )
                    equipos_duro[nombre] = jugadores
                    print(f"🆕 Nuevo bloque añadido en el registro duro: {nombre}")
                else:
                    actualizar_bloque_equipo(msg_duro, rol.id, jugadores)

                # Asegurar que el jugador no esté en otro equipo
                for uid in jugadores:
                    for otro_equipo, otros_jugadores in equipos_duro.items():
                        if otro_equipo == nombre:
                            continue
                        if uid in otros_jugadores:
                            otro_rol = discord.utils.get(guild.roles, name=otro_equipo)
                            try:
                                miembro = await guild.fetch_member(uid)
                                if miembro and otro_rol in miembro.roles:
                                    await miembro.remove_roles(otro_rol)
                                    print(f"🚫 {miembro.display_name} removido de rol {otro_rol.name} (asignado a {nombre})")
                            except discord.NotFound:
                                continue


                await procesar_rol_equipo(guild, rol, jugadores, equipos_duro.get(nombre, []))
                equipos_duro[nombre] = jugadores 

            bloques_eliminados = set()
            for nombre in list(equipos_duro.keys()):
                if nombre not in equipos_editable and nombre not in bloques_eliminados:
                    rol = discord.utils.get(guild.roles, name=nombre)
                    rol_id = rol.id if rol else None
                    if rol:

                        canal = discord.utils.get(
                            guild.text_channels,
                            name=rol.name.lower().replace(" ", "-"),
                            category_id=CATEGORY_ID
                        )

                        if canal:
                            try:
                                await canal.delete()
                                print(f"🗑️ Canal eliminado: {canal.name}")
                            except discord.Forbidden:
                                print(f"🚫 No tengo permisos para eliminar el canal: {canal.name}")
                            except discord.NotFound:
                                print(f"🚫 No se encontró el canal: {canal.name}")
                            except discord.HTTPException as e:
                                print(f"🚨 Error al intentar eliminar el canal {canal.name}: {e}")

                        await rol.delete()
                        print(f"🗑️ Rol eliminado: {rol.name}")

                    if rol_id:
                        msg_duro.embeds[0].description = eliminar_bloque_por_id(
                            msg_duro.embeds[0].description,
                            rol_id
                        )
                        print(f"❌ Bloque eliminado del registro duro: {nombre}")

            msg_duro.embeds[0].description = RU.limpiar_desc(msg_duro.embeds[0].description)

            if msg_duro.embeds[0].description != original_description:
                await msg_duro.edit(embed=msg_duro.embeds[0])
                print("📝 Registro duro actualizado.")

        except Exception as e:
            print(f"🚨 Error en sync_team_registers: {e}")


@llamar_sincronizacion.before_loop
async def before_sync():
    await bot.wait_until_ready()

def parse_embed(embed, guild, incluir_extra_pulls=True):
    equipos = {}
    if not embed or not embed.description:
        return equipos
    lines = embed.description.splitlines()
    current_team = None
    role_id_actual = None

    for line in lines:
        line_strip = line.strip()
        if line_strip.startswith("# Team:"):
            raw = line_strip.split(":", 1)[1].strip()
            mention_match = re.match(r"<@&(\d+)>", raw)
            if mention_match:
                role_id_actual = int(mention_match.group(1))
                role = discord.utils.get(guild.roles, id=role_id_actual)
                current_team = role.name if role else f"RolDesconocido_{role_id_actual}"
            else:
                current_team = raw

        elif line_strip.startswith("Players:") and current_team is not None:
            ids = re.findall(r"<@!?(\d+)>", line_strip)
            equipos[current_team] = [int(uid) for uid in ids]
        elif incluir_extra_pulls and line_strip.startswith("Extra pulls:"):
            continue

    return equipos

def actualizar_bloque_equipo(msg_duro, rol_id, nuevos_jugadores):
    description = msg_duro.embeds[0].description
    block_start = description.find(f"# Team: <@&{rol_id}>")
    if block_start == -1:
        return

    block_end = description.find("# Team:", block_start + 1)
    if block_end == -1:
        block_end = len(description)

    team_block = description[block_start:block_end]

    match = re.search(r"Players: (.+?)\n", team_block)
    if not match:
        return

    jugadores_actuales = re.findall(r"<@!?(\d+)>", match.group(1))
    jugadores_actuales_set = set(jugadores_actuales)
    nuevos_set = set(str(uid) for uid in nuevos_jugadores)

    if jugadores_actuales_set == nuevos_set:
        return

    nuevos_str = ', '.join(f"<@{uid}>" for uid in nuevos_jugadores)
    nuevo_bloque = team_block.replace(match.group(0), f"Players: {nuevos_str}\n")

    msg_duro.embeds[0].description = description[:block_start] + nuevo_bloque + description[block_end:]
    print(f"🔄 Jugadores actualizados para <@&{rol_id}>")


def eliminar_bloque(texto, nombre_equipo, guild):
    bloques = re.split(r"(?=# Team: <@&\d+>)", texto)
    nuevos_bloques = []

    for bloque in bloques:
        if not bloque.strip():
            continue

        match = re.match(r"# Team: <@&(\d+)>", bloque.strip())
        if not match:
            nuevos_bloques.append(bloque)
            continue

        role_id = int(match.group(1))
        rol = discord.utils.get(guild.roles, id=role_id)

        print(f"Buscando rol con ID {role_id} y nombre {nombre_equipo}")
        nombre_rol = rol.name if rol else f"Rol desconocido ({role_id})"

        if nombre_equipo != nombre_rol:
            nuevos_bloques.append(bloque)
        else:
            print(f"❌ Eliminando bloque para {nombre_equipo}")

    return '\n'.join(b.strip() for b in nuevos_bloques if b.strip())


async def procesar_rol_equipo(guild, rol, nuevos_jugadores, antiguos_jugadores):
    nuevos_set = set(nuevos_jugadores)
    antiguos_set = set(antiguos_jugadores)

    eliminados = antiguos_set - nuevos_set
    añadidos = nuevos_set - antiguos_set

    for uid in eliminados:
        try:
            member = await guild.fetch_member(uid)
            if member and rol in member.roles:
                await member.remove_roles(rol)
                print(f"❌ Rol {rol.name} retirado a: {member.display_name}")
        except discord.NotFound:
            continue

    for uid in añadidos:
        try:
            member = await guild.fetch_member(uid)
            if member and rol not in member.roles:
                await member.add_roles(rol)
                print(f"✅ Rol {rol.name} asignado a: {member.display_name}")
        except discord.NotFound:
            continue

def eliminar_bloque_por_id(texto, rol_id):
    bloques = re.split(r"(?=# Team: <@&\d+>)", texto)
    nuevos_bloques = []

    for bloque in bloques:
        if not bloque.strip():
            continue

        match = re.match(r"# Team: <@&(\d+)>", bloque.strip())
        if match and int(match.group(1)) == rol_id:
            print(f"🧹 Eliminando bloque con rol ID {rol_id}")
            continue

        nuevos_bloques.append(bloque)

    return '\n'.join(b.strip() for b in nuevos_bloques if b.strip())
