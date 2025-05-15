import discord
from utils.bot_instance import bot
import math
import requests
import asyncio
import random
from io import BytesIO
from PIL import Image
from utils.claves import(
    GITHUB_TOKEN,
    API_BASE_URL,
    url_repository,
    server_id as guild_id,
    bot_version,
    url_avatar
)
from comandos.pulls.constantes_pull import(
    max_pages,
    index_exclude,
    five_percentage_drop,
    twenty_five_percentage_drop,
    seventy_percentage_drop,
    gold_star,
    purple_star,
    blue_star,
    cuantity_weapons,
    max_length,
    mensajes_suerte_mala,
    mensajes_suerte_regular,
    mensajes_suerte_buena,
    mensajes_suerte_épica,
    mensajes_suerte_legendaria,
)

def calcular_columnas_dinamicas(num_items):

    mejor_filas = 1
    mejor_columnas = num_items

    for filas in range(1, int(math.sqrt(num_items)) + 1):
        if num_items % filas == 0:
            columnas = num_items // filas
            if abs(filas - columnas) < abs(mejor_filas - mejor_columnas):
                mejor_filas = filas
                mejor_columnas = columnas

    return mejor_columnas, mejor_filas

def obtener_arma_info(armas_seleccionadas):
    armas_info = []
    page = 1

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    encontrados = set()

    while page <= max_pages:
        api_url = f"{API_BASE_URL}?per_page=100&page={page}"
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        for entry in data:
            filename = entry["name"]
            if not filename.endswith(".png"):
                continue

            sin_extension = filename[:-4]

            if "_" not in sin_extension:
                continue

            id_str, nombre = sin_extension.split("_", 1)

            try:
                index = int(id_str)
            except ValueError:
                continue

            nombre = nombre.replace("%20", " ")

            if index in armas_seleccionadas and index not in index_exclude and index not in encontrados:
                raw_url = url_repository.replace("github.com", "raw.githubusercontent.com").replace("/blob", "") + f"/{filename}"
                armas_info.append({'index': index, 'name': nombre, 'url': raw_url})
                encontrados.add(index)
                print(f"✅ Arma encontrada: {index} - {nombre} - {raw_url}")

        if len(encontrados) == len(armas_seleccionadas):
            break

        page += 1

    print(f"🧪 Se encontraron {len(armas_info)} armas de {len(armas_seleccionadas)} solicitadas")

    if len(armas_info) != len(armas_seleccionadas):
        print(f"❌ Faltan armas: {set(armas_seleccionadas) - encontrados}")
        raise Exception("Not all selected weapons could be found in the repository")

    return armas_info

def obtener_rareza(index):
    if index in five_percentage_drop:
        return gold_star
    elif index in twenty_five_percentage_drop:
        return purple_star
    elif index in seventy_percentage_drop:
        return blue_star
    else:
        return "❓ Unknown"

def crear_collage(armas_info):

    columnas, filas =calcular_columnas_dinamicas(len(armas_info))
    imagenes = []

    primera_url = armas_info[0]['url']
    response = requests.get(primera_url)
    if response.status_code != 200 or not response.headers['Content-Type'].startswith('image/'):
        raise Exception(f"Invalid URL or no image: {primera_url} - Status: {response.status_code}")

    base_img = Image.open(BytesIO(response.content)).convert("RGBA")
    cell_w, cell_h = base_img.size

    estrellas_cache = {}
    estrella_archivos = {
        'gold': "GoldStar.png",
        'purple': "PurpleStar.png",
        'blue': "BlueStar.png"
    }

    for clave, nombre_archivo in estrella_archivos.items():
        star_url = url_repository.replace("github.com", "raw.githubusercontent.com").replace("/blob", "") + f"/{nombre_archivo}"
        print(f"Descargando estrella {clave} desde: {star_url}")
        response = requests.get(star_url)
        if response.status_code != 200 or not response.headers['Content-Type'].startswith('image/'):
            raise Exception(f"Invalid star or no image: {star_url} - Status: {response.status_code}")
        
        star_img = Image.open(BytesIO(response.content)).convert("RGBA")
        factor = 4
        new_w = cell_w // factor
        new_h = int(star_img.height * (new_w / star_img.width))
        star_img = star_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        estrellas_cache[clave] = star_img

    for arma in armas_info:
        weapon_img = Image.open(BytesIO(requests.get(arma['url']).content)).convert("RGBA")

        if arma['index'] in five_percentage_drop:
            star_img = estrellas_cache['gold']
        elif arma['index'] in twenty_five_percentage_drop:
            star_img = estrellas_cache['purple']
        else:
            star_img = estrellas_cache['blue']

        weapon_img.paste(star_img, (5, 5), star_img)
        imagenes.append(weapon_img)

    collage = Image.new('RGBA', (columnas * cell_w, filas * cell_h))
    for i, img in enumerate(imagenes):
        x = (i % columnas) * cell_w
        y = (i // columnas) * cell_h
        collage.paste(img, (x, y))

    buffer = BytesIO()
    collage.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def crear_embed_armas(armas_info, embed_color, equipo_id, extra_pulls, test_mode=False):
    
    if test_mode:
        equipo_mention = "Test Mode"
    else:
        rol_equipo = discord.utils.get(bot.get_guild(guild_id).roles, id=int(equipo_id))
        
        if not rol_equipo:
            raise ValueError(f"Role not found for team with ID {equipo_id}")
        
        equipo_mention = rol_equipo.mention  
    
    if len(armas_info) != cuantity_weapons:
        raise ValueError(f"Se esperaban exactamente {cuantity_weapons} armas.")

    columna_izquierda = armas_info[:cuantity_weapons//2]
    columna_derecha = armas_info[cuantity_weapons//2:]

    texto_izquierda = "\n".join([f"**{obtener_rareza(arma['index'])}** {arma['name']}" for arma in columna_izquierda])
    texto_derecha = "\n".join([f"**{obtener_rareza(arma['index'])}** {arma['name']}" for arma in columna_derecha])

    if len(texto_izquierda) > max_length:
        texto_izquierda = ""

    if len(texto_derecha) > max_length:
        texto_derecha = ""

    texto_izquierda += f"\n\n**Extra Pulls**\n**{extra_pulls}** available"
    texto_derecha += f"\n\n**Drop Chances**\n{blue_star} 70%{purple_star} 25%{gold_star} 5%"

    embed = discord.Embed(
        description=f"# Here's your weapons {equipo_mention}",  # Aquí se usa equipo_mention, no rol_equipo.mention
        color=embed_color,
    )

    embed.add_field(name="", value=texto_izquierda, inline=True)
    embed.add_field(name="", value=texto_derecha, inline=True)

    num_tres_estrellas = sum(1 for arma in armas_info if obtener_rareza(arma['index']) == gold_star)
    num_dos_estrellas = sum(1 for arma in armas_info if obtener_rareza(arma['index']) == purple_star)

    if num_tres_estrellas >= 3:
        mensaje_footer = random.choice(mensajes_suerte_épica)
    elif num_tres_estrellas == 2:
        mensaje_footer = random.choice(mensajes_suerte_legendaria)
    elif num_tres_estrellas == 1:
        mensaje_footer = random.choice(mensajes_suerte_buena)
    elif num_dos_estrellas >= 3:
        mensaje_footer = random.choice(mensajes_suerte_regular)
    else:
        mensaje_footer = random.choice(mensajes_suerte_mala)

    embed.set_footer(
        text=f"Version {bot_version} || {mensaje_footer} ",
        icon_url=url_avatar
    )

    return embed


async def generar_collage_y_embed(armas_seleccionadas, embed_color, equipo_id, extra_pulls, test_mode=False):
    armas_info = await asyncio.to_thread(obtener_arma_info, armas_seleccionadas)
    random.shuffle(armas_info)

    embed = crear_embed_armas(armas_info, embed_color, equipo_id, extra_pulls , test_mode)

    imagen_urls = [arma['url'] for arma in armas_info]
    collage_buffer = await asyncio.to_thread(crear_collage, armas_info)
    file = discord.File(collage_buffer, filename="collage.png")
    embed.set_image(url="attachment://collage.png")

    return embed, file