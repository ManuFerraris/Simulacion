from collections import defaultdict
import os
import simpy
import random
import statistics
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import List, Dict, Optional

# ==============================================================================
# 1. CLASE PRINCIPAL DEL MODELO M/M/1
# ==============================================================================
class SimuladorMM1:
    def __init__(self, env, lambd, mu, capacidad_cola=None):
        self.env = env
        self.lambd = lambd
        self.mu = mu
        
        if capacidad_cola is not None:
            self.capacidad_sistema = capacidad_cola + 1
        else:
            self.capacidad_sistema = float('inf')
        
        self.servidor = simpy.Resource(env, capacity=1)
        
        self.ultimo_cambio_tiempo = 0.0
        self.area_sistema = 0.0
        self.area_cola = 0.0
        self.area_servidor = 0.0
        
        self.tiempos_en_sistema = []
        self.tiempos_en_cola = []
        self.total_llegadas = 0
        self.total_rechazos = 0

        self.tiempo_en_estado_cola: Dict[int, float] = defaultdict(float)

    def actualizar_areas(self):
        ahora = self.env.now
        duracion = ahora - self.ultimo_cambio_tiempo
        
        if duracion > 0:
            en_cola = len(self.servidor.queue)
            en_servidor = len(self.servidor.users)
            en_sistema = en_cola + en_servidor
            
            self.area_sistema += en_sistema * duracion
            self.area_cola += en_cola * duracion
            self.area_servidor += en_servidor * duracion
            
            self.tiempo_en_estado_cola[en_cola] += duracion

        self.ultimo_cambio_tiempo = ahora

    def generar_clientes(self):
        while True:
            tiempo_entre_llegadas = random.expovariate(self.lambd)
            yield self.env.timeout(tiempo_entre_llegadas)
            
            self.total_llegadas += 1
            
            en_cola = len(self.servidor.queue)
            en_servidor = len(self.servidor.users)
            
            if (en_cola + en_servidor) < self.capacidad_sistema:
                self.env.process(self.atender_cliente())
            else:
                self.total_rechazos += 1

    def atender_cliente(self):
        hora_llegada = self.env.now
        self.actualizar_areas()
        
        peticion = self.servidor.request()
        yield peticion
        
        self.actualizar_areas()
        self.tiempos_en_cola.append(self.env.now - hora_llegada)
        
        tiempo_servicio = random.expovariate(self.mu)
        yield self.env.timeout(tiempo_servicio)
        
        self.actualizar_areas()
        self.tiempos_en_sistema.append(self.env.now - hora_llegada)
        
        self.servidor.release(peticion)
        self.actualizar_areas()

# ==============================================================================
# 2. FUNCIÓN PARA CORRER LAS 30 CORRIDAS INDEPENDIENTES
# ==============================================================================
def correr_experimento_mm1(lambd, mu, capacidad_cola, num_corridas=30, tiempo_sim=2500):
    resultados_L = []
    resultados_Lq = []
    resultados_W = []
    resultados_Wq = []
    resultados_Util = []
    resultados_Rechazo = []
    suma_prob_n: Dict[int, float] = defaultdict(float)

    for i in range(num_corridas):
        random.seed(500 + i) 
        
        env = simpy.Environment()
        sim = SimuladorMM1(env, lambd, mu, capacidad_cola)
        
        env.process(sim.generar_clientes())
        env.run(until=tiempo_sim)
        
        sim.actualizar_areas()
        t_final = env.now
        
        resultados_L.append(sim.area_sistema / t_final)
        resultados_Lq.append(sim.area_cola / t_final)
        
        resultados_W.append(statistics.mean(sim.tiempos_en_sistema) if sim.tiempos_en_sistema else 0)
        resultados_Wq.append(statistics.mean(sim.tiempos_en_cola) if sim.tiempos_en_cola else 0)
        resultados_Util.append(sim.area_servidor / t_final)
        resultados_Rechazo.append((sim.total_rechazos / sim.total_llegadas * 100) if sim.total_llegadas > 0 else 0)

        for n, tiempo_en_n in sim.tiempo_en_estado_cola.items():
            prob_n_esta_corrida = tiempo_en_n / t_final
            suma_prob_n[n] += prob_n_esta_corrida
    
    prob_n_promedio = {n: suma / num_corridas for n, suma in suma_prob_n.items()}
    
    return {
        "L": statistics.mean(resultados_L),
        "Lq": statistics.mean(resultados_Lq),
        "W": statistics.mean(resultados_W),
        "Wq": statistics.mean(resultados_Wq),
        "Utilizacion": statistics.mean(resultados_Util),
        "Rechazo": statistics.mean(resultados_Rechazo),
        "Prob_n_cola": prob_n_promedio,
    }

def graficar_prob_n_cola_por_tasa(
    lista_resultados_infinita: List[Dict],
    mu: float,
    figsize: tuple[float, float] = (8, 5),
    guardar_en: Optional[str] = None,
    mostrar: bool = False,
    max_barras: int = 30,
) -> List[plt.Figure]:
    """
    Genera una figure (ventana) independiente por cada tasa de arribo simulada,
    comparando la distribución de probabilidad de n clientes en cola
    SIMULADA (histograma azul) contra la TEÓRICA (histograma naranja),
    usando la fórmula M/M/1: P(n) = (1 - rho) * rho^n.

    Args:
        lista_resultados_infinita: lista de diccionarios de resultados, uno por
            cada tasa de arribo simulada. Cada diccionario debe contener al menos:
                - "Prob_n_cola": Dict[int, float]  -> P(n) simulada por cada n
                - "lambda": float                   -> tasa de arribo (lambda) usada
                - "tasa_pct": float                 -> proporción respecto a mu (ej. 0.75)
            (Esta es exactamente la estructura que devuelve correr_experimento_mm1
            una vez agregado el campo "Prob_n_cola", más "lambda" y "tasa_pct".)
        mu: tasa de servicio utilizada en las corridas (para calcular rho = lambda/mu).
        figsize: tamaño (ancho, alto) en pulgadas de cada figura individual.
        guardar_en: si se especifica una ruta de carpeta, cada figura se exporta
            como PNG dentro de esa carpeta (se crea si no existe). Si es None,
            no se guarda nada en disco.
        mostrar: si es True, llama a plt.show() al final para desplegar todas
            las ventanas generadas. Si es False, no muestra (útil si solo se
            quiere guardar a disco sin abrir ventanas, por ejemplo en un script
            batch).

    Returns:
        Lista de objetos Figure de matplotlib, uno por cada tasa de arribo,
        en el mismo orden que lista_resultados_infinita. Útil si se quiere
        manipular o guardar cada figura manualmente después de llamar a la función.
    """
    if guardar_en is not None:
        os.makedirs(guardar_en, exist_ok=True)

    figures: List[plt.Figure] = []

    for res in lista_resultados_infinita:
        prob_n_cola: Dict[int, float] = res["Prob_n_cola"]
        lambd: float = res["lambda"]
        tasa_pct: float = res["tasa_pct"]
        rho: float = lambd / mu

        n_max = max(prob_n_cola.keys()) if prob_n_cola else 0
        cantidad_valores_n = n_max + 1  # cantidad de enteros en [0, n_max]

        fig, ax = plt.subplots(figsize=figsize)

        if cantidad_valores_n <= max_barras:
            # --- CASO CHICO: una barra por cada n, igual que antes ---
            ns = list(range(n_max + 1))
            prob_simulada = [prob_n_cola.get(n, 0.0) for n in ns]

            ancho = 0.4
            ax.bar(
                [n - ancho / 2 for n in ns], prob_simulada, width=ancho,
                label="Simulado", color="steelblue", edgecolor="black",
            )

            if rho < 1:
                prob_teorica = [(1 - rho) * (rho ** n) for n in ns]
                ax.bar(
                    [n + ancho / 2 for n in ns], prob_teorica, width=ancho,
                    label="Teórico", color="orange", edgecolor="black", alpha=0.8,
                )

            ax.set_xticks(ns)
            ax.set_xlabel("n (clientes en cola)")

        else:
            # --- CASO GRANDE: agrupar en bins de tamaño uniforme ---
            tam_bin = max(1, -(-cantidad_valores_n // max_barras))  # ceil division
            n_bins = -(-cantidad_valores_n // tam_bin)  # ceil division

            bin_centros = []
            bin_etiquetas = []
            prob_simulada_bin = []
            prob_teorica_bin = []

            for b in range(n_bins):
                n_inicio = b * tam_bin
                n_fin = min(n_inicio + tam_bin - 1, n_max)

                # Suma de probabilidad simulada de todos los n dentro del bin
                suma_sim = sum(prob_n_cola.get(n, 0.0) for n in range(n_inicio, n_fin + 1))
                prob_simulada_bin.append(suma_sim)

                if rho < 1:
                    suma_teo = sum((1 - rho) * (rho ** n) for n in range(n_inicio, n_fin + 1))
                    prob_teorica_bin.append(suma_teo)

                bin_centros.append(b)
                bin_etiquetas.append(f"{n_inicio}" if n_inicio == n_fin else f"{n_inicio}-{n_fin}")

            ancho = 0.4
            ax.bar(
                [b - ancho / 2 for b in bin_centros], prob_simulada_bin, width=ancho,
                label="Simulado", color="steelblue", edgecolor="black",
            )

            if rho < 1:
                ax.bar(
                    [b + ancho / 2 for b in bin_centros], prob_teorica_bin, width=ancho,
                    label="Teórico", color="orange", edgecolor="black", alpha=0.8,
                )

            # Mostrar solo algunas etiquetas de bin si hay muchas, para no saturar
            paso_etiquetas = max(1, len(bin_centros) // 15)
            ax.set_xticks(bin_centros[::paso_etiquetas])
            ax.set_xticklabels(bin_etiquetas[::paso_etiquetas], rotation=45, ha="right", fontsize=7)
            ax.set_xlabel(f"n (clientes en cola, agrupado de a {tam_bin})")

        if rho >= 1:
            ax.text(
                0.02, 0.95,
                "ρ ≥ 1: sistema inestable\n(sin distribución estacionaria teórica)",
                transform=ax.transAxes, ha="left", va="top",
                fontsize=9, color="red", style="italic",
            )

        ax.set_title(f"Probabilidad de n clientes en cola\nTasa de arribo: {tasa_pct*100:.0f}%  (ρ = {rho:.2f}, n_max observado = {n_max})")
        ax.set_ylabel("P(n)")
        ax.legend(fontsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        fig.tight_layout()

        if guardar_en is not None:
            nombre_archivo = f"prob_n_cola_tasa_{int(tasa_pct*100)}pct.png"
            ruta_completa = os.path.join(guardar_en, nombre_archivo)
            fig.savefig(ruta_completa, dpi=150)

        figures.append(fig)

    if mostrar:
        plt.show()

    return figures
# ==============================================================================
# 3. BLOQUE DE EJECUCIÓN CON GENERACIÓN DE GRÁFICOS
# ==============================================================================
if __name__ == "__main__":
    print("--- SIMULADOR DE COLAS M/M/1 INTERACTIVO ---")
    MU = float(input("Ingrese la tasa de servicio MU (ej. 10 clientes por unidad de tiempo): "))
    tiempo_sim_input = input("Ingrese el tiempo de simulación (default 2500 unidades de tiempo): ")
    tiempo_sim = 2500.0 if tiempo_sim_input == "" else float(tiempo_sim_input)
    variacion_tasas_arribo = [0.25, 0.50, 0.75, 1.00, 1.25]

    # Listas para guardar datos que van a los gráficos
    lista_resultados_infinita = []  # uno por cada tasa (25%, 50%, 75%, 100%, 125%)
    lista_lambdas = []
    lista_Lq = []
    lista_Wq = []
    
    print("\nEjecutando experimentos para Cola Infinita variando tasas...")
    for t in variacion_tasas_arribo:
        LAMBDA = MU * t
        res = correr_experimento_mm1(lambd=LAMBDA, mu=MU, capacidad_cola=None, tiempo_sim=tiempo_sim)
        
        lista_lambdas.append(f"{t*100}%")
        lista_Lq.append(res['Lq'])
        lista_Wq.append(res['Wq'])
        
        res["tasa_pct"] = t          # guardamos la tasa para el título del subplot
        res["lambda"] = LAMBDA
        lista_resultados_infinita.append(res)


        print(f"\nTasas de arribo al {t*100}% de tasa de servicio -> Lambda = {LAMBDA}")
        print(f"  - Promedio de clientes en sistema (L): {res['L']:.4f}")
        print(f"  - Promedio de clientes en cola (Lq): {res['Lq']:.4f}")
        print(f"  - Tiempo promedio en cola (Wq): {res['Wq']:.4f}")
        print(f"  - Tiempo promedio en sistema (W): {res['W']:.4f}")
        print(f"  - Utilización del servidor: {res['Utilizacion']*100:.2f}%")

    # Guardar datos para el segundo gráfico (Cola Finita)
    capacidades_cola = [0, 2, 5, 10, 50]
    resultados_finita: Dict[float, Dict[int, float]] = {}

    print("\n-------------------------------------------------------------")
    print("Ejecutando experimentos para Cola Finita (Denegación de servicio)...")
    for t in variacion_tasas_arribo:
        LAMBDA = MU * t
        resultados_finita[t] = {}
        for cap in capacidades_cola:
            res = correr_experimento_mm1(lambd=LAMBDA, mu=MU, capacidad_cola=cap, tiempo_sim=tiempo_sim)
            resultados_finita[t][cap] = res['Rechazo']
            print(f"\n  rho={t:.2f} | Capacidad={cap:>3} | Rechazo={res['Rechazo']:.2f}%")
            print(f"  - Promedio de clientes en sistema (L): {res['L']:.4f}")
            print(f"  - Promedio de clientes en cola (Lq): {res['Lq']:.4f}")
            print(f"  - Tiempo promedio en cola (Wq): {res['Wq']:.4f}")
            print(f"  - Tiempo promedio en sistema (W): {res['W']:.4f}")
            print(f"  - Utilización del servidor: {res['Utilizacion']*100:.2f}%")
    
    print("\n[INFO] Generando gráficos... Cerrá las ventanas para finalizar el programa.")

    # --- GRÁFICO 1: Comportamiento de la cola (Infinita) ---
    plt.figure(figsize=(10, 5))
    
    # Subgráfico izquierdo: Clientes en cola
    plt.subplot(1, 2, 1)
    plt.plot(lista_lambdas, lista_Lq, marker='o', color='blue', linewidth=2)
    plt.title("Clientes Promedio en Cola (Lq)")
    plt.xlabel("Tasa de Arribos (% de Mu)")
    plt.ylabel("Clientes")
    plt.grid(True)
    
    # Subgráfico derecho: Tiempo en cola
    plt.subplot(1, 2, 2)
    plt.plot(lista_lambdas, lista_Wq, marker='s', color='red', linewidth=2)
    plt.title("Tiempo Promedio en Cola (Wq)")
    plt.xlabel("Tasa de Arribos (% de Mu)")
    plt.ylabel("Tiempo de espera")
    plt.grid(True)
    
    plt.tight_layout()
    
    # --- GRÁFICO Denegación de Servicio en funcion de capacidad de cola (Finita) ---
    plt.figure(figsize=(8, 5))
    for t in variacion_tasas_arribo:
        rechazos = [resultados_finita[t][cap] for cap in capacidades_cola]
        plt.plot(capacidades_cola, rechazos, marker='o', label=f"ρ={t:.2f}")

    plt.title("Probabilidad de Rechazo vs Capacidad de Cola, por nivel de carga")
    plt.xlabel("Capacidad máxima de la cola")
    plt.ylabel("% de Clientes Rechazados")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()    
    
    # --- GRÁFICO probabilidad N clientes en cola
    graficar_prob_n_cola_por_tasa(
        lista_resultados_infinita=lista_resultados_infinita,
        mu=MU,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # deja espacio para el suptitle    
    
    # Mostrar gráficos en pantalla
    plt.show()