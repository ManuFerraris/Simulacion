import argparse
from typing import Dict, List

# Consignas de desarrollo
# Elaborar un programa por cada distribución de probabilidad en lenguaje Python 3.x.
# Testear la generación de valores de la forma más conveniente para cada caso (queda a criterio del grupo el como testear). # -- como adicional, yo, compararía contra alguna librería que genere esos valores.

class Distribucion: 
    def __init__(self, nombre: str, label: str):
        self.nombre = nombre
        self.label = label

distribuciones: Dict[str, Distribucion] = {
    'uniforme': Distribucion(nombre='Distribución Uniforme', label='uniforme'),
    'exponencial': Distribucion(nombre='Distribución Exponencial', label='exponencial'),
    'gamma': Distribucion(nombre='Distribución Gamma', label='gamma'),
    'normal': Distribucion(nombre='Distribución Normal', label='normal'),
    'pascal': Distribucion(nombre='Distribución Pascal', label='pascal'),
    'binomial': Distribucion(nombre='Distribución Binomial', label='binomial'),
    'hipergeometrica': Distribucion(nombre='Distribución Hipergeométrica', label='hipergeometrica'),
    'poisson': Distribucion(nombre='Distribución Poisson', label='poisson'),
    'empirica_discreta': Distribucion(nombre='Distribución Empírica Discreta', label='empirica_discreta')
}




## IMPORTANTE 
## los argumentos los generó COPILOT, no aseguro que estén bien.
## Se deben revisar las definiciones teóricas de cada distribución

def generador_valores_uniforme(a, b, n):
    pass

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
