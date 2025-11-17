import mesa
from .agentes import Individuo # ¡Importamos nuestra nueva clase Agente!

class ModeloAnisi(mesa.Model):
    """
    Versión "Agentificada" del Modelo Simple de Anisi (Cap. 24).
    """
    def __init__(self, G_a=500, z=50.0, w=10.0, z_b=5.0, 
                 T_i_total=2000, c=0.8, l=1.0, x=1.0, 
                 N=100, j=1.0):
        
        super().__init__()
        
        # Guardamos los parámetros exógenos
        self.G_a = G_a
        self.z = z
        self.w = w
        self.z_b = z_b
        self.T_i_total = T_i_total # Renombramos T_i para que sea "total"
        self.c = c
        self.l = l
        self.x = x
        self.N = N  # Número de agentes (Población)
        self.j = j  # Jornada de trabajo de mercado (horas por agente)

        # --- Cálculos globales (se hacen una vez) ---
        
        # L (Total horas de mercado necesarias) (Eq. 21.8)
        self.L = self.G_a / (self.z - self.w)
        
        # H (Puestos de trabajo de mercado disponibles) (Basado en Cap. 24)
        # H = L / j
        self.H_puestos = self.L / self.j
        
        # C_m (Consumo deseado TOTAL) (Eq. 21.9)
        self.C_m_total = self.c * self.T_i_total
        
        # C_m_agente (Consumo deseado POR AGENTE)
        self.C_m_agente = self.C_m_total / self.N
        
        # L_w_p (Tiempo Máximo Disponible TOTAL) (Eq. 21.21)
        self.L_w_p = self.T_i_total * (1 - self.c * (self.l / self.x))
        
        # --- Atributos de resultado (emergentes) ---
        self.L_w = 0    # Tiempo de trabajo TOTAL (emergente)
        self.I3 = 0     # Índice 13 (emergente)
        
        # --- Configuración de Agentes y Scheduler ---
        self.schedule = mesa.time.RandomActivation(self)
        
        for i in range(self.N):
            agente = Individuo(i, self)
            self.schedule.add(agente)

    def step(self):
        """
        Ejecuta un paso de la simulación.
        """
        
        # --- 1. Fase de Contratación (Lógica del Modelo) ---
        
        # Reseteamos a todos los agentes a "desempleados"
        for agente in self.schedule.agents:
            agente.esta_empleado_mercado = False
            
        # Redondeamos H a un número entero de puestos
        H_contratados = int(round(self.H_puestos, 0))
        
        # Seleccionamos N agentes al azar
        poblacion_barajada = self.random.sample(self.schedule.agents, self.N)
        
        # Contratamos a los primeros H
        for i in range(H_contratados):
            if i < len(poblacion_barajada): # Seguridad por si H > N
                poblacion_barajada[i].esta_empleado_mercado = True
        
        # --- 2. Fase de Acción (Lógica de los Agentes) ---
        self.schedule.step()
        
        # --- 3. Fase de Agregación (Resultados Emergentes) ---
        
        # Sumamos el trabajo total de TODOS los agentes
        self.L_w = sum([a.horas_trabajo_total for a in self.schedule.agents])
        
        # Calculamos el Índice I3 Emergente
        if self.L_w_p > 0:
            self.I3 = self.L_w / self.L_w_p
        else:
            self.I3 = float('inf')

        # --- Imprimir Resultados ---
        print("--- PASO DEL MODELO (AGENTIFICADO) ---")
        print(f"Puestos de Mercado (H): {self.H_puestos:.2f} (Contratados: {H_contratados})")
        print(f"L_w (Trabajo Total Emergente): {self.L_w:.2f}")
        print(f"L_w_p (Tiempo Máximo Disponible): {self.L_w_p:.2f}")
        print(f"ÍNDICE I3 (Emergente): {self.I3:.4f}")