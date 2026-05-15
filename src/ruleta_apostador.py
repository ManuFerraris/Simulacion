import argparse
import random
import matplotlib.pyplot as plt

def simular_apuestas(corridas, tiradas, estrategia, tipo_capital):
    # Diccionario de nombres para los gráficos
    nombres_estrategias = {
        'm': 'Martingala',
        'd': "D'Alembert",
        'f': 'Fibonacci',
        'o': 'Paroli (Martingala Inversa)'
    }
    
    capital_inicial = 1000 if tipo_capital == 'f' else 0
    apuesta_base = 10
    
    # Secuencia Fibonacci precalculada para la estrategia 'f'
    fib = [1, 1]
    for i in range(2, 50):
        fib.append(fib[i-1] + fib[i-2])

    fig, axs = plt.subplots(2, 1, figsize=(10, 10))
    fig.suptitle(f"Estrategia: {nombres_estrategias[estrategia]} - Capital: {'Finito' if tipo_capital == 'f' else 'Infinito'}")

    bancarrotas = 0

    for c in range(corridas):
        flujo_caja = [capital_inicial]
        capital_actual = capital_inicial
        apuesta_actual = apuesta_base
        indice_fib = 0

        for n in range(1, tiradas + 1):
            # Verificar bancarrota en capital finito
            if tipo_capital == 'f' and capital_actual < apuesta_actual:
                bancarrotas += 1
                # Rellenar el resto de las tiradas con el capital congelado
                flujo_caja.extend([capital_actual] * (tiradas - n + 1))
                break

            # Simulamos apostar a un color (18 números ganadores sobre 37)
            gano = random.randint(0, 36) != 0 and random.randint(1, 37) <= 18

            if gano:
                capital_actual += apuesta_actual
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
                capital_actual -= apuesta_actual
                # Ajuste de apuesta según estrategia (PIERDE)
                if estrategia == 'm':
                    apuesta_actual *= 2
                elif estrategia == 'd':
                    apuesta_actual += apuesta_base
                elif estrategia == 'f':
                    indice_fib += 1
                    apuesta_actual = apuesta_base * fib[indice_fib]
                elif estrategia == 'o': # Paroli
                    apuesta_actual = apuesta_base
            
            flujo_caja.append(capital_actual)

        eje_x = range(0, len(flujo_caja))
        
        # Graficar en el primer subplot solo si es la primera corrida
        if c == 0:
            axs[0].plot(eje_x, flujo_caja, color='blue', alpha=0.8)
            axs[0].set_title('Flujo de Caja - Corrida Individual')
            axs[0].set_xlabel('n (Número de tiradas)')
            axs[0].set_ylabel('fc (Flujo de caja)')
            axs[0].grid(True)

        # Graficar en el segundo subplot todas las corridas
        axs[1].plot(eje_x, flujo_caja, alpha=0.6)

    axs[1].set_title(f'Flujo de Caja - {corridas} Corridas Simultáneas (Bancarrotas: {bancarrotas})')
    axs[1].set_xlabel('n (Número de tiradas)')
    axs[1].set_ylabel('fc (Flujo de caja)')
    axs[1].grid(True)

    plt.subplots_adjust(top=0.90, bottom=0.1, hspace=0.4)
    
    # Exportar resultados
    output_file = f"estrategia_{estrategia}_capital_{tipo_capital}.png"
    plt.savefig(output_file)
    print(f"Gráfico generado: {output_file} | Bancarrotas totales: {bancarrotas}")
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="TP 1.2 - Estrategias de Apuestas")
    parser.add_argument('-c', '--corridas', type=int, required=True, help="Cantidad de corridas")
    parser.add_argument('-n', '--tiradas', type=int, required=True, help="Cantidad de tiradas")
    parser.add_argument('-e', '--elegido', type=int, default=0, help="Número elegido (opcional)")
    parser.add_argument('-s', '--estrategia', choices=['m', 'd', 'f', 'o'], required=True, help="m=Martingala, d=D'Alembert, f=Fibonacci, o=Paroli")
    parser.add_argument('-a', '--capital', choices=['i', 'f'], required=True, help="i=Infinito, f=Finito")

    args = parser.parse_args()

    simular_apuestas(args.corridas, args.tiradas, args.estrategia, args.capital)

if __name__ == "__main__":
    main()