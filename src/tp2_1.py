import argparse
import random
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List
from scipy import stats
from scipy.stats import chi2

nombres_generadores: Dict[str, str] = {
    'GCL': 'Generador Congruencial Lineal',
    'p': "Python Native",
    'ms': "Parte Media del Cuadrado",
    'r': "RANDU",
}

# constantes para GCL de java
glc_java :Dict[str, int] = {
    'A': 25214903917,
    'C': 11,
    'M': 2**48,
    'SEED': 0
}

# constantes para generador medio de cuadrado
generator_ms :Dict[str, int] = {
    'SEED': 3972
}
# seed 2159 "rompe" rápidamente. Estaría bien mostrarlo en el informe.
# seed 1231, 9731 generan patrón notable en 512x5125
# 540
# 3792


generator_randu :Dict[str, int] = {
    'SEED': 12345,
    'A': 65539,
    'M': 2**31,
}


# Consigna
# Definir al menos dos generadores de números pseudoaleatorios, además de GCL
# Evaluar con al menos 4 tests
# comparar generadores entre sí y vs generador de python


def generador_congruencial_lineal(n: int) -> List[float]:
    a: int = glc_java['A']
    c: int = glc_java['C']
    m: int = glc_java['M']
    seed: int = glc_java['SEED']

    numeros: List[float] = []
    for _ in range(n):
        seed = (a * seed + c) % m
        numeros.append(seed / m)
    return numeros

def generador_python(n: int) -> List[float]:
    return [random.random() for _ in range(n)]

def generador_media_cuadrado(n: int) -> List[float]:
    seed: int = generator_ms['SEED']
    numeros: List[float] = []
    for i in range(n):
        seed_squared: int = seed ** 2
        str_seed = str(seed_squared) if len(str(seed_squared)) == 8 else str(seed_squared).zfill(8)    
        seed = int(str_seed[2:6])
        numeros.append(seed / 10000)
    return numeros

# ---------------------------------------------------
# RANDU
# X_{n+1} = (65539 * X_n) mod 2^31
# ---------------------------------------------------

def randu(n: int) -> List[float]:
    nums: List[float] = []
    x: int = generator_randu['SEED']

    for _ in range(n):
        x = (generator_randu['A'] * x) % generator_randu['M']
        nums.append(x / generator_randu['M'])

    return nums


# Esta implementación la generó para mostrar la correlación de RANDU. 
# Estaría bien adaptarla a los números generados que para poder aplicarle varios tests
def graficar_scatter_randu_2d() -> None:
    """
    Grafica X_{n+1} en función de X_n para RANDU.
    Permite visualizar las correlaciones de RANDU.
    """
    # Generamos suficientes números para tener pares consecutivos
    n: int = 10000
    x: int = generator_randu['SEED']
    numeros: List[float] = []
    
    for _ in range(n):
        x = (generator_randu['A'] * x) % generator_randu['M']
        numeros.append(x / generator_randu['M'])
    
    # Creamos pares (X_n, X_{n+1})
    x_n: np.ndarray = np.array(numeros[:-1])
    x_n_plus_1: np.ndarray = np.array(numeros[1:])
    
    # Graficamos
    plt.figure(figsize=(8, 8))
    plt.scatter(x_n, x_n_plus_1, alpha=0.5, s=1)
    plt.xlabel('$X_n$')
    plt.ylabel('$X_{n+1}$')
    plt.title('RANDU: $X_{n+1}$ vs $X_n$')
    plt.grid(True, alpha=0.3)
    plt.show()

def prueba_chi_cuadrado(numeros: List[float], k: int = 10) -> float:
    """
    Realiza la prueba de chi-cuadrado para evaluar la uniformidad de los números generados.

    Parámetros
    ----------
    numeros : list[float]
        Lista de valores entre 0 y 1.

    k : int
        Número de intervalos para la prueba (default: 10).

    Retorna
    -------
    float
        Valor del estadístico chi-cuadrado.
    """
    n = len(numeros)
    # Definir los 10 bins
    bins = np.linspace(0, 1, 11) # [0, 0.1, ..., 1.0]

    # Contar frecuencias
    observados, _ = np.histogram(numeros, bins=bins)

    # Frecuencias esperadas (10000 / 10 = 1000 por cada bin)
    esperados = np.full(k, n/k)

    # Test
    statistic, pvalue = stats.chisquare(f_obs=observados, f_exp=esperados)
    return statistic

# Esta generación de bitmap solo considera blanco o negro, podría extenderse para utilizar más escalas de colores y mostrar de otro modo los patrones
def graficar_bitmap(numeros: List[float], titulo: str = "Bitmap aleatorio"):
    """
    Convierte una lista de números en una imagen blanco/negro.

    Parámetros
    ----------
    numeros : list[float]
        Lista de valores entre 0 y 1.

    titulo : str
        Título del gráfico.
    """

    # Convertimos a bits:
    # < 0.5 -> 0 (negro)
    # >= 0.5 -> 1 (blanco)
    bits: np.ndarray = np.array([1 if x >= 0.5 else 0 for x in numeros])
    
    # Calculamos tamaño cuadrado máximo posible
    lado: int = int(np.sqrt(len(bits)))

    # Recortamos para formar matriz cuadrada
    bits = bits[:lado * lado]

    # Convertimos a matriz 2D
    bitmap: np.ndarray = bits.reshape((lado, lado))

    # Graficamos
    plt.figure(figsize=(6, 6))
    plt.imshow(bitmap, cmap="gray", interpolation="nearest")
    plt.title(titulo)
    plt.axis("off")

    plt.show()


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-g', '--generador', choices=['GCL', 'p', 'ms', 'r'], required=True, help=f"GCL={nombres_generadores['GCL']}, p={nombres_generadores['p']}, ms={nombres_generadores['ms']}, r={nombres_generadores['r']}")
    parser.add_argument('-n', '--ladoGrilla', type=int, required=True, help="Lado de grilla para gráfico")
    
    args: argparse.Namespace = parser.parse_args()


    dimension_grilla: int = args.ladoGrilla * args.ladoGrilla

    if args.generador == 'GCL':
        numeros = generador_congruencial_lineal(dimension_grilla)
    elif args.generador == 'p':
        numeros = generador_python(dimension_grilla)
    elif args.generador == 'ms':
        numeros = generador_media_cuadrado(dimension_grilla)
    elif args.generador == 'r':
        numeros = randu(dimension_grilla)
        graficar_scatter_randu_2d()
    
    graficar_bitmap(numeros, f"Generador {nombres_generadores[args.generador]}")

    deviacion_chi_cuadrado: float = prueba_chi_cuadrado(numeros)  