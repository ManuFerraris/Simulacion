import argparse
import math
import random
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
import bisect
from scipy.stats import norm, expon

SEED_DEFAULT = 42
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
    'normal': Distribucion(nombre='Distribución Normal', label='n'),
    'pascal': Distribucion(nombre='Distribución Pascal', label='p'),
    'binomial': Distribucion(nombre='Distribución Binomial', label='b'),
    'hipergeometrica': Distribucion(nombre='Distribución Hipergeométrica', label='h'),
    'poisson': Distribucion(nombre='Distribución Poisson', label='po'),
    'empirica_discreta': Distribucion(nombre='Distribución Empírica Discreta', label='ed')
}

distribucion_empirica_discreta: list[tuple[int, float]] = [(1, 0.1), (2, 0.3), (3, 0.3), (4, 0.2), (5, 0.1)]


## IMPORTANTE 
## los argumentos los generó COPILOT, no aseguro que estén bien.
## Se deben revisar las definiciones teóricas de cada distribución


# =================== Generadores mediante transformada inversa ===================
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

def generador_valores_normal(mu: float, sigma: float, n: int) -> List[float]:
    """
    SUBROUTINE NORMAL (EX, VX, X)
    SUM = 0
    DO 10 I = 1, 12
    10 SUM = SUM + RND(R)
    X = EX + (SUM - 6.0) * STDX(VX)
    RETURN
    """
    x: List[float] = [0 for i in range(0,n)]
    for j in range(0, n):
        for _ in range(0, 11):
            x[j] = x[j] + random.random()
        x[j] = mu + (x[j] - 6) * sigma
    return x

def generador_valores_pascal(r: int, p: float, n: int):
    pass

def generador_valores_binomial(n: int, p: float, n_samples: int):
    pass

def generador_valores_hipergeometrica(N: int, K: int, n: int, n_samples: int):
    pass

def generador_valores_poisson(lambda_param: float, n: int):
    pass

def generador_valores_empirica_discreta(valores: List[tuple[int, float]], n: int):
    
    acumuladas: list[float] = []
    valores_discretos: int = []
    suma = 0.0
    
    for valor, prob in valores:
        if prob < 0:
            raise ValueError("Las probabilidades no pueden ser negativas.")
        
        suma += prob
        acumuladas.append(suma)
        valores_discretos.append(valor)
    
    if not abs(suma - 1.0) < 1e-9:
        raise ValueError(
            f"La suma de probabilidades debe ser 1. Suma actual: {suma}"
        )
    
    acumuladas[-1] = 1.0
    
    resultados: List[int] = []
    
    for _ in range(n):
        r: float = random.random()
        indice: int = bisect.bisect_left(acumuladas, r)
        resultados.append(valores_discretos[indice])
    
    return resultados

# =================== Generadores mediante transformada inversa ===================

# =================== Generadores mediante método de rechazo ===================

def f_normal(MU: float, SIGMA: float):
    """Normal con parámetros MU y SIGMA."""
    return lambda x : norm.pdf(x, loc=MU, scale=SIGMA)

def rejection_sampling_normal(n: int, MU: float, SIGMA: float, A: float, B: float, rng=None):
    """
    Genera n muestras de f(x) ~ Normal(MU, SIGMA) por método del rechazo.

    Parámetros
    ----------
    n         : cantidad de muestras deseadas
    MU, SIGMA : parametros mu y sigma "reales" de la distribución normal
    a,b       : dominio [a, b] donde se buscan candidatos
    rng       : numpy Generator (semilla reproducible)

    Retorna
    -------
    accepted_points : Lista de tuplas (x, r2) de puntos aceptados
    rejected_points : Lista de tuplas (x, r2) de puntos rechazados
    n_tries         : total de intentos realizados  (para calcular eficiencia)
    """
    funcion_normal = f_normal(MU, SIGMA)
    C: float = 1.0 / funcion_normal(MU)   # = σ√2π  (factor de escala)
        
    # ─── Constante de escalado c ────────────────────────────────────────────
    #
    #   Necesitamos  c · f(x) ≤ 1  para todo x ∈ [A, B].
    #   El máximo de f(x) es f(μ) = 1 / (σ√2π).
    #   Por lo tanto  c = 1 / f(μ) = σ√2π.
    #   Así  c · f(x) ∈ (0, 1]  y podemos compararlo con r₂ ~ U(0,1).
    #

    if rng is None:
        rng = np.random.default_rng(seed=SEED_DEFAULT)

    accepted_points: List[tuple[float, float]] = []
    rejected_points: List[tuple[float, float]] = []
    accepted: int = 0
    n_tries: int  = 0

    while accepted < n:
        # Paso 1 – proponer candidato uniforme en [a, b]
        r1: float = rng.uniform(0.0, 1.0)
        x_candidate: float = A + (B - A) * r1

        # Paso 2 – criterio de aceptación
        r2: float = rng.uniform(0.0, 1.0)

        if r2 <= C * funcion_normal(x_candidate):
            accepted_points.append((x_candidate, r2))            
            accepted += 1
        else:
            rejected_points.append((x_candidate, r2))
        n_tries += 1

    return accepted_points, rejected_points, n_tries


def rejection_sampling_uniform():
    pass

def f_exp(lambda_param):
    """
    Densidad Exponencial de parámetro lambda.

    f(x) = lambda * exp(-lambda*x), x >= 0
    """
    return lambda x: expon.pdf(x, scale=1.0 / lambda_param)

def rejection_sampling_exponential(
    n: int,
    LAMBDA: float,
    A: float,
    B: float,
    rng=None):    
    """
    Genera n muestras de una Exponencial(lambda)
    mediante el método del rechazo.

    Parámetros
    ----------
    n       : cantidad de muestras deseadas
    LAMBDA  : parámetro de la exponencial
    A, B    : intervalo de búsqueda de candidatos
    rng     : generador aleatorio opcional

    Retorna
    -------
    accepted_points : puntos aceptados (x, r2)
    rejected_points : puntos rechazados (x, r2)
    n_tries         : cantidad total de intentos
    """

    funcion_exponencial = f_exp(LAMBDA)

    # ────────────────────────────────────────────────
    # Escalado:
    #
    # max f(x) = f(0) = lambda
    #
    # Queremos:
    #      C * f(x) <= 1
    #
    # Entonces:
    #      C = 1/lambda
    #
    # y queda:
    #      C*f(x)=exp(-lambda*x)
    # ────────────────────────────────────────────────

    C: float = 1.0 / funcion_exponencial(0.0)

    if rng is None:
        rng = np.random.default_rng(seed=SEED_DEFAULT)

    accepted_points: List[tuple[float, float]] = []
    rejected_points: List[tuple[float, float]] = []

    accepted: int = 0
    n_tries: int = 0

    while accepted < n:
        # Paso 1:
        # Generar candidato uniforme en [A,B]
        r1: float = rng.uniform(0.0, 1.0)

        x_candidate: float = A + (B - A) * r1

        # Paso 2:
        # Generar altura aleatoria uniforme
        r2: float = rng.uniform(0.0, 1.0)

        # Paso 3:
        # Aceptar si el punto cae debajo de
        # la curva escalada C*f(x)
        if r2 <= C * funcion_exponencial(x_candidate):

            accepted_points.append(
                (x_candidate, r2)
            )

            accepted += 1
        else:

            rejected_points.append(
                (x_candidate, r2)
            )

        n_tries += 1
    return accepted_points, rejected_points, n_tries

# =================== Generadores mediante método de rechazo ===================

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

def graficar_normal(puntos_aceptados: List[tuple[float, float]], puntos_rechazados: List[tuple[float, float]], intentos: int, MU_TEORICO: float, SIGMA_TEORICO: float, A: float, B: float):
    funcion_normal = f_normal(MU_TEORICO, SIGMA_TEORICO)
    C = 1.0 / funcion_normal(MU_TEORICO)   # = σ√2π  (factor de escala)        

    accepted_x  = [p[0] for p in puntos_aceptados]
    accepted_r2 = [p[1] for p in puntos_aceptados]

    rejected_x  = [p[0] for p in puntos_rechazados]
    rejected_r2 = [p[1] for p in puntos_rechazados]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # — Histograma vs. densidad teórica
    ax = axes[0]
    ax.hist(accepted_x, bins="auto", density=True, alpha=0.65, label="Muestras")
    xs = np.linspace(A, B)
    ax.plot(xs, norm.pdf(xs, MU_TEORICO, SIGMA_TEORICO), lw=1.5, label="Normal teórica")
    ax.set_title("Histograma vs. densidad teórica")
    ax.set_xlabel("x"); ax.set_ylabel("Densidad")
    ax.legend()

    ax2 = axes[1]

    ax2.scatter(
        accepted_x,
        accepted_r2,
        s=8,
        alpha=0.7,
        label="Aceptado"
    )

    ax2.scatter(
        rejected_x,
        rejected_r2,
        s=8,
        alpha=0.4,
        label="Rechazado"
    )

    ax2.plot(xs, C * norm.pdf(xs, MU_TEORICO, SIGMA_TEORICO), lw=1.5, label="c · f(x)  (frontera)")
    ax2.set_title("Geometría del método del rechazo")
    ax2.set_xlabel("x (candidato r₁)")
    ax2.set_ylabel("r₂  (criterio)")
    ax2.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig("rechazo_normal.png", dpi=150)
    plt.show()

def graficar_rechazo_uniforme():
    pass

def graficar_rechazo_exponencial(
    puntos_aceptados: List[tuple[float, float]],
    puntos_rechazados: List[tuple[float, float]],
    intentos: int,
    LAMBDA_TEORICO: float,
    A: float,
    B: float):
    """
    Grafica:

    1) Histograma de muestras aceptadas
       vs densidad exponencial teórica

    2) Geometría del método del rechazo
    """

    funcion_exponencial = f_exp(LAMBDA_TEORICO)

    C: float = 1.0 / funcion_exponencial(0.0)

    accepted_x = [p[0] for p in puntos_aceptados]
    accepted_r2 = [p[1] for p in puntos_aceptados]

    rejected_x = [p[0] for p in puntos_rechazados]
    rejected_r2 = [p[1] for p in puntos_rechazados]

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(12, 5)
    )

    # ------------------------------------------------
    # Histograma vs densidad teórica
    # ------------------------------------------------

    ax = axes[0]

    ax.hist(
        accepted_x,
        bins="auto",
        density=True,
        alpha=0.65,
        label="Muestras"
    )

    xs = np.linspace(A, B, 500)

    ax.plot(
        xs,
        expon.pdf(xs, scale=1.0 / LAMBDA_TEORICO),
        lw=1.5,
        label="Exponencial teórica"
    )

    ax.set_title(
        "Histograma vs. densidad teórica"
    )

    ax.set_xlabel("x")
    ax.set_ylabel("Densidad")
    ax.legend()

    # ------------------------------------------------
    # Geometría del rechazo
    # ------------------------------------------------

    ax2 = axes[1]

    ax2.scatter(
        accepted_x,
        accepted_r2,
        s=8,
        alpha=0.7,
        label="Aceptado"
    )

    ax2.scatter(
        rejected_x,
        rejected_r2,
        s=8,
        alpha=0.4,
        label="Rechazado"
    )

    ax2.plot(
        xs,
        C * expon.pdf(
            xs,
            scale=1.0 / LAMBDA_TEORICO
        ),
        lw=1.5,
        label="c · f(x) (frontera)"
    )

    ax2.set_title(
        "Geometría del método del rechazo"
    )

    ax2.set_xlabel(
        "x (candidato r₁)"
    )

    ax2.set_ylabel(
        "r₂ (criterio)"
    )

    ax2.legend(fontsize=8)

    plt.tight_layout()

    plt.savefig(
        "rechazo_exponencial.png",
        dpi=150
    )

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
        
        # Metodo rechazo
        A: float = 0.0
        B: float = 10.0 / lambda_param
        
        accepted_points, rejected_points, intentos = rejection_sampling_exponential(args.observaciones, lambda_param, A, B)
        graficar_rechazo_exponencial(accepted_points, rejected_points, intentos, lambda_param, A, B)
    elif args.distribucion == distribuciones['gamma'].label:
        alpha = int(input("Ingrese el valor de alpha: "))
        beta = float(input("Ingrese el valor de beta: "))
        valores: List[float] = generador_valores_gamma(alpha, beta, args.observaciones)
        print(valores)
    elif args.distribucion == distribuciones['normal'].label:
        mu = int(input("Ingrese el valor de mu: "))
        sigma = float(input("Ingrese el valor de sigma: "))
        valores: List[float] = generador_valores_normal(mu, sigma, args.observaciones)
        A = mu - 4 * sigma   # límite inferior
        B = mu + 4 * sigma   # límite superior
        accepted_points, rejected_points, intentos = rejection_sampling_normal(args.observaciones, mu, sigma, A, B)
        graficar_normal(accepted_points, rejected_points, intentos, mu, sigma, A, B)
    elif args.distribucion == distribuciones['empirica_discreta'].label:
        valores: List[int] = generador_valores_empirica_discreta(distribucion_empirica_discreta, args.observaciones)