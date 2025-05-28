import discord
import aiohttp
import io
import re
from PIL import Image, ImageDraw , ImageFilter , ImageFont
from utils.bot_instance import bot
from utils.claves import (
    server_id as guild_id,
    CANAL_DE_REGISTROS_ID,
    MESSAGE_ID_REGISTRO_DURO,
    MESSAGE_ID_REGISTRO_EDITABLE,
)
from comandos.registers import register_utilities as RU
import tareas.task_ajustar_registros as TAR
import tareas.task_copiar_registro_duro as TCRD

async def handle_register_team(interaction, team_name: str, players: list[discord.User]):

    if len(players) < 1 or len(players) > 6:
        raise ValueError("A team must have between 1 and 6 players.")

    rol = await RU.create_team_role(interaction.guild, team_name)

    jugadores_objs = await RU.assign_players_to_role(interaction.guild, players, rol)
    await RU.create_team_channel(interaction.guild, team_name, rol, jugadores_objs)
    collage_buffer = await create_collage(players)

    return [m.mention for m in jugadores_objs], collage_buffer, rol


async def make_circle_avatar(avatar_bytes, size=128, blur_radius=2, margin=2):
    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar = avatar.resize((size, size))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((margin, margin, size - margin, size - margin), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(avatar, (0, 0), mask)
    return result

async def create_collage(users):
    size, padding, font_size = 128, 10, 16

    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    avatar_images = []
    async with aiohttp.ClientSession() as session:
        for user in users:
            async with session.get(user.display_avatar.url) as resp:
                if resp.status == 200:
                    avatar = await make_circle_avatar(await resp.read(), size)
                    avatar_images.append((avatar, user.display_name))

    count = len(avatar_images)

    cols = min(3, count) if count != 4 else 2

    rows = (count + cols - 1) // cols

    width = cols * (size + padding) - padding
    height = rows * (size + font_size + padding + 8)

    collage = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(collage)

    for idx, (img, name) in enumerate(avatar_images):
        row = idx // cols
        col = idx % cols

        items_in_this_row = (
            count % cols if row == rows - 1 and count % cols != 0 else cols
        )
        row_offset = ((cols - items_in_this_row) * (size + padding)) // 2

        x = col * (size + padding) + row_offset
        y = row * (size + font_size + padding + 8)

        collage.paste(img, (x, y), img)
        text_width = font.getlength(name) if hasattr(font, "getlength") else draw.textlength(name, font=font)
        draw.text((x + (size - text_width) // 2, y + size + 4), name, fill="#FF007A", font=font)

    buf = io.BytesIO()
    collage.save(buf, format="PNG")
    buf.seek(0)
    return buf


@bot.tree.command(
    guild=discord.Object(id=guild_id),
    description="Register the team to be able to use /round_pull and /extra_pull"
)
async def register_team(
    interaction: discord.Interaction,
    team_name: str,
    captain: discord.User,
    player_1: discord.User = None,
    player_2: discord.User = None,
    player_3: discord.User = None,
    player_4: discord.User = None,
    player_5: discord.User = None
    ):

    await interaction.response.defer()

    if not re.fullmatch(r"[A-Za-z0-9 \-]+", team_name):
        return await interaction.followup.send(
            "The team name may only contain letters, numbers, spaces, and hyphens.",
            ephemeral=False
        )

    guild = interaction.guild

    players = list(filter(None, [captain, player_1, player_2, player_3, player_4, player_5]))

    if len(players) != len(set(p.id for p in players)):
        return await interaction.followup.send("You cannot repeat players on the same team.",  ephemeral=False)

    all_ids = {p.id for p in players}

    if not guild.me.guild_permissions.manage_roles:
        raise PermissionError("I do not have permissions to create or assign roles.")
    
    lock = await RU.get_guild_lock(interaction.guild.id)
    async with lock:

        channel = await bot.fetch_channel(CANAL_DE_REGISTROS_ID)
        try:
            message_duro = await channel.fetch_message(MESSAGE_ID_REGISTRO_DURO)
            message_editable = await channel.fetch_message(MESSAGE_ID_REGISTRO_EDITABLE)
        except discord.NotFound:
            return await interaction.followup.send("One of the embed messages was not found.", ephemeral=False)

        embed_duro = message_duro.embeds[0]
        embed_editable = message_editable.embeds[0]

        existing_description = embed_duro.description or "__ __"
        editable_description = embed_editable.description or "__ __"

        # Verificar duplicados en registro duro
        if f"Team: {team_name}" in existing_description:
            return await interaction.followup.send(f"There is already a team called  '{team_name}'.", ephemeral=False)

        for user_id in all_ids:
            match = re.search(rf"Team: (.+?)\nPlayers:.*<@{user_id}>", existing_description)
            if match:
                nombre_equipo = match.group(1)
                role = discord.utils.get(guild.roles, name=nombre_equipo)
                mention = role.mention if role else f"**{nombre_equipo}**"
                return await interaction.followup.send(
                    f"<@{user_id}> is already registered with the {mention} team.",
                    ephemeral=False
                )

        try:
            mentions, collage_buffer, role = await handle_register_team(interaction, team_name, players)
        except (PermissionError, ValueError) as e:
            return await interaction.followup.send(str(e), ephemeral=False)

        nuevo_bloque_editable = (
            f"\n# Team: {role.name}\n"
            f"Players: {', '.join(mentions)}\n"
        )

        embed_editable.description = RU.limpiar_desc(editable_description) + nuevo_bloque_editable

        await message_editable.edit(embed=embed_editable)

        file = discord.File(collage_buffer, filename="team_collage.png")
        response_embed = discord.Embed(
            title=f"Registered {team_name} team",
            color=discord.Color.blue()
        )

        response_embed.add_field(name="Team Members:",value=" ", inline=True)

        response_embed.set_image(url="attachment://team_collage.png")

        await interaction.followup.send(embed=response_embed, file=file)
    
    await TAR.sync_team_registers()
    await TCRD.sincronizar_registro()