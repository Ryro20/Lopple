import discord
import time
from comandos.pulls.constantes_pull import ultimo_pull, COOLDOWN_MINUTOS

def cooldown_activo(equipo_id, cooldown=60):
    ahora = time.time()
    if equipo_id not in ultimo_pull:
        return False
    return (ahora - ultimo_pull[equipo_id]) < cooldown

def obtener_tiempo_restante(equipo_id, cooldown=60):
    ahora = time.time()
    return max(0, cooldown - (ahora - ultimo_pull.get(equipo_id, 0)))

async def verificar_cooldown(interaction: discord.Interaction, equipo_id: str | None):
    if equipo_id is None:
        await interaction.followup.send("❌ Your team could not be determined.", ephemeral=False)
        return True

    rol_equipo = discord.utils.get(interaction.guild.roles, id=int(equipo_id))
    if not rol_equipo:
        await interaction.followup.send("❌ Team role not found.", ephemeral=False)
        return True

    cooldown = COOLDOWN_MINUTOS * 60

    if cooldown_activo(equipo_id, cooldown):
        tiempo_restante = obtener_tiempo_restante(equipo_id, cooldown)
        minutos = int(tiempo_restante // 60)
        segundos = int(tiempo_restante % 60)

        await interaction.followup.send(
            f"⏳ The {rol_equipo.mention} team must wait {minutos}m {segundos}s before using /round_pull again.\n" +
            "If you wanted to re-roll your weapons, use /extra-pull.",
            ephemeral=False
        )
        return True

    return False
