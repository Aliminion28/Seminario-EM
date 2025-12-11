import mesa
import numpy as np
from .agentes import AdminPublica, Empresa, Trabajador

class ModeloAnisi(mesa.Model):
    """
    Modelo ABM Completo (VERSIÓN ESTABILIZADA) basado en el análisis de David Anisi.
    """
    
    def __init__(self, 
                 # Macro
                 G_a=15000, t=0.22, j=1.0, 
                 # Empresas 
                 z_media=55.0, z_std=2.0,    
                 w_media=16.5, w_std=1.0,    
                 # Hogares
                 zb_media=10.0, zb_std=2.0, c_media=0.8, c_std=0.1,
                 # Población
                 N_trabajadores=1000, N_empresas=50, T_i_total=2000):
        
        super().__init__()
        self.T_i_total = T_i_total
        self.schedule = mesa.time.RandomActivation(self)
        self.N = N_trabajadores
        self.w_promedio = w_media # Inicializamos el salario promedio (para Ls de desempleados)
        
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
            
        # Métricas Macro
        self.empleo_total = 0 # Número de trabajadores empleados en mercado
        self.tasa_paro = 0.0
        self.I1_colocacion = 0.0
        self.I2_dualismo = 0.0
        self.I3_agregado = 0.0


    def step(self):
        # 1. ACTUALIZAR SALARIO PROMEDIO (Referencia para Ls)
        # Esto asegura que Ls usa una referencia de mercado razonable incluso para los no empleados
        salarios = [e.w for e in self.empresas]
        self.w_promedio = np.mean(salarios) if salarios else 1.0

        # 2. MERCADO LABORAL: Asignación de trabajadores a vacantes
        for t in self.trabajadores: t.empleador = None
        # La asignación sigue la lógica simple de las empresas demandando L horas (y por lo tanto, L/j hombres)
        disponibles = self.random.sample(self.trabajadores, len(self.trabajadores))
        indice = 0
        self.empleo_total = 0
        
        for empresa in self.empresas:
            # Demanda de trabajo total de la empresa (en horas L)
            empresa.calcular_demanda(self.admin_publica.G_a, len(self.empresas))
            
            # Convertir a número de hombres (H = L / j), asumiendo j=1
            vacantes = int(round(empresa.demanda_trabajo / self.admin_publica.j))
            contratados = 0
            
            # Contratación: Asignar trabajadores de la lista disponible
            while contratados < vacantes and indice < len(disponibles):
                trabajador = disponibles[indice]
                trabajador.empleador = empresa
                indice += 1
                contratados += 1
            empresa.trabajadores_contratados = contratados
            self.empleo_total += contratados

        # 3. ACCIÓN AGENTES (Cálculo de ingresos, L_b, L_s, L_w_total)
        self.schedule.step()
        
        # 4. CÁLCULOS MACRO Y AGREGACIÓN DE ÍNDICES
        
        # Agregación de tiempos (horas eficaces)
        L_mercado_total = sum([t.horas_mercado for t in self.trabajadores]) 
        L_b_total = sum([t.L_b for t in self.trabajadores])
        L_w_total = L_mercado_total + L_b_total
        
        L_s_total = sum([t.L_s for t in self.trabajadores if t.L_s != float('inf')])
        L_wp_total = sum([t.L_wp for t in self.trabajadores])
        
        # Tasa de Paro (clásica, sobre la población activa total N)
        self.tasa_paro = 1.0 - (self.empleo_total / self.N)
        
        # [cite_start]I1: Índice de Colocación (Mercado vs. Oferta Nocional) [cite: 87, 436]
        if L_s_total > 0:
            self.I1_colocacion = L_mercado_total / L_s_total
        else:
            self.I1_colocacion = 0.0

        # [cite_start]I2: Índice de Dualismo (Mercado vs. Trabajo Total) [cite: 116, 446]
        if L_w_total > 0:
            self.I2_dualismo = L_mercado_total / L_w_total
        else:
            self.I2_dualismo = 0.0
        
        # [cite_start]I3: Índice de Ocupación/Frustración (Trabajo Total vs. Potencial) [cite: 159, 166]
        if L_wp_total > 0:
            self.I3_agregado = L_w_total / L_wp_total
        else:
            # Indica Frustración Extrema (Lw^p=0 o negativo, lo que es físicamente imposible)
            self.I3_agregado = float('inf')