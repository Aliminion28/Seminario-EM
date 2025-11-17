import mesa

class ModeloAnisi(mesa.Model):
    """
    Un modelo ABM que implementa el 'Modelo Simple' de Anisi (Cap. 21).
    """
    def __init__(self, G_a=500, z=50.0, w=10.0, z_b=5.0, T_i=2000, c=0.8, l=1.0, x=1.0):
        """
        Inicializa el modelo con todas las variables exógenas de Anisi.
        """
        super().__init__()
        
        # Guardamos los parámetros exógenos
        self.G_a = G_a  # Gasto autónomo
        self.z = z      # Productividad trabajo de mercado
        self.w = w      # Salario real
        self.z_b = z_b  # Productividad trabajo extramercado
        self.T_i = T_i  # Tiempo total disponible
        self.c = c      # Necesidad de consumo por hora
        self.l = l      # Grado de incompatibilidad
        self.x = x      # Intensidad del consumo
        
        # Preparamos atributos para guardar los resultados
        self.L = 0      # Tiempo de trabajo de mercado (Eq. 21.8)
        self.L_b = 0    # Tiempo de trabajo extramercado (Eq. 21.13)
        self.L_w = 0    # Tiempo de trabajo TOTAL (Eq. 21.14)
        self.L_w_p = 0  # Tiempo de no consumo (Eq. 21.21)
        self.I3 = 0     # Índice 13 (Eq. 21.22)

    def step(self):
        """
        Ejecuta un paso de la simulación.
        En este modelo, todo se calcula en un solo paso.
        """
        
        # --- CASO 1: Calcular L ---
        # Ecuación (21.8) del libro de Anisi
        self.L = self.G_a / (self.z - self.w)
        
        # --- CASO 2: Resto de cálculos del Cap. 21 ---
        
        # Consumo deseado total (Eq. 21.9)
        C_m = self.c * self.T_i
        
        # Consumo obtenido del mercado (Masa Salarial, Eq. 21.12)
        MS = self.w * self.L
        
        # Tiempo de trabajo extramercado (Eq. 21.13)
        # (Aseguramos que no sea negativo si el mercado da más de lo deseado)
        consumo_faltante = C_m - MS
        self.L_b = max(0, consumo_faltante / self.z_b)
        
        # Tiempo de trabajo TOTAL (Eq. 21.14)
        self.L_w = self.L + self.L_b
        
        # Tiempo de NO consumo exclusivo (Eq. 21.21)
        # (El tiempo máximo disponible para trabajar)
        self.L_w_p = self.T_i * (1 - self.c * (self.l / self.x))
        
        # --- Índice Clave: I3 (Eq. 21.22) ---
        # El ratio entre el trabajo necesario y el trabajo posible
        if self.L_w_p > 0: # Evitar división por cero
            self.I3 = self.L_w / self.L_w_p
        else:
            self.I3 = float('inf') # Caso extremo de frustración
        
        print("--- PASO DEL MODELO COMPLETO ---")
        print(f"L (Mercado): {self.L:.2f}")
        print(f"L_b (Extra-Mercado): {self.L_b:.2f}")
        print(f"L_w (Trabajo Total Necesario): {self.L_w:.2f}")
        print(f"L_w_p (Tiempo Máximo Disponible): {self.L_w_p:.2f}")
        print(f"ÍndICE I3 (Ratio): {self.I3:.4f}")