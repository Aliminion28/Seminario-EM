import mesa
import numpy as np

# --- AGENTE 1: ADMINISTRACIÓN PÚBLICA ---
class AdminPublica(mesa.Agent):
    """
    Representa al Estado. Fija las reglas del juego macroeconómico.
    Controla: Gasto Autónomo (Ga), Impuestos (t) y Jornada Legal (j).
    """
    def __init__(self, unique_id, model, G_a, t, j):
        super().__init__(model)
        self.unique_id = unique_id
        
        # Variables de control estatal
        self.G_a = G_a  # Presupuesto de Gasto Público    
        self.t = t      # Tipo impositivo    
        self.j = j      # Jornada laboral legal    

    def step(self):
        pass


# --- AGENTE 2: EMPRESA ---
class Empresa(mesa.Agent):
    """
    Produce bienes y contrata trabajadores.
    Controla: Productividad (z), Salario (w) y Demanda de Trabajo.
    """
    def __init__(self, unique_id, model, z_media, z_std, w_media, w_std):
        super().__init__(model)
        self.unique_id = unique_id
        
        # Productividad de mercado (z)    
        self.z = np.random.normal(z_media, z_std)
        
        # Salario real por hora (w)    
        w_provisional = np.random.normal(w_media, w_std)
        # Aseguramos que el salario sea positivo y menor que la productividad
        self.w = max(1.0, min(w_provisional, self.z - 1.0)) 
        
        # Estado
        self.trabajadores_contratados = 0
        self.demanda_trabajo = 0

    def calcular_demanda(self, G_a_total, num_empresas):
        """
        Calcula la Demanda de Trabajo L (en horas) basada en el multiplicador.
        L = (Cuota_Ga) / (z - w)  
        """
        G_a_individual = G_a_total / num_empresas
        if self.z > self.w:
            # L = G_a / (z - w)
            self.demanda_trabajo = G_a_individual / (self.z - self.w)
        else:
            self.demanda_trabajo = 0

    def step(self):
        pass


# --- AGENTE 3: TRABAJADOR (HOGAR) ---
class Trabajador(mesa.Agent):
    """
    Trabaja y consume.
    Controla: Prod. Extramercado (z_b), Deseo de Consumo (c), Tecnologías (x, l).
    """
    def __init__(self, unique_id, model, zb_media, zb_std, c_media, c_std):
        super().__init__(model)
        self.unique_id = unique_id
        
        # --- VARIABLES DE ESTADO ---
        self.empleador = None 
        self.salario_percibido = 0
        self.impuestos_pagados = 0
        self.horas_mercado = 0 # Horas dedicadas al mercado
        self.L_s = 0 # Oferta nocional de trabajo (Horas)
        
        # --- VARIABLES DE HOGAR ---
        self.z_b = max(0.1, np.random.normal(zb_media, zb_std)) # Productividad Extramercado    
        self.c = max(0.1, np.random.normal(c_media, c_std))     # Deseo de Consumo por hora    
        
        # Tecnología de Consumo
        # l: Intensidad (requerimiento de consumo por hora) 
        # x: Grado de incompatibilidad
        self.x = np.random.uniform(0.8, 1.2)
        self.l = np.random.uniform(0.8, 1.2)

        # Resultados de Tiempo
        self.L_b = 0          # Horas extramercado
        self.L_w_total = 0    # Trabajo total (L + L_b)
        self.L_wp = 0         # Tiempo de no consumo exclusivo (Lw^p)

    def step(self):
        # El modelo asume que el Salario (w) es el precio del consumo de mercado
        
        # 1. RECIBIR INGRESOS Y HORAS DE MERCADO
        if self.empleador is not None:
            w_real_mercado = self.empleador.w
            self.horas_mercado = self.model.admin_publica.j
        else:
            # Si está en paro, el salario real en el mercado es 0 para sus cálculos
            w_real_mercado = 0
            self.horas_mercado = 0
        
        # Ingreso Bruto (Monetario)
        renta_bruta = w_real_mercado * self.horas_mercado
        # Consumo Proporcionado por el Mercado (Masa Salarial Neta)
        # Se asume que esto se traduce directamente en unidades de consumo (supuesto: precio=1)
        C_proporcionado_mercado = renta_bruta * (1 - self.model.admin_publica.t)
        self.salario_percibido = C_proporcionado_mercado
        self.impuestos_pagados = renta_bruta * self.model.admin_publica.t
            
        # 2. CÁLCULO DE NECESIDADES (Monetario/Bienes)
        # C_m = c * T_t
        C_deseado_total = self.c * self.model.T_i_total
        
        # 3. OFERTA NOCIONAL DE TRABAJO (L^s)   
        # L^s = C_m / w (usamos el salario promedio de mercado como referencia, si está en paro)
        w_referencia = w_real_mercado if w_real_mercado > 0 else self.model.w_promedio # Usamos la media agregada del modelo
        
        if w_referencia > 0:
            self.L_s = C_deseado_total / w_referencia
        else:
            self.L_s = 0
        
        # 4. TRABAJO EXTRAMERCADO (L_b)   
        # L_b = (C_m - C_mercado) / z_b
        deficit = C_deseado_total - C_proporcionado_mercado
        
        if deficit > 0:
            self.L_b = deficit / self.z_b
        else:
            self.L_b = 0
            
        # 5. TIEMPO TOTAL Y POTENCIAL 
        self.L_w_total = self.horas_mercado + self.L_b
        # L_w^p = T_t * (1 - c * l/x)
        self.L_wp = self.model.T_i_total * (1 - self.c * (self.l / self.x))
        # Aseguramos que L_wp no sea negativo
        self.L_wp = max(0, self.L_wp)