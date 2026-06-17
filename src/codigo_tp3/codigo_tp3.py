import simpy
import random
import statistics
from collections import Counter

class SimuladorMM1:
    def __init__(self, lambd, mu, capacidad_cola, tiempo_simulacion):
        self.lambd = lambd
        self.mu = mu
        self.capacidad_cola = capacidad_cola
        self.tiempo_simulacion = tiempo_simulacion
        
        self.tiempos_en_sistema = []
        self.tiempos_en_cola = []
        self.clientes_atendidos = 0
        self.clientes_rechazados = 0
        self.total_clientes_llegados = 0
        
        self.historial_longitud_cola = []
        self.historial_longitud_sistema = []
        
        self.env = simpy.Environment()
        self.servidor = simpy.Resource(self.env, capacity=1)

    def generar_clientes(self):
        id_cliente = 0
        while True:
            tiempo_entre_llegadas = random.expovariate(self.lambd)
            yield self.env.timeout(tiempo_entre_llegadas)
            
            id_cliente += 1
            self.total_clientes_llegados += 1
            self.registrar_estado()
            
            if self.capacidad_cola is None or len(self.servidor.put_queue) < self.capacidad_cola:
                self.env.process(self.atender_cliente(id_cliente))
            else:
                self.clientes_rechazados += 1

    def atender_cliente(self, id_cliente):
        hora_llegada = self.env.now
        
        with self.servidor.request() as peticion:
            yield peticion 
            
            hora_inicio_servicio = self.env.now
            tiempo_esperado_en_cola = hora_inicio_servicio - hora_llegada
            self.tiempos_en_cola.append(tiempo_esperado_en_cola)
            
            tiempo_servicio = random.expovariate(self.mu)
            yield self.env.timeout(tiempo_servicio)
            
            hora_salida = self.env.now
            tiempo_total_en_sistema = hora_salida - hora_llegada
            self.tiempos_en_sistema.append(tiempo_total_en_sistema)
            self.clientes_atendidos += 1

    def registrar_estado(self):
        longitud_cola = len(self.servidor.put_queue)
        longitud_sistema = longitud_cola + self.servidor.count
        
        self.historial_longitud_cola.append((self.env.now, longitud_cola))
        self.historial_longitud_sistema.append((self.env.now, longitud_sistema))

    def ejecutar(self):
        self.env.process(self.generar_clientes())
        self.env.run(until=self.tiempo_simulacion)
        return self.calcular_estadisticas()

    def calcular_estadisticas(self):
        L = statistics.mean([x[1] for x in self.historial_longitud_sistema]) if self.historial_longitud_sistema else 0
        Lq = statistics.mean([x[1] for x in self.historial_longitud_cola]) if self.historial_longitud_cola else 0
        W = statistics.mean(self.tiempos_en_sistema) if self.tiempos_en_sistema else 0
        Wq = statistics.mean(self.tiempos_en_cola) if self.tiempos_en_cola else 0
        
        tiempo_total_ocupado = sum([t_sys - t_cola for t_sys, t_cola in zip(self.tiempos_en_sistema, self.tiempos_en_cola)])
        utilizacion = tiempo_total_ocupado / self.tiempo_simulacion
        
        prob_rechazo = (self.clientes_rechazados / self.total_clientes_llegados) if self.total_clientes_llegados > 0 else 0
        
        cantidades_cola = [x[1] for x in self.historial_longitud_cola]
        conteo_cola = Counter(cantidades_cola)
        total_muestras = len(cantidades_cola)
        prob_n_cola = {n: round(count/total_muestras, 4) for n, count in conteo_cola.items()}

        # ¡Acá estaba el error! Ahora las claves son cortas y coinciden con las del print.
        return {
            "L": round(L, 4),
            "Lq": round(Lq, 4),
            "W": round(W, 4),
            "Wq": round(Wq, 4),
            "Utilizacion": round(utilizacion, 4),
            "Prob_Rechazo": round(prob_rechazo * 100, 2),
            "Prob_n_cola": prob_n_cola
        }

# ================================================================
# --- BLOQUE DE EJECUCIÓN PARA TODOS LOS ESCENARIOS DEL TP ---
# ================================================================
if __name__ == "__main__":
    MU = 10 
    TIEMPO_SIM = 1000 
    lambdas = [2.5, 5.0, 7.5, 10.0, 12.5]
    
    print("==========================================================")
    print("--- RESULTADOS SIMULACIÓN COLA INFINITA ---")
    print("==========================================================")
    for l in lambdas:
        # random.seed(42) # Opcional: Descomentar para tener siempre los mismos resultados exactos
        sim = SimuladorMM1(lambd=l, mu=MU, capacidad_cola=None, tiempo_simulacion=TIEMPO_SIM)
        stats = sim.ejecutar()
        print(f"Lambda={l:04.1f} (rho={l/MU:.2f}) | L={stats['L']:06.2f} | Lq={stats['Lq']:06.2f} | W={stats['W']:06.2f} | Wq={stats['Wq']:06.2f} | Util={stats['Utilizacion']*100:05.1f}%")

    # Tamaños de cola a evaluar: 0, 2, 5, 10, 50
    tamanos_cola = [0, 2, 5, 10, 50]

    for capacidad in tamanos_cola:
        print(f"\n==========================================================")
        print(f"--- RESULTADOS SIMULACIÓN COLA FINITA (Tamaño cola = {capacidad}) ---")
        print(f"==========================================================")
        for l in lambdas:
            # random.seed(42) # Opcional: Descomentar para tener siempre los mismos resultados exactos
            sim = SimuladorMM1(lambd=l, mu=MU, capacidad_cola=capacidad, tiempo_simulacion=TIEMPO_SIM)
            stats = sim.ejecutar()
            print(f"Lambda={l:04.1f} (rho={l/MU:.2f}) | L={stats['L']:06.2f} | Lq={stats['Lq']:06.2f} | W={stats['W']:06.2f} | Wq={stats['Wq']:06.2f} | Rechazos={stats['Prob_Rechazo']:05.2f}%")