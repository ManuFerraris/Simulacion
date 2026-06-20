"""
Definiciones externas para un sistema de colas de un solo servidor.
Traducción de ej_mm1.c a Python.
Propósito: Simular un sistema de colas M/M/1 para calcular estadísticas
como retardo promedio, número promedio en cola y utilización del servidor.
"""

import math
import sys
import argparse
from lcgrand import lcgrand


# ============================================================================
# CONSTANTES
# ============================================================================

Q_LIMIT = 100           # Límite en la longitud de la cola
BUSY = 1                # Mnemónico: servidor ocupado
IDLE = 0                # Mnemónico: servidor inactivo


# ============================================================================
# VARIABLES GLOBALES
# ============================================================================

# Variables de eventos y control
next_event_type = None                  # Tipo de próximo evento
num_events = None                       # Número total de eventos

# Contadores de clientes y demoras
num_custs_delayed = None                # Número de clientes con demora registrada
num_delays_required = None              # Número de demoras a simular
num_in_q = None                         # Número de clientes en cola

# Estado del servidor
server_status = None                    # Estado del servidor (BUSY o IDLE)

# Acumuladores de estadísticas de promedio de tiempo
area_num_in_q = None                    # Área bajo la función "número en cola"
area_server_status = None               # Área bajo la función "servidor ocupado"

# Parámetros de entrada
mean_interarrival = None                # Tiempo medio entre llegadas
mean_service = None                     # Tiempo medio de servicio

# Tiempo de simulación
sim_time = None                         # Tiempo de simulación actual
time_last_event = None                  # Tiempo del último evento

# Listas de eventos
time_arrival = [None] * (Q_LIMIT + 1)   # Tiempos de llegada de clientes en cola
time_next_event = [None] * 3            # Tiempos del próximo evento (índices 1 y 2)

# Acumulador de demoras
total_of_delays = None                  # Total acumulado de demoras




# ============================================================================
# FUNCIONES (Declaraciones)
# ============================================================================

def initialize():
    """
    Función de inicialización.
    Inicializa todas las variables globales y contadores estadísticos.
    """
    global sim_time, server_status, num_in_q, time_last_event, num_custs_delayed
    global total_of_delays, area_num_in_q, area_server_status, time_next_event
    
    # Initialize the simulation clock.
    sim_time = 0.0
    # Initialize the state variables.
    server_status = IDLE
    num_in_q = 0
    time_last_event = 0.0
    # Initialize the statistical counters.
    num_custs_delayed = 0
    total_of_delays = 0.0
    area_num_in_q = 0.0
    area_server_status = 0.0
    # Initialize event list. Since no customers are present, the departure
    # (service completion) event is eliminated from consideration.
    time_next_event[1] = sim_time + expon(mean_interarrival)
    time_next_event[2] = 1.0e+30


def timing():
    """
    Función de temporización.
    Determina el tipo de próximo evento a ocurrir y avanza el reloj de simulación.
    """
    global sim_time, next_event_type, time_next_event
    
    min_time_next_event = 1.0e+29
    next_event_type = 0
    
    # Determine the event type of the next event to occur.
    for i in range(1, num_events + 1):
        if time_next_event[i] < min_time_next_event:
            min_time_next_event = time_next_event[i]
            next_event_type = i
    
    # Check to see whether the event list is empty.
    if next_event_type == 0:
        # The event list is empty, so stop the simulation.
        print(f"\nEvent list empty at time {sim_time}")
        sys.exit(1)
    
    # The event list is not empty, so advance the simulation clock.
    sim_time = min_time_next_event


def arrive():
    """
    Arrival event function.
    Procesa la llegada de un cliente al sistema.
    """
    global sim_time, server_status, num_in_q, total_of_delays, num_custs_delayed
    global time_next_event, time_arrival
    
    float_delay = None
    # Schedule next arrival.
    time_next_event[1] = sim_time + expon(mean_interarrival)
    # Check to see whether server is busy.
    if server_status == BUSY:
        # Server is busy, so increment number of customers in queue.
        num_in_q += 1
        # Check to see whether an overflow condition exists.
        if num_in_q > Q_LIMIT:
            # The queue has overflowed, so stop the simulation.
            print(f"\nOverflow of the array time_arrival at time {sim_time}")
            sys.exit(2)
        # There is still room in the queue, so store the time of arrival of the
        # arriving customer at the (new) end of time_arrival.
        time_arrival[num_in_q] = sim_time
    else:
        # Server is idle, so arriving customer has a delay of zero. (The
        # following two statements are for program clarity and do not affect
        # the results of the simulation.)
        float_delay = 0.0
        total_of_delays += float_delay
        # Increment the number of customers delayed, and make server busy.
        num_custs_delayed += 1
        server_status = BUSY
        # Schedule a departure (service completion).
        time_next_event[2] = sim_time + expon(mean_service)


def depart():
    """
    Departure event function.
    Procesa la salida (finalización de servicio) de un cliente del sistema.
    """
    global sim_time, server_status, num_in_q, total_of_delays, num_custs_delayed
    global time_next_event, time_arrival
    
    delay = None
    # Check to see whether the queue is empty.
    if num_in_q == 0:
        # The queue is empty so make the server idle and eliminate the
        # departure (service completion) event from consideration.
        server_status = IDLE
        time_next_event[2] = 1.0e+30
    else:
        # The queue is nonempty, so decrement the number of customers in
        # queue.
        num_in_q -= 1
        # Compute the delay of the customer who is beginning service and update
        # the total delay accumulator.
        delay = sim_time - time_arrival[1]
        total_of_delays += delay
        # Increment the number of customers delayed, and schedule departure.
        num_custs_delayed += 1
        time_next_event[2] = sim_time + expon(mean_service)
        # Move each customer in queue (if any) up one place.
        for i in range(1, num_in_q + 1):
            time_arrival[i] = time_arrival[i + 1]


def report():
    """
    Función generadora de reportes.
    Calcula e imprime las medidas de desempeño deseadas.
    
    Compute and write estimates of desired measures of performance.
    """
    # Calcular promedio de delay en cola
    avg_delay = total_of_delays / num_custs_delayed
    
    # Calcular promedio de clientes en cola
    avg_num_in_q = area_num_in_q / sim_time
    
    # Calcular utilización del servidor
    server_util = area_server_status / sim_time
    
    # Escribir resultados con formato exacto como en C
    print(f"\n\nAverage delay in queue{avg_delay:11.3f} minutes\n")
    print(f"Average number in queue{avg_num_in_q:10.3f}\n")
    print(f"Server utilization{server_util:15.3f}\n")
    print(f"Time simulation ended{sim_time:12.3f} minutes")


def update_time_avg_stats():
    """
    Update area accumulators for time-average statistics.
    """
    global sim_time, time_last_event, num_in_q, area_num_in_q, server_status, area_server_status
    
    # Compute time since last event, and update last-event-time marker.
    time_since_last_event = sim_time - time_last_event
    time_last_event = sim_time
    # Update area under number-in-queue function.
    area_num_in_q += num_in_q * time_since_last_event
    # Update area under server-busy indicator function.
    area_server_status += server_status * time_since_last_event


def expon(mean):
    """Return an exponential random variate with mean "mean"."""
    return -mean * math.log(lcgrand(1))


def main():
    """
    Función principal.
    Controla el flujo general de la simulación.
    """
    global num_events, mean_interarrival, mean_service, num_delays_required
    global num_custs_delayed
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Simulador de sistema de colas M/M/1")
    parser.add_argument("-u", "--mean-interarrival", type=float, default=1.0,
                        help="Tiempo promedio entre llegadas (default: 1.0)")
    parser.add_argument("-s", "--mean-service", type=float, default=0.5,
                        help="Tiempo promedio de servicio (default: 0.5)")
    parser.add_argument("-c", "--customers", type=int, default=1000,
                        help="Número de clientes a simular (default: 1000)")
    
    args = parser.parse_args()
    
    # Assign parsed arguments to global variables
    mean_interarrival = args.mean_interarrival
    mean_service = args.mean_service
    num_delays_required = args.customers
    
    # Specify the number of events for the timing function.
    num_events = 2
    
    # Write report heading and input parameters.
    print("Single-server queueing system\n")
    print(f"Mean interarrival time{mean_interarrival:11.3f} minutes\n")
    print(f"Mean service time{mean_service:16.3f} minutes\n")
    print(f"Number of customers{num_delays_required:14d}\n")
    
    # Initialize the simulation.
    initialize()
    
    # Run the simulation while more delays are still needed.
    while num_custs_delayed < num_delays_required:
        # Determine the next event.
        timing()
        # Update time-average statistical accumulators.
        update_time_avg_stats()
        # Invoke the appropriate event function.
        if next_event_type == 1:
            arrive()
        elif next_event_type == 2:
            depart()
    
    # Invoke the report generator and end the simulation.
    report()


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    main()
