import argparse
import math
import random
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np

# Consignas de desarrollo
# Elaborar un programa por cada distribución de probabilidad en lenguaje Python 3.x.
# Testear la generación de valores de la forma más conveniente para cada caso (queda a criterio del grupo el como testear). # -- como adicional, yo, compararía contra alguna librería que genere esos valores.

class Distribucion: 
    def __init__(self, nombre: str, label: str):
        self.nombre = nombre
        self.label = label

distribuciones: Dict[str, Distribucion] = {
    'uniforme': Distribucion(nombre='Distribución Uniforme', label='u'),
    'exponencial': Distribucion(nombre='Distribución Exponencial', label='e'),
    'gamma': Distribucion(nombre='Distribución Gamma', label='g'),
    'normal': Distribucion(nombre='Distribución Normal', label='m'),
    'pascal': Distribucion(nombre='Distribución Pascal', label='p'),
    'binomial': Distribucion(nombre='Distribución Binomial', label='b'),
    'hipergeometrica': Distribucion(nombre='Distribución Hipergeométrica', label='h'),
    'poisson': Distribucion(nombre='Distribución Poisson', label='po'),
    'empirica_discreta': Distribucion(nombre='Distribución Empírica Discreta', label='ed')
}




## IMPORTANTE 
## los argumentos los generó COPILOT, no aseguro que estén bien.
## Se deben revisar las definiciones teóricas de cada distribución

def generador_valores_uniforme(a: float, b: float, n: int) -> List[float]:
    """    
    1. SUBROUTINE UNIFORM (A,B,X)
    2. R = RND (R)
    3. X= A+(B-A)*R
    3. RETURN
    """
    r = [random.random() for _ in range(n)]
    x: List[float] = [a + (b - a) * r_i for r_i in r]
    return x

def generador_valores_exponencial(lambda_param: float, n: int) -> List[float]:
    """
    C   SUBROUTINE EXPENT (EX, X)
    R = RND(R)
    X = -EX * LOG(R)
    RETURN
    """
    r: List[float] = [random.random() for _ in range(n)] 
    x: List[float] = [-math.log(r_i) / lambda_param for r_i in r]
    return x

def generador_valores_gamma(alpha: int, beta: float, n: int) -> List[float]:
    tr: List[float] = [1.0 for _ in range(n)]
    x: List[float] = []
    for i in range(0, n):
        for j in range(0, int(alpha)):
            tr[i] = (tr[i] * random.random())
        x.append(-math.log(tr[i]) / beta)
    return x

def generador_valores_normal(mu: float, sigma: float, n: int):
    pass

def generador_valores_pascal(r: int, p: float, n: int):
    pass

def generador_valores_binomial(n: int, p: float, n_samples: int):
    pass

def generador_valores_hipergeometrica(N: int, K: int, n: int, n_samples: int):
    pass

def generador_valores_poisson(lambda_param: float, n: int):
    pass

def generador_valores_empirica_discreta(probabilidades: List[float], n: int):
    pass

# Graficos
def graficar_exponencial(lambda_param: float, valores_generados: List[float]):
    EX = 1 / lambda_param
    DX = 1 / lambda_param
    
    # 1. Configurar el tamaño y estilo del gráfico
    plt.figure(figsize=(10, 6))
    
    # 2. Graficar la distribución obtenida (Histograma de densidad)
    # Usamos density=True para que el área total del histograma sea 1
    count, bins, ignored = plt.hist(
        valores_generados, 
        bins='auto', 
        density=True, 
        alpha=0.6, 
        color='skyblue', 
        edgecolor='white',
        label=f'Obtenida (n={len(valores_generados)})'
    )
    
    # 3. Calcular y graficar la distribución esperada (Teórica)
    # Generamos un rango de X desde 0 hasta el máximo valor obtenido para la curva continua
    x_teorico = np.linspace(0, max(valores_generados), 1000)
    y_teorico = lambda_param * np.exp(-lambda_param * x_teorico)
    
    plt.plot(
        x_teorico, 
        y_teorico, 
        color='red', 
        linewidth=2, 
        label=f'Esperada ($\\lambda$={lambda_param})'
    )
    
    # 4. Añadir métricas estadísticas en un cuadro de texto dentro del gráfico
    media_obtenida = np.mean(valores_generados)
    desvio_obtenido = np.std(valores_generados)
    
    info_text = (
        f"Métricas Teóricas:\n"
        f"  $\\mu$ (EX) = {EX:.4f}\n"
        f"  $\\sigma$ (DX) = {DX:.4f}\n\n"
        f"Métricas Obtenidas:\n"
        f"  Media = {media_obtenida:.4f}\n"
        f"  Desvío = {desvio_obtenido:.4f}"
    )
    
    # Colocamos el cuadro en la esquina superior derecha
    plt.gca().text(
        0.95, 0.95, info_text, 
        transform=plt.gca().transAxes, 
        fontsize=10,
        verticalalignment='top', 
        horizontalalignment='right',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='gray')
    )
    
    plt.title('Validación de Generador: Distribución Exponencial', fontsize=14, fontweight='bold')
    plt.xlabel('Valor de la Variable ($X$)', fontsize=12)
    plt.ylabel('Densidad de Probabilidad $f(x)$', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='center right')
    
    plt.savefig('generador_exp')
    plt.show()

def graficar_uniforme(a_param: float, b_param: float, valores_generados: List[float]):
    MU = (a_param + b_param) / 2
    VX = ((b_param - a_param) ** 2) / 12
    SIGMA = np.sqrt(VX)

    plt.figure(figsize=(10, 6))
    
    plt.hist(
        valores_generados, 
        bins='auto', 
        density=True, 
        alpha=0.6, 
        color='palegreen', 
        edgecolor='white',
        label=f'Obtenida (n={len(valores_generados)})'
    )
    
    # Generamos un rango de X que extienda un 10% los márgenes para ver la caída a cero
    margen = (b_param - a_param) * 0.1
    x_teorico = np.linspace(a_param - margen, b_param + margen, 1000)
    
    y_teorico = np.where((x_teorico >= a_param) & (x_teorico <= b_param), 1 / (b_param - a_param), 0)
    
    plt.plot(
        x_teorico, 
        y_teorico, 
        color='darkgreen', 
        linewidth=2, 
        label=f'Esperada (U[{a_param}, {b_param}])'
    )
    
    media_obtenida = np.mean(valores_generados)
    desvio_obtenido = np.std(valores_generados)
    
    info_text = (
        f"Métricas Teóricas:\n"
        f"  $\\mu$ = {MU:.4f}\n"
        f"  $\\sigma$ = {SIGMA:.4f}\n\n"
        f"Métricas Obtenidas:\n"
        f"  Media = {media_obtenida:.4f}\n"
        f"  Desvío = {desvio_obtenido:.4f}"
    )
    
    plt.gca().text(
        0.05, 0.95, info_text, 
        transform=plt.gca().transAxes, 
        fontsize=10,
        verticalalignment='top', 
        horizontalalignment='left',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='gray')
    )
    
    plt.title('Validación de Generador: Distribución Uniforme', fontsize=14, fontweight='bold')
    plt.xlabel('Valor de la Variable ($X$)', fontsize=12)
    plt.ylabel('Densidad de Probabilidad $f(x)$', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.ylim(0, (1 / (b_param - a_param)) * 1.5) # Ajusta el eje Y para que no tape el texto
    plt.legend(loc='upper right')
    
    plt.savefig('generador_uni.png', dpi=300, bbox_inches='tight')
    plt.show()
# 

if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-d', '--distribucion', choices=list([d.label for d in distribuciones.values()]), required=True, help="Distribución de probabilidad a utilizar")
    parser.add_argument('-n', '--observaciones', type=int, required=True, help="Número de observaciones a generar")
    
    args: argparse.Namespace = parser.parse_args()
    if args.distribucion == distribuciones['uniforme'].label:
        a = float(input("Ingrese el valor de a: "))
        b = float(input("Ingrese el valor de b: "))
        valores: List[float] = generador_valores_uniforme(a, b, args.observaciones)
        graficar_uniforme(a, b, valores)
    elif args.distribucion == distribuciones['exponencial'].label:
        lambda_param = float(input("Ingrese el valor de lambda: "))
        valores: List[float] = generador_valores_exponencial(lambda_param, args.observaciones)
        graficar_exponencial(lambda_param, valores)
    elif args.distribucion == distribuciones['gamma'].label:
        alpha = int(input("Ingrese el valor de alpha: "))
        beta = float(input("Ingrese el valor de beta: "))
        valores: List[float] = generador_valores_gamma(alpha, beta, args.observaciones)
        print(valores)