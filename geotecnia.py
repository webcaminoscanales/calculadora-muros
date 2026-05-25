# geotecnia.py
# Motor Geotécnico: Empujes de tierras, Estratigrafía y Nivel Freático

import math

def calcular_ka_rankine(phi_grados, beta_grados=0):
    """
    Calcula el coeficiente de empuje activo (Ka) según la teoría de Rankine
    para un terreno con una inclinación beta en la coronación.
    """
    phi = math.radians(phi_grados)
    beta = math.radians(beta_grados)
    
    # Si la inclinación del talud es mayor que el rozamiento interno, el talud es inestable
    if beta > phi:
        beta = phi
        
    cos_b = math.cos(beta)
    
    # Formulación matemática de Rankine generalizada
    sustraendo = math.sqrt(abs(cos_b**2 - math.cos(phi)**2))
    num = cos_b - sustraendo
    den = cos_b + sustraendo
    
    ka = cos_b * (num / den) if den != 0 else 0
    return ka

def calcular_presiones_terreno(estratos, beta_grados=0, nivel_freatico=None):
    """
    Calcula las presiones efectivas del terreno y la presión hidrostática paso a paso.
    Soporta múltiples capas de suelo (estratigrafía) y presencia de agua.
    
    estratos: Lista de diccionarios ordenados de arriba a abajo.
              Ejemplo: [{"espesor": 2.0, "phi": 30, "c": 0, "gamma": 18, "gamma_sat": 20}]
    nivel_freatico: Profundidad en metros desde la coronación. None si está seco.
    """
    puntos_calculo = []
    z_actual = 0.0
    sigma_v_efectiva = 0.0
    gamma_agua = 9.81  # Peso específico del agua en kN/m3
    
    for i, estrato in enumerate(estratos):
        espesor = estrato["espesor"]
        phi = estrato["phi"]
        c = estrato["c"]
        gamma_seco = estrato["gamma"]
        # Si no se define peso saturado, estimamos un valor razonable
        gamma_sat = estrato.get("gamma_sat", gamma_seco + 2.0)
        
        ka = calcular_ka_rankine(phi, beta_grados)
        
        # --- PUNTO SUPERIOR DEL ESTRATO ---
        u_top = 0.0
        if nivel_freatico is not None and z_actual > nivel_freatico:
            u_top = (z_actual - nivel_freatico) * gamma_agua
            
        # Ecuación de Coulomb/Rankine considerando cohesión
        p_tierra_top = ka * sigma_v_efectiva - 2 * c * math.sqrt(ka)
        p_tierra_top = max(0.0, p_tierra_top)  # El terreno no trabaja a tracción
        
        puntos_calculo.append({
            "z": z_actual,
            "estrato": i + 1,
            "posicion": "Inicio Estrato",
            "sigma_v_ef": sigma_v_efectiva,
            "p_tierra": p_tierra_top,
            "p_agua": u_top
        })
        
        # --- CALCULO DEL INCREMENTO DE TENSIÓN VERTICAL ---
        z_siguiente = z_actual + espesor
        
        # Caso A: El nivel freático corta este estrato por la mitad
        if nivel_freatico is not None and z_actual < nivel_freatico < z_siguiente:
            espesor_seco = nivel_freatico - z_actual
            espesor_sat = z_siguiente - nivel_freatico
            delta_sigma = (espesor_seco * gamma_seco) + (espesor_sat * (gamma_sat - gamma_agua))
        # Caso B: Todo el estrato está por debajo del nivel freático (sumergido)
        elif nivel_freatico is not None and z_actual >= nivel_freatico:
            delta_sigma = espesor * (gamma_sat - gamma_agua)
        # Caso C: El estrato está completamente seco
        else:
            delta_sigma = espesor * gamma_seco
            
        sigma_v_efectiva += delta_sigma
        z_actual = z_siguiente
        
        # --- PUNTO INFERIOR DEL ESTRATO ---
        u_bot = 0.0
        if nivel_freatico is not None and z_actual > nivel_freatico:
            u_bot = (z_actual - nivel_freatico) * gamma_agua
            
        p_tierra_bot = ka * sigma_v_efectiva - 2 * c * math.sqrt(ka)
        p_tierra_bot = max(0.0, p_tierra_bot)
        
        puntos_calculo.append({
            "z": z_actual,
            "estrato": i + 1,
            "posicion": "Fin Estrato",
            "sigma_v_ef": sigma_v_efectiva,
            "p_tierra": p_tierra_bot,
            "p_agua": u_bot
        })
        
    return puntos_calculo