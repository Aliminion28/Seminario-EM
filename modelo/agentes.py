import mesa

class Individuo(mesa.Agent):
    """
    Un agente que representa un 'Individuo' u 'Hogar' en el modelo de Anisi.
    """
    def __init__(self, unique_id, model):
        # --- INICIO DE LA CORRECCIÓN ---
        # 1. Llamamos al __init__ padre SÓLO con el modelo (como espera tu versión de Mesa)
        super().__init__(model) 
        
        # 2. Sobrescribimos el unique_id que Mesa haya autogenerado
        #    con el 'i' que le pasamos desde el modelo.
        self.unique_id = unique_id
        # --- FIN DE LA CORRECCIÓN ---
        
        # Estado inicial del agente
        self.esta_empleado_mercado = False
        
        # Parámetros que el agente "conoce" del modelo
        self.consumo_deseado = model.C_m_agente  # Consumo deseado por este agente
        self.salario_jornada = model.w * model.j  # Salario por la jornada de mercado
        self.jornada_mercado = model.j
        self.prod_extramercado = model.z_b
        
        # Variables de resultado del agente
        self.horas_trabajo_mercado = 0
        self.horas_trabajo_extramercado = 0
        self.horas_trabajo_total = 0

    def step(self):
        """
        Define el comportamiento del agente en cada paso.
        """
        # 1. ¿Tengo trabajo de mercado?
        if self.esta_empleado_mercado:
            consumo_obtenido = self.salario_jornada
            self.horas_trabajo_mercado = self.jornada_mercado
        else:
            consumo_obtenido = 0
            self.horas_trabajo_mercado = 0
            
        # 2. ¿Necesito trabajo extramercado?
        consumo_faltante = self.consumo_deseado - consumo_obtenido
        
        if consumo_faltante > 0:
            # Calcular horas necesarias para cubrir el hueco
            horas_extra = consumo_faltante / self.prod_extramercado
            self.horas_trabajo_extramercado = horas_extra
        else:
            self.horas_trabajo_extramercado = 0 # No necesito trabajo extra
            
        # 3. Calcular trabajo total del agente
        self.horas_trabajo_total = self.horas_trabajo_mercado + self.horas_trabajo_extramercado