import random
from comandos.pulls.constantes_pull import ( 
    pesos, 
    probabilidades, 
    cuantity_weapons, 
    rango_distancia,
    five_percentage_drop,
    twenty_five_percentage_drop,
    seventy_percentage_drop,
    index_exclude
)

for idx in five_percentage_drop:
    pesos[idx] = probabilidades[0] / len(five_percentage_drop)
for idx in twenty_five_percentage_drop:
    pesos[idx] = probabilidades[1] / len(twenty_five_percentage_drop)
for idx in seventy_percentage_drop:
    pesos[idx] = probabilidades[2] / len(seventy_percentage_drop)

def elegir_arma_con_probabilidad(armas_previas, distancia_minima):
    posibles_armas = [
        idx for idx in pesos
        if idx not in armas_previas
        and idx not in index_exclude
        and (
            not armas_previas or abs(idx - armas_previas[-1]) >= distancia_minima
        )
    ]

    if not posibles_armas:
        return None

    pesos_filtrados = [pesos[idx] for idx in posibles_armas]

    total = sum(pesos_filtrados)
    pesos_normalizados = [p / total for p in pesos_filtrados]

    return random.choices(posibles_armas, weights=pesos_normalizados, k=1)[0]

def seleccionar_armas(cantidad=cuantity_weapons, distancia_minima = None):

    if distancia_minima is None:
        distancia_minima = random.randint(*rango_distancia)
    armas_seleccionadas = []
    intentos = 0
    while len(armas_seleccionadas) < cantidad:
        if intentos > 100:
            raise Exception("Not enough valid weapons could be selected.")
        nueva_arma = elegir_arma_con_probabilidad(armas_seleccionadas, distancia_minima)
        if nueva_arma is not None:
            armas_seleccionadas.append(nueva_arma)
        intentos += 1
    return armas_seleccionadas