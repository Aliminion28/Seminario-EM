# Guardar en: modelo/agentes.py
import mesa
import numpy as np

# --- AGENTE 1: ADMINISTRACIÓN PÚBLICA ---
class AdminPublica(mesa.Agent):
    def __init__(self, unique_id, model, G_a, t, j):
        super().__init__(model)
        self.unique_id = unique_id
        self.G_a = G_a  
        self.t = t      
        self.j = j      

    def step(self):
        pass

# --- AGENTE 2: EMPRESA ---
class Empresa(mesa.Agent):
    def __init__(self, unique_id, model, z_media, z_std, w_media, w_std):
        super().__init__(model)
        self.unique_id = unique_id
        self.z = np.random.normal(z_media, z_std)
        w_provisional = np.random.normal(w_media, w_std)
        self.w = max(1.0, min(w_provisional, self.z - 1.0)) 
        self.trabajadores_contratados = 0
        self.demanda_trabajo = 0

    def calcular_demanda(self, G_a_total, num_empresas):
        G_a_individual = G_a_total / num_empresas
        if self.z > self.w:
            self.demanda_trabajo = G_a_individual / (self.z - self.w)
        else:
            self.demanda_trabajo = 0

    def step(self):
        pass

# --- AGENTE 3: TRABAJADOR ---
class Trabajador(mesa.Agent):
    def __init__(self, unique_id, model, zb_media, zb_std, c_media, c_std):
        super().__init__(model)
        self.unique_id = unique_id
        self.empleador = None 
        self.salario_percibido = 0
        self.horas_mercado = 0 
        self.L_s = 0 
        self.z_b = max(0.1, np.random.normal(zb_media, zb_std))    
        self.c = max(0.1, np.random.normal(c_media, c_std))     
        self.x = np.random.uniform(0.8, 1.2)
        self.l = np.random.uniform(0.8, 1.2)
        self.L_b = 0          
        self.L_w_total = 0    
        self.L_wp = 0         

    def step(self):
        if self.empleador is not None:
            w_real_mercado = self.empleador.w
            self.horas_mercado = self.model.admin_publica.j
        else:
            w_real_mercado = 0
            self.horas_mercado = 0
        
        renta_bruta = w_real_mercado * self.horas_mercado
        C_proporcionado_mercado = renta_bruta * (1 - self.model.admin_publica.t)
        self.salario_percibido = C_proporcionado_mercado
            
        C_deseado_total = self.c * self.model.T_i_total
        
        w_referencia = w_real_mercado if w_real_mercado > 0 else self.model.w_promedio
        if w_referencia > 0:
            self.L_s = C_deseado_total / w_referencia
        else:
            self.L_s = 0
        
        deficit = C_deseado_total - C_proporcionado_mercado
        if deficit > 0:
            self.L_b = deficit / self.z_b
        else:
            self.L_b = 0
            
        self.L_w_total = self.horas_mercado + self.L_b
        self.L_wp = max(0, self.model.T_i_total * (1 - self.c * (self.l / self.x)))