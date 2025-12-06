import mesa
import numpy as np

# --- AGENTE 1: ADMINISTRACIÓN PÚBLICA ---
class AdminPublica(mesa.Agent):
    """
    Representa al Estado. Fija las reglas del juego macroeconómico.
    Controla: Gasto Autónomo (Ga), Impuestos (t) y Jornada Legal (j).
    Referencia: [cite: 21-26]
    """
    def __init__(self, unique_id, model, G_a, t, j):
        super().__init__(model)
        self.unique_id = unique_id
        
        # Variables de control estatal
        self.G_a = G_a  # Presupuesto de Gasto Público
        self.t = t      # Tipo impositivo (0.15 = 15%)
        self.j = j      # Jornada laboral legal (ej. 1.0 unidad o 40h)

    def step(self):
        # En modelos simples, el estado es estático o reactivo.
        # Aquí podría subir impuestos si hay déficit, etc.
        pass


# --- AGENTE 2: EMPRESA ---
class Empresa(mesa.Agent):
    """
    Produce bienes y contrata trabajadores.
    Controla: Productividad (z), Salario (w) y Demanda de Trabajo.
    Referencia: [cite: 27-34]
    """
    def __init__(self, unique_id, model, z_media, z_std, w_media, w_std):
        super().__init__(model)
        self.unique_id = unique_id
        
        # GENERACIÓN DE HIPÓTESIS: PRODUCTIVIDAD (Normal)
        # Cada empresa nace con una tecnología diferente
        self.z = np.random.normal(z_media, z_std)
        
        # GENERACIÓN DE DATOS: SALARIO (Log-Normal simplificada o Normal positiva)
        # Asumimos una distribución para la oferta salarial de esta empresa
        # (Aseguramos que no sea negativo ni mayor que la productividad)
        w_provisional = np.random.normal(w_media, w_std)
        self.w = max(1.0, min(w_provisional, self.z - 1.0)) 
        
        # Estado
        self.trabajadores_contratados = 0
        self.demanda_trabajo = 0

    def calcular_demanda(self, G_a_total, num_empresas):
        """
        Calcula cuánta gente necesita contratar basándose en su cuota de mercado.
        Suponemos reparto igualitario del Gasto Público (G_a) por simplicidad inicial.
        L = (Cuota_Ga) / (z - w)
        """
        G_a_individual = G_a_total / num_empresas
        if self.z > self.w:
            self.demanda_trabajo = G_a_individual / (self.z - self.w)
        else:
            self.demanda_trabajo = 0 # Empresa inviable

    def step(self):
        pass


# --- AGENTE 3: TRABAJADOR (HOGAR) ---
class Trabajador(mesa.Agent):
    """
    Trabaja y consume.
    Controla: Prod. Extramercado (z_b), Consumo (c), Tecnologías (x, l).
    Referencia: [cite: 35-43]
    """
    def __init__(self, unique_id, model, zb_media, zb_std, c_media, c_std):
        super().__init__(model)
        self.unique_id = unique_id
        
        # --- VARIABLES DE ESTADO ---
        self.empleador = None # Quién me ha contratado (Agente Empresa)
        self.salario_percibido = 0
        self.impuestos_pagados = 0
        
        # --- GENERACIÓN DE HIPÓTESIS (Variables Heterogéneas) ---
        
        # 1. Productividad Extramercado (Hipótesis: Normal, menor que mercado)
        self.z_b = max(0.1, np.random.normal(zb_media, zb_std))
        
        # 2. Deseo de Consumo (Hipótesis: Normal vinculada a expectativas sociales)
        self.c = max(0.1, np.random.normal(c_media, c_std))
        
        # 3. Tecnología de Consumo (Hipótesis: Uniforme - Aleatoriedad total)
        # x: Intensidad, l: Incompatibilidad
        self.x = np.random.uniform(0.8, 1.2)
        self.l = np.random.uniform(0.8, 1.2)

        # Resultados
        self.L_b = 0 # Horas extramercado
        self.L_w_total = 0 # Trabajo total

    def step(self):
        # 1. Recibir ingresos (Mercado)
        if self.empleador is not None:
            # Renta Bruta = Salario hora * Jornada
            renta_bruta = self.empleador.w * self.model.admin_publica.j
            # Renta Neta = Bruta * (1 - tipos)
            self.salario_percibido = renta_bruta * (1 - self.model.admin_publica.t)
            self.impuestos_pagados = renta_bruta * self.model.admin_publica.t
            horas_mercado = self.model.admin_publica.j
        else:
            self.salario_percibido = 0
            self.impuestos_pagados = 0
            horas_mercado = 0
            
        # 2. Calcular Necesidad de Consumo Total
        # C_total = c * T_total
        C_deseado_total = self.c * self.model.T_i_total
        
        # 3. Decisión de Trabajo Extramercado
        # Déficit = Lo que quiero - Lo que tengo
        deficit = C_deseado_total - self.salario_percibido
        
        if deficit > 0:
            self.L_b = deficit / self.z_b
        else:
            self.L_b = 0
            
        # 4. Total
        self.L_w_total = horas_mercado + self.L_b