import argparse
import random
from typing import List
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

def simular_ruleta(tiradas: int, corridas: int, numero_elegido: int, nombre_archivo: str) -> None:
    FRE_TEORICA: float = 1.0 / 37.0
    ESPERANZA_TEORICA: float = 18.0
    VARIANZA_TEORICA: float = 114.0
    DESVIO_TEORICO: float = float(np.sqrt(VARIANZA_TEORICA))

    promedios_finales: List[float] = []
    # Preparamos la grilla 2x3 (6 gráficos) para que entre todo
    fig: plt.Figure
    axs: np.ndarray
    fig, axs = plt.subplots(3, 2, figsize=(15, 12))
    plt.subplots_adjust(hspace=0.4, wspace=0.3)

    for c in range(corridas):
        resultados: List[int] = [random.randint(0, 36) for _ in range(tiradas)]
        promedio_corrida: float = float(np.mean(resultados))
        promedios_finales.append(promedio_corrida)
        # Cálculos de convergencia
        eje_n: np.ndarray = np.arange(1, tiradas + 1)
        freq_relativa: np.ndarray = np.cumsum(np.array(resultados) == numero_elegido) / eje_n
        promedios: np.ndarray = np.cumsum(resultados) / eje_n
        varianzas: List[float] = [float(np.var(resultados[:i])) if i > 1 else 0.0 for i in range(1, tiradas + 1)]
        desvios: np.ndarray = np.sqrt(np.array(varianzas, dtype=float))

        # 1. Frecuencia Relativa
        axs[0, 0].plot(eje_n, freq_relativa, alpha=0.5)
        # 2. Promedio
        axs[0, 1].plot(eje_n, promedios, alpha=0.5)
        # 3. Varianza
        axs[1, 0].plot(eje_n, varianzas, alpha=0.5)
        # 4. Desvío
        axs[1, 1].plot(eje_n, desvios, alpha=0.5)

    # Configuración de líneas teóricas
    axs[0, 0].axhline(FRE_TEORICA, color='red', linestyle='--', label='Teórica')
    axs[0, 0].set_title(f'Convergencia Frecuencia Relativa (Número {numero_elegido})')
    
    axs[0, 1].axhline(ESPERANZA_TEORICA, color='red', linestyle='--', label='Teórica')
    axs[0, 1].set_title('Convergencia del Promedio')

    axs[1, 0].axhline(VARIANZA_TEORICA, color='red', linestyle='--', label='Teórica')
    axs[1, 0].set_title('Convergencia de la Varianza')

    axs[1, 1].axhline(DESVIO_TEORICO, color='red', linestyle='--', label='Teórica')
    axs[1, 1].set_title('Convergencia del Desvío Estándar')

    # 5. Distribución de frecuencias (Bar plot del total de la última corrida como muestra)
    counts: np.ndarray = np.bincount(resultados, minlength=37)
    axs[2, 0].bar(range(37), counts / float(tiradas), color='skyblue', edgecolor='black')
    axs[2, 0].axhline(FRE_TEORICA, color='red', linestyle='--')
    axs[2, 0].set_title('Distribución de Frecuencias (Última Corrida)')

    # 6. Histograma TCL (Promedios de todas las corridas)
    axs[2, 1].hist(promedios_finales, bins=10, density=True, color='lightgreen', edgecolor='black', alpha=0.7)
    # Curva Normal superpuesta
    mu: float
    std: float
    mu, std = norm.fit(promedios_finales)
    xmin: float
    xmax: float
    xmin, xmax = axs[2, 1].get_xlim()
    x: np.ndarray = np.linspace(xmin, xmax, 100)
    p: np.ndarray = norm.pdf(x, mu, std)
    axs[2, 1].plot(x, p, 'k', linewidth=2, label='Normal Fit')
    axs[2, 1].set_title('Histograma de Promedios (TCL)')

    plt.savefig(nombre_archivo)
    print(f"Imagen guardada: {nombre_archivo}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', type=int, required=True, help="Tiradas")
    parser.add_argument('-c', type=int, required=True, help="Corridas")
    parser.add_argument('-n', type=int, required=True, help="Número elegido")
    parser.add_argument('-f', type=str, required=True, help="Nombre de archivo")
    args = parser.parse_args()
    
    simular_ruleta(args.t, args.c, args.n, args.f)