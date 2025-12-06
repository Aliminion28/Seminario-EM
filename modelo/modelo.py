import mesa
import numpy as np
from .agentes import AdminPublica, Empresa, Trabajador

class ModeloAnisi(mesa.Model):
    """
    Modelo ABM Completo (VERSIÓN ESTABILIZADA).
    Reducimos la varianza para evitar resultados erráticos en la calibración.
    """
    
    def __init__(self, 
                 # Macro
                 G_a=15000, t=0.22, j=1.0, 
                 # Empresas (MENOS VARIANZA AQUÍ)
                 z_media=55.0, z_std=2.0,    # Antes 15.0 -> Ahora 5.0
                 w_media=16.5, w_std=1.0,    # Antes 5.0  -> Ahora 2.0
                 # Hogares
                 zb_media=10.0, zb_std=2.0, c_media=0.8, c_std=0.1,
                 # Población
                 N_trabajadores=1000, N_empresas=50, T_i_total=2000):
        
        super().__init__()
        self.T_i_total = T_i_total
        self.schedule = mesa.time.RandomActivation(self)
        self.N = N_trabajadores
        
        # 1. Gobierno
        self.admin_publica = AdminPublica("Gobierno", self, G_a, t, j)
        self.schedule.add(self.admin_publica)
        
        # 2. Empresas
        self.empresas = []
        for i in range(N_empresas):
            empresa = Empresa(f"Empresa_{i}", self, z_media, z_std, w_media, w_std)
            self.empresas.append(empresa)
            self.schedule.add(empresa)
            
        # 3. Trabajadores
        self.trabajadores = []
        for i in range(N_trabajadores):
            trabajador = Trabajador(f"Trabajador_{i}", self, zb_media, zb_std, c_media, c_std)
            self.trabajadores.append(trabajador)
            self.schedule.add(trabajador)
            
        self.empleo_total = 0
        self.I3_agregado = 0

    def step(self):
        # 1. MERCADO LABORAL
        for t in self.trabajadores: t.empleador = None
        disponibles = self.random.sample(self.trabajadores, len(self.trabajadores))
        indice = 0
        self.empleo_total = 0
        
        for empresa in self.empresas:
            # Demanda
            empresa.calcular_demanda(self.admin_publica.G_a, len(self.empresas))
            vacantes = int(round(empresa.demanda_trabajo))
            contratados = 0
            # Contratación
            while contratados < vacantes and indice < len(disponibles):
                trabajador = disponibles[indice]
                trabajador.empleador = empresa
                indice += 1
                contratados += 1
            empresa.trabajadores_contratados = contratados
            self.empleo_total += contratados

        # 2. ACCIÓN AGENTES
        self.schedule.step()
        
        # 3. CÁLCULOS MACRO
        L_mercado_total = self.empleo_total * self.admin_publica.j
        trabajo_extramercado_total = sum([t.L_b for t in self.trabajadores])
        L_w_total = L_mercado_total + trabajo_extramercado_total
        
        # Tiempo disponible (Suma total)
        L_wp_total = sum([self.T_i_total * (1 - t.c * (t.l/t.x)) for t in self.trabajadores])
        
        if L_wp_total > 0:
            self.I3_agregado = L_w_total / L_wp_total
        else:
            self.I3_agregado = float('inf')