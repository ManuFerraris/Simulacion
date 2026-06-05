import argparse
import random
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List
from scipy import stats
from scipy.stats import chi2
import requests
from collections import Counter
from statsmodels.sandbox.stats.runs import runstest_1samp
from tabulate import tabulate

nombres_generadores: Dict[str, str] = {
    'GCL': 'Generador Congruencial Lineal',
    'p': "Python Native",
    'ms': "Parte Media del Cuadrado",
    'r': "RANDU",
    'ro': "Random.org",
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
    'SEED': 3792
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

def get_random_org_url(n: int, min_value: int = 1, max_value: int = 10) -> str:
    return f"https://www.random.org/integers/?num={n}&min={min_value}&max={max_value}&col=1&base=10&format=plain&rnd=new"

def generador_random_org(n: int) -> List[int]:
    """
    Genera números pseudoaleatorios (entre 1 y 10) utilizando la API de random.org.    
    Parámetros
    ----------
    n : int
        Cantidad de números a generar.

    Retorna
    -------
    list[int]
        Lista de números pseudoaleatorios entre 1 y 10.
    """
    url = get_random_org_url(n)
    
    try:
        response = requests.get(url)
        if(response.status_code != 200):
            raise Exception(f"Error al obtener datos de random.org: {response.status_code}")
        numeros = [float(num) for num in response.text.strip().split('\n')]
        return numeros    
    except Exception as e:
        raise Exception(e)

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

def graficar_scatter_2d(numeros: List[float], nombre_generador: str) -> None:
    """
    Grafica X_{n+1} en función de X_n
    Permite visualizar las correlaciones
    
    Parámetros
    ----------
    numeros : list[float]
        Lista de valores numéricos.
    nombre_generador : str
        Nombre del generador de números pseudoaleatorios.
    """
    # Creamos pares (X_n, X_{n+1})
    x_n: np.ndarray = np.array(numeros[:-1])
    x_n_plus_1: np.ndarray = np.array(numeros[1:])
    
    plt.figure(figsize=(8, 8))
    plt.scatter(x_n, x_n_plus_1, alpha=0.5, s=1)
    plt.xlabel('$X_n$')
    plt.ylabel('$X_{n+1}$')
    plt.title(f'{nombre_generador}: $X_{{n+1}}$ vs $X_n$')
    plt.grid(True, alpha=0.3)
    plt.show()

def generar_bins_0_1(k: int = 10) -> np.ndarray:
    """
    Genera los bordes de intervalo para una prueba de chi-cuadrado uniforme en [0, 1].
    """
    return np.linspace(0.0, 1.0, k + 1)

def prueba_series(numeros: List[float]) -> tuple[float, float]:
    """
    Realizar la prueba dividiendo el espacio en k x k celdas y contando las frecuencias observadas. Luego, comparar con las frecuencias esperadas bajo la hipótesis de independencia utilizando una prueba de chi-cuadrado.
    """
    k: int = 10
    bins: np.ndarray = np.linspace(0.0, 1.0, k + 1)
    observed, _, _ = np.histogram2d(numeros[:-1], numeros[1:], bins=[bins, bins])
    num_pairs = len(numeros) - 1
    expected_val = num_pairs / (k * k)
    statistic, pvalue = stats.chisquare(f_obs=observed.flatten(), f_exp=np.full(k*k, expected_val))

    return statistic, pvalue

def prueba_chi_cuadrado(numeros: List[float], bins: np.ndarray) -> tuple[float, float]:
    """
    Realiza la prueba de chi-cuadrado para evaluar la uniformidad de los números generados.

    Parámetros
    ----------
    numeros : list[float]
        Lista de valores numéricos.

    bins : np.ndarray
        Bordes de los intervalos para la prueba.

    Retorna
    -------
    float
        Valor del estadístico chi-cuadrado.
    float
        Valor del p-valor.
    """
    n: int = len(numeros)
    observados, _ = np.histogram(numeros, bins=bins)
    esperados: np.ndarray = np.full(len(observados), n / len(observados))

    statistic, pvalue = stats.chisquare(f_obs=observados, f_exp=esperados)
    return statistic, pvalue

def prueba_rachas(numeros: List[float]) -> tuple[float, float]:
    """
    Realiza la prueba de rachas para evaluar la independencia de los números generados.

    Parámetros
    ----------
    numeros : list[float]
        Lista de valores entre 0 y 1 o entre 1 y 10.

    Retorna
    -------
    float
        Valor del estadístico de rachas.
    float
        Valor del p-valor.
    """
    z_stat, p_valor = runstest_1samp(numeros, cutoff='median', correction=True)

    return z_stat, p_valor

def prueba_kolmogorov_smirnov(numeros: List[float]) -> tuple[float, float]:
    """
    Realiza la prueba de Kolmogorov-Smirnov para evaluar la uniformidad de los números generados.

    Parámetros
    ----------
    numeros : list[float]

    Retorna
    -------
    float
        Valor del estadístico D.
    float
        Valor del p-valor.
    """ 
    statistic, pvalue = stats.kstest(numeros, 'uniform')
    return statistic, pvalue

def prueba_cusum(numeros: List[float]) -> tuple[float, float]:
    """
    Realiza la prueba de CUSUM para evaluar la independencia de los números generados.

    Parámetros
    ----------
    numeros : list[float]

    Retorna
    -------
    float
        Valor del estadístico CUSUM.
    float
        Valor del p-valor.
    """
    n: int = len(numeros)
    media: float = np.mean(numeros)
    cusum: np.ndarray = np.cumsum(numeros - media)
    
    statistic: float = np.max(np.abs(cusum)) / np.sqrt(n * np.var(numeros))
    pvalue: float = 2 * (1 - stats.norm.cdf(statistic))

    return statistic, pvalue

def graficar_cusum(numeros: List[float], nombre_generador: str) -> None:
    """
    Grafica la función de CUSUM para evaluar la independencia de los números generados.

    Parámetros
    ----------
    numeros : list[float]
        Lista de valores numéricos.

    nombre_generador : str
        Nombre del generador de números pseudoaleatorios.
    """
    n: int = len(numeros)
    media: float = np.mean(numeros)
    cusum: np.ndarray = np.cumsum(numeros - media)

    plt.figure(figsize=(10, 6))
    plt.plot(cusum, label='CUSUM', color='blue')
    plt.axhline(0, color='red', linestyle='--', label='Media')
    plt.xlabel('Índice')
    plt.ylabel('CUSUM')
    plt.title(f'Gráfico CUSUM - {nombre_generador}')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.show()

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

def graficar_histograma(numeros: List[float], generador: str):
    plt.figure(figsize=(8, 6))
    clases = 10
    plt.hist(numeros, bins=clases, edgecolor='blue', alpha=0.7)

    frec_teorica = len(numeros) / clases
    plt.axhline(frec_teorica, color='red', linestyle='--', linewidth=2, label=f'Frecuencia teórica: {frec_teorica:.2f}')
    plt.xlabel('Valor')
    plt.ylabel('Frecuencia')
    plt.title(f'Histograma - {generador}')
    plt.grid(True, alpha=0.3)
    plt.show()

def graficar_barras(numeros, generador):
    valores = np.arange(1, 11)
    conteos = Counter(numeros)
    frecuencias = [conteos[v] for v in valores]
    frec_teorica = len(numeros) / len(valores)

    plt.figure(figsize=(8, 6))

    plt.bar(
        valores,
        frecuencias,
        width=0.8,
        edgecolor='blue',
        alpha=0.7
    )

    plt.axhline(
        frec_teorica,
        color='red',
        linestyle='--',
        linewidth=2,
        label=f'Frecuencia teórica: {frec_teorica:.2f}'
    )

    plt.xticks(valores)

    plt.xlabel('Valor')
    plt.ylabel('Frecuencia')
    plt.title(f'Distribución de frecuencias - {generador}')
    plt.grid(True, axis='y', alpha=0.3)
    plt.legend()

    plt.show()

def graficar_kolmogorov_smirnov(numeros: List[float], generador: str):
    plt.figure(figsize=(8, 6))
    stats.probplot(numeros, dist="uniform", plot=plt)
    plt.title(f'Gráfico Distribución empírica vs Distribución teórica - {generador}')
    plt.grid(True, alpha=0.3)
    plt.show()

if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-g', '--generador', choices=['GCL', 'p', 'ms', 'r', 'ro'], required=True, help=f"GCL={nombres_generadores['GCL']}, p={nombres_generadores['p']}, ms={nombres_generadores['ms']}, r={nombres_generadores['r']}, ro={nombres_generadores['ro']}")
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
    elif args.generador == 'ro':
        numeros = generador_random_org(args.ladoGrilla)

    if args.generador != 'ro':
        graficar_bitmap(numeros, f"Generador {nombres_generadores[args.generador]}")
        graficar_histograma(numeros, nombres_generadores[args.generador])
    else:
        graficar_barras(numeros, nombres_generadores[args.generador])
    graficar_scatter_2d(numeros, nombres_generadores[args.generador])
    graficar_kolmogorov_smirnov(numeros, nombres_generadores[args.generador])
    graficar_cusum(numeros, nombres_generadores[args.generador])

    # Ejecucion de pruebas estadísticas
    bins = generar_bins_0_1() if args.generador != 'ro' else np.arange(1, 11)

    chi_stat, p_valor_chi = prueba_chi_cuadrado(numeros, bins=bins)
    z_stat, p_valor = prueba_rachas(numeros)
    d_stat, p_valor_ks = prueba_kolmogorov_smirnov(numeros)
    p_valor_series, _ = prueba_series(numeros)
    p_valor_cusum, _ = prueba_cusum(numeros)
    nivel_significancia = 0.05

    headers_pvalues = ["Generador", "p-valor Chi-cuadrado", "p-valor Rachas", "p-valor Kolmogorov-Smirnov", "p-valor Series", "p-valor CUSUM"]
    data_pvalues = [[nombres_generadores[args.generador], f"{p_valor_chi:.4f}", f"{p_valor:.4f}", f"{p_valor_ks:.4f}", f"{p_valor_series:.4f}", f"{p_valor_cusum:.4f}"]]
    
    headers_resultados = ["Generador", "Chi-cuadrado", "Rachas", "Kolmogorov-Smirnov", "Series", "CUSUM"]
    data_results = [[nombres_generadores[args.generador], f"{'OK' if p_valor_chi > nivel_significancia else 'ERROR'}", f"{'OK' if p_valor > nivel_significancia else 'ERROR'}", f"{'OK' if p_valor_ks > nivel_significancia else 'ERROR'}", f"{'OK' if p_valor_series > nivel_significancia else 'ERROR'}", f"{'OK' if p_valor_cusum > nivel_significancia else 'ERROR'}"]]
    print(tabulate(data_pvalues, headers=headers_pvalues, tablefmt="grid"))
    print(tabulate(data_results, headers=headers_resultados, tablefmt="grid"))
