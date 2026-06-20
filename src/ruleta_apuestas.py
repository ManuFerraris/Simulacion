import argparse
import random
from datetime import datetime
from pathlib import Path
from unittest import case
import matplotlib.pyplot as plt
from typing import Dict, List, Literal

# Diccionario de nombres para los gráficos
nombres_estrategias: Dict[str, str] = {
    'm': 'Martingala',
    'd': "D'Alembert",
    'f': 'Fibonacci',
    'o': 'Paroli (Martingala Inversa)'
}
nombres_tipos_apuestas: Dict[str, str] = {
    'p': 'Pleno',
    'c': 'Color',
    'i': 'Par-Impar'
}

def simular_apuestas(
    corridas: int,
    tiradas: int,
    estrategia: Literal['m', 'd', 'f', 'o'],
    tipo_capital: Literal['i', 'f'],
    tipo_apuesta: Literal['p', 'c', 'i'],
    numero_elegido: int | None = None,
    color_elegido: str | None = None,
    par_elegido: str | None = None,
) -> None:
    """Simula múltiples corridas de apuestas y guarda gráficos en disco.

    Args:
        corridas: número de corridas simultáneas.
        tiradas: número de tiradas por corrida.
        estrategia: código de estrategia ('m','d','f','o').
        tipo_capital: 'i' infinito o 'f' finito.
        tipo_apuesta: tipo de apuesta ('p', 'c', 'i').
        numero_elegido: número elegido por el jugador (para incluir en el filename).
    """

    capital_inicial: float = 1000.0 if tipo_capital == 'f' else 0.0
    apuesta_base: float = 10.0

    # Secuencia Fibonacci precalculada para la estrategia 'f'
    fib: List[float] = [1.0, 1.0]
    for i in range(2, 50):
        fib.append(fib[i - 1] + fib[i - 2])

    fig, axs = plt.subplots(2, 1, figsize=(10, 10))
    fig.suptitle(
        f"Estrategia: {nombres_estrategias[estrategia]} - Capital: {'Finito' if tipo_capital == 'f' else 'Infinito'} - {"" if numero_elegido is None else f'Número: {numero_elegido} - '} {nombres_tipos_apuestas[tipo_apuesta]}",
    )

    bancarrotas: int = 0
    corridas_ganadas: int = 0
    todas_fr_relativas: List[List[float]] = []

    for c in range(corridas):
        flujo_caja: List[float] = [capital_inicial]
        fr_relativa_acumulada_corrida: List[float] = []
        tiradas_ganadas: int = 0
        capital_actual: float = capital_inicial
        apuesta_actual: float = apuesta_base
        indice_fib: int = 0

        for n in range(1, tiradas + 1):
            # Verificar bancarrota en capital finito
            if tipo_capital == 'f' and capital_actual < apuesta_actual:
                bancarrotas += 1
                # Rellenar el resto de las tiradas con el capital congelado
                flujo_caja.extend([capital_actual] * (tiradas - n + 1))
                # Rellenar el resto de fr_relativa_acumulada con el número de éxitos fijo y el denominador creciente
                fr_relativa_acumulada_corrida.extend(
                    [tiradas_ganadas / i for i in range(n, tiradas + 1)]
                )
                break

            ## Hacer variabe en funcion del tipo de apuesta (color, par/impar, etc.) y del número elegido
            resultado = random.randint(0, 36)            
            gano, monto = determinar_resultado(tipo_apuesta, resultado, numero_elegido, color_elegido, par_elegido, apuesta_actual)
            if gano:
                capital_actual += monto
                tiradas_ganadas += 1
                # Ajuste de apuesta según estrategia (GANA)
                if estrategia == 'm':
                    apuesta_actual = apuesta_base
                elif estrategia == 'd':
                    apuesta_actual = max(apuesta_base, apuesta_actual - apuesta_base)
                elif estrategia == 'f':
                    indice_fib = max(0, indice_fib - 2)
                    apuesta_actual = apuesta_base * fib[indice_fib]
                elif estrategia == 'o': # Paroli
                    apuesta_actual *= 2
            else:
                capital_actual += monto
                # Ajuste de apuesta según estrategia (PIERDE)
                if estrategia == 'm':
                    apuesta_actual *= 2
                elif estrategia == 'd':
                    apuesta_actual += apuesta_base
                elif estrategia == 'f':
                    indice_fib = min(indice_fib + 1, len(fib) - 1)
                    apuesta_actual = apuesta_base * fib[indice_fib]
                elif estrategia == 'o': # Paroli
                    apuesta_actual = apuesta_base

            fr_relativa_acumulada_corrida.append(tiradas_ganadas / n)
            flujo_caja.append(capital_actual)

        todas_fr_relativas.append(fr_relativa_acumulada_corrida)
        eje_x = range(0, len(flujo_caja))

        # Graficar en el segundo subplot todas las corridas
        axs[1].plot(eje_x, flujo_caja, alpha=0.6)
        if c >= 0 and flujo_caja[-1] > capital_inicial:
                    corridas_ganadas += 1

        # Graficar en el último subplot una linea de puntos en el capital inicial
        axs[1].axhline(y=capital_inicial, color='red', linestyle='--', label='Capital Inicial')
    
    # Graficar histograma de la frecuencia relativa acumulada en el primer subplot
    max_len: int = tiradas
    fr_promedio: List[float] = []
    for i in range(max_len):
        valores: List[float] = [fr[i] for fr in todas_fr_relativas]
        fr_promedio.append(sum(valores) / len(valores) if valores else 0.0)
    
    axs[0].bar(range(len(fr_promedio)), fr_promedio, color='blue', alpha=0.8, edgecolor='black')
    axs[0].set_title('Fr promedio de obtener la apuesta favorable')
    axs[0].set_xlabel('n (Número de tiradas)')
    axs[0].set_ylabel('fr (frecuencia relativa promedio)')
    axs[0].grid(True, alpha=0.3)
    
    axs[1].set_title(f'Flujo de Caja - {corridas} Corridas Simultáneas (Bancarrotas: {bancarrotas}, Ganadas: {corridas_ganadas}, Perdidas {corridas-corridas_ganadas})')
    axs[1].set_xlabel('n (Número de tiradas)')
    axs[1].set_ylabel('fc (Flujo de caja)')
    axs[1].grid(True)

    plt.subplots_adjust(top=0.90, bottom=0.1, hspace=0.4)

    # Preparar directorio y nombre descriptivo (sin caracteres inválidos en Windows)
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    output_dir = project_root / 'results' / 'plots'
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = get_filename(tipo_apuesta, corridas, tiradas, numero_elegido, estrategia, tipo_capital)
    output_path = output_dir / filename

    plt.savefig(output_path)
    print(f"Gráfico generado: {output_path} | Bancarrotas totales: {bancarrotas} | Ganadas: {corridas_ganadas}")
    plt.show()

def main() -> None:
    parser = argparse.ArgumentParser(description="TP 1.2 - Estrategias de Apuestas")
    parser.add_argument('-c', '--corridas', type=int, required=True, help="Cantidad de corridas")
    parser.add_argument('-n', '--tiradas', type=int, required=True, help="Cantidad de tiradas")
    parser.add_argument('-t', '--tipo_apuesta', type=str, required=True, help="Tipo de apuesta", choices=['p', 'c', 'i'])
    parser.add_argument('-s', '--estrategia', choices=['m', 'd', 'f', 'o'], required=True, help="m=Martingala, d=D'Alembert, f=Fibonacci, o=Paroli")
    parser.add_argument('-a', '--capital', choices=['i', 'f'], required=True, help="i=Infinito, f=Finito")

    args = parser.parse_args()

    numero_elegido = None;
    color_elegido = None;
    par_elegido = None;
    match args.tipo_apuesta:
        case 'c':
            print("Tipo de apuesta seleccionado: Color")
            color = input("Ingrese color (r/n): ").lower()

            if color in ["r", "n"]:
                print(f"Apostaste al color {'Rojo' if color == 'r' else 'Negro'}")
            else:
                print("Color inválido")

            color_elegido = color
        case 'p':
            print("Tipo de apuesta seleccionado: Pleno")
            numero = input("Ingrese número (0-36): ")
            if numero.isdigit() and 0 <= int(numero) <= 36:
                print(f"Apostaste al número {numero}")
            else:
                print("Número inválido")
            numero_elegido = int(numero)
        case 'i':            
            print("Tipo de apuesta seleccionado: Par/Impar")
            par_impar = input("Ingrese par/impar (p/i): ").lower()
            if par_impar in ["p", "i"]:
                print(f"Apostaste al {'Par' if par_impar == 'p' else 'Impar'}")
            else:
                print("Valor inválido")
        
    args = parser.parse_args()

    simular_apuestas(args.corridas, args.tiradas, args.estrategia, args.capital, args.tipo_apuesta, numero_elegido, color_elegido, par_elegido)

# retorna una tupla con el resultado de la apuesta (gana o pierde) y el monto ganado o perdido
def determinar_resultado(tipo_apuesta: Literal['p', 'c', 'i'], resultado: int, numero_elegido: int | None, color_elegido: str | None, par_elegido: str | None, apuesta_actual: float) -> tuple[bool, float]:
    match tipo_apuesta:
        case 'c': # Color
            resultado = (color_elegido == 'r' and resultado in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]) or (color_elegido == 'n' and resultado in [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35])
            return (resultado, apuesta_actual if resultado else -apuesta_actual)
        case 'p': # Pleno
            return (resultado == numero_elegido, 35.0 * apuesta_actual if resultado == numero_elegido else -apuesta_actual)
        case 'i': # Par/Impar
            if resultado == 0:
                return False, -apuesta_actual
            elif par_elegido == 'p':
                return resultado % 2 == 0, apuesta_actual if resultado % 2 == 0 else -apuesta_actual
            else:
                return resultado % 2 == 1, apuesta_actual if resultado % 2 == 1 else -apuesta_actual

def get_filename(tipo_apuesta: str | None, corridas: int, tiradas: int, numero_elegido: int | None, estrategia: str, tipo_capital: str) -> str:
    timestamp: str = datetime.now().strftime('%d-%m-%y-%H-%M-%S')
    return  f"ejecucion-apuesta-{timestamp}-{nombres_tipos_apuestas.get(tipo_apuesta, 'Desconocido')}-c{corridas}-n{tiradas}-s{nombres_estrategias[estrategia]}-a{tipo_capital}-{"" if numero_elegido is None else f'e{numero_elegido}'}.png"


if __name__ == "__main__":
    main()