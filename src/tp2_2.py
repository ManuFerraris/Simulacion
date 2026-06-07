import argparse
import random
from typing import Dict, List

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

def generador_valores_uniforme(a: float, b: float, n: int):
    """    
    1. SUBROUTINE UNIFORM (A,B,X)
    2. R = RND (R)
    3. X= A+(B-A)*R
    3. RETURN
    """
    r = [random.random() for _ in range(n)]
    x: List[float] = [a + (b - a) * r_i for r_i in r]
    return x

def generador_valores_exponencial(lambda_param, n):
    pass

def generador_valores_gamma(alpha, beta, n):
    pass

def generador_valores_normal(mu, sigma, n):
    pass

def generador_valores_pascal(r, p, n):
    pass

def generador_valores_binomial(n, p, n_samples):
    pass

def generador_valores_hipergeometrica(N, K, n, n_samples):
    pass

def generador_valores_poisson(lambda_param, n):
    pass

def generador_valores_empirica_discreta(probabilidades, n):
    pass

if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument('-d', '--distribucion', choices=list([d.label for d in distribuciones.values()]), required=True, help="Distribución de probabilidad a utilizar")
    parser.add_argument('-n', '--observaciones', type=int, required=True, help="Número de observaciones a generar")
    
    args: argparse.Namespace = parser.parse_args()
    if(args.distribucion == distribuciones['uniforme'].label):
        a = float(input("Ingrese el valor de a: "))
        b = float(input("Ingrese el valor de b: "))
        valores = generador_valores_uniforme(a, b, args.observaciones)
        print(valores)
