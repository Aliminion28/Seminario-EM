# Guardar en: modelo/modelo.py
import mesa
import numpy as np
# Importación relativa para que funcione como paquete
from .agentes import AdminPublica, Empresa, Trabajador

class ModeloAnisi(mesa.Model):
    """
    Modelo ABM Calibrado para España 2024.
    """
    def __init__(self, 
                 # DATOS MACRO ESPAÑA 2024 (Reales)
                 G_a=45000,      # Gasto estimado inicial
                 t=0.30,         # Presión fiscal efectiva ~30%
                 j=1.0,          # Jornada normalizada
                 # EMPRESAS (Productividad y Salarios 2024)
                 z_media=68.0, z_std=5.0,    # PIB/hora
                 w_media=17.5, w_std=2.0,    # Coste laboral neto aprox
                 # HOGARES
                 zb_media=15.0, zb_std=2.0,  # Prod. doméstica (hipótesis)
                 c_media=0.7, c_std=0.1,     # Consumo (hipótesis)
                 # POBLACIÓN
                 N_trabajadores=1000, N_empresas=50, T_i_total=2000):
        
        super().__init__()
        self.T_i_total = T_i_total
        self.schedule = mesa.time.RandomActivation(self)
        self.N = N_trabajadores
        self.w_promedio = w_media 
        
        self.admin_publica = AdminPublica("Gobierno", self, G_a, t, j)
        self.schedule.add(self.admin_publica)
        
        self.empresas = []
        for i in range(N_empresas):
            empresa = Empresa(f"Empresa_{i}", self, z_media, z_std, w_media, w_std)
            self.empresas.append(empresa)
            self.schedule.add(empresa)
            
        self.trabajadores = []
        for i in range(N_trabajadores):
            trabajador = Trabajador(f"Trabajador_{i}", self, zb_media, zb_std, c_media, c_std)
            self.trabajadores.append(trabajador)
            self.schedule.add(trabajador)
            
        self.empleo_total = 0
        self.I3_agregado = 0

    def step(self):
        salarios = [e.w for e in self.empresas]
        self.w_promedio = np.mean(salarios) if salarios else 1.0

        # Mercado Laboral
        for t in self.trabajadores: t.empleador = None
        disponibles = self.random.sample(self.trabajadores, len(self.trabajadores))
        indice = 0
        self.empleo_total = 0
        
        for empresa in self.empresas:
            empresa.calcular_demanda(self.admin_publica.G_a, len(self.empresas))
            vacantes = int(round(empresa.demanda_trabajo / self.admin_publica.j))
            contratados = 0
            while contratados < vacantes and indice < len(disponibles):
                trabajador = disponibles[indice]
                trabajador.empleador = empresa
                indice += 1
                contratados += 1
            empresa.trabajadores_contratados = contratados
            self.empleo_total += contratados

        self.schedule.step()
        
        # Cálculos Macro (I3)
        L_mercado_total = sum([t.horas_mercado for t in self.trabajadores]) 
        L_b_total = sum([t.L_b for t in self.trabajadores])
        L_w_total = L_mercado_total + L_b_total
        L_wp_total = sum([t.L_wp for t in self.trabajadores])
        
        if L_wp_total > 0:
            self.I3_agregado = L_w_total / L_wp_total
        else:
            self.I3_agregado = float('inf')