# hormigon.py
# Módulo Estructural: Estabilidad Global y Verificación de Armaduras

import math

def comprobar_estabilidad(m_estabilizador, m_desestabilizador, f_roce, f_deslizamiento):
    """
    Comprueba la estabilidad global del muro.
    Calcula los Coeficientes de Seguridad (CS) a Vuelco y Deslizamiento.
    """
    # Evitar divisiones por cero
    cs_vuelco = (m_estabilizador / m_desestabilizador) if m_desestabilizador > 0 else 999.0
    cs_deslizamiento = (f_roce / f_deslizamiento) if f_deslizamiento > 0 else 999.0
    
    # Criterio estricto de norma (CS >= 1.50)
    cumple_vuelco = cs_vuelco >= 1.50
    cumple_desliza = cs_deslizamiento >= 1.50
    
    return {
        "CS_Vuelco": round(cs_vuelco, 2),
        "Cumple_Vuelco": cumple_vuelco,
        "CS_Deslizamiento": round(cs_deslizamiento, 2),
        "Cumple_Deslizamiento": cumple_desliza
    }

def verificar_cuantia_flexion(m_ed_kNm, b_m, d_m, fck_MPa, fyk_MPa, as_propuesto_cm2):
    """
    Comprobación a flexión simple en Estado Límite Último (ELU).
    Recibe el Momento de diseño y el armado propuesto por el usuario.
    Compara el cálculo puro con los mínimos geométricos del Código Estructural.
    """
    # 1. Conversión al Sistema Internacional puro (N, mm)
    m_ed = m_ed_kNm * 1e6
    b = b_m * 1000
    d = d_m * 1000
    
    # 2. Resistencias minoradas del material (gamma_c = 1.5, gamma_s = 1.15)
    fcd = fck_MPa / 1.5
    fyd = fyk_MPa / 1.15
    
    # 3. Momento reducido (Límite de sección)
    mu = m_ed / (b * (d**2) * fcd)
    necesita_compresion = mu > 0.295 # Si supera este límite, el muro es muy fino
    
    # 4. Cálculo del As estrictamente necesario por cálculo (Fórmulas de equilibrio)
    if not necesita_compresion:
        omega = 1 - math.sqrt(1 - 2 * mu)
        as_nec_mm2 = omega * b * d * (fcd / fyd)
        as_nec_cm2 = as_nec_mm2 / 100
    else:
        as_nec_cm2 = 0.0 # Requiere rediseñar la sección (aumentar canto)
        
    # 5. Cuantía geométrica mínima (aprox 2 por mil para muros en general)
    as_min_geom_cm2 = (0.002 * b * d) / 100
    
    # 6. Decisión del motor: El requerimiento es el máximo entre cálculo y norma
    as_final_requerido = max(as_nec_cm2, as_min_geom_cm2)
    
    # 7. Veredicto final frente a la propuesta del usuario
    cumple_propuesto = as_propuesto_cm2 >= as_final_requerido
    
    return {
        "Cumple": cumple_propuesto,
        "As_Usuario_cm2": as_propuesto_cm2,
        "As_Calculo_Puro_cm2": round(as_nec_cm2, 2),
        "As_Minimo_Norma_cm2": round(as_min_geom_cm2, 2),
        "As_Definitivo_Requerido": round(as_final_requerido, 2),
        "Alerta_Canto": "Canto insuficiente. Aumente espesor del muro." if necesita_compresion else "OK"
    }