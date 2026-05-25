# normativa.py
# Motor Base: Parámetros del Código Estructural

def obtener_coeficientes_seguridad():
    """Devuelve los coeficientes de mayoración de cargas (ELU)"""
    gamma = {
        "permanente_desfavorable": 1.35,
        "permanente_favorable": 1.00,
        "variable_desfavorable": 1.50,
        "variable_favorable": 0.00,
        "agua_desfavorable": 1.20, # Empuje hidrostático
        "agua_favorable": 1.00
    }
    return gamma

def obtener_coeficientes_simultaneidad():
    """Devuelve los valores Psi (psi_0, psi_1, psi_2) por categoría de uso"""
    psi = {
        "A_residencial": [0.70, 0.50, 0.30],
        "B_oficinas": [0.70, 0.50, 0.30],
        "C_comercial": [0.70, 0.70, 0.60],
        "D_publica_concurrencia": [0.70, 0.70, 0.60],
        "E_almacenamiento": [1.00, 0.90, 0.80],
        "F_trafico_ligero": [0.70, 0.70, 0.60],
        "G_trafico_pesado": [0.70, 0.50, 0.30],
        "viento": [0.60, 0.20, 0.00],
        "nieve": [0.50, 0.20, 0.00]
    }
    return psi

def obtener_recubrimientos_minimos(clase_exposicion):
    """Devuelve el recubrimiento nominal mínimo en mm según exposición"""
    recubrimientos = {
        "I_interiores": 35,
        "IIa_exteriores_secos": 40,
        "IIb_exteriores_humedos": 45,
        "IIIa_marina_aerea": 50,
        "IV_enterrado": 50 # Crítico para cimentaciones y trasdós
    }
    return recubrimientos.get(clase_exposicion, 50)