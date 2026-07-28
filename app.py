# app.py
# Motor unificado: Interfaz + Geotecnia + Hormigón + Normativa

import streamlit as st
import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np

# --- 0. FUNCIONES MATEMÁTICAS Y MOTORES ---

def calcular_ka_rankine(phi_grados, beta_grados=0):
    phi = math.radians(phi_grados)
    beta = math.radians(beta_grados)
    if beta > phi:
        beta = phi
    cos_b = math.cos(beta)
    sustraendo = math.sqrt(abs(cos_b**2 - math.cos(phi)**2))
    num = cos_b - sustraendo
    den = cos_b + sustraendo
    ka = cos_b * (num / den) if den != 0 else 0
    return ka

def comprobar_estabilidad(m_estabilizador, m_desestabilizador, f_roce, f_deslizamiento):
    cs_vuelco = (m_estabilizador / m_desestabilizador) if m_desestabilizador > 0 else 999.0
    cs_deslizamiento = (f_roce / f_deslizamiento) if f_deslizamiento > 0 else 999.0
    return {
        "CS_Vuelco": round(cs_vuelco, 2),
        "Cumple_Vuelco": cs_vuelco >= 1.50,
        "CS_Deslizamiento": round(cs_deslizamiento, 2),
        "Cumple_Deslizamiento": cs_deslizamiento >= 1.50
    }

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Cálculo Estructural | Muros", layout="wide")

# Colores de la marca
COLOR_PRINCIPAL = "#0f172a"
COLOR_ACCIO = "#0ea5e9"

# --- 2. CABECERA ---
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    st.markdown(f"<h1 style='color: {COLOR_ACCIO};'>CE</h1>", unsafe_allow_html=True)
with col_titulo:
    st.title("🏗️ Cálculo Avanzado de Muros de Contención")
    st.markdown("Definición completa de geometría, terreno y cargas.")

st.divider()

# --- 3. CONTENEDOR DE PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["📏 1. Geometría", "🌍 2. Terreno y Agua", "⬇️ 3. Cargas", "⚙️ 4. Materiales"])

# PESTAÑA 1: GEOMETRÍA
with tab1:
    st.markdown("#### Geometría del Alzado y Zapata")
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        h_muro = st.number_input("Altura libre del alzado (m)", value=3.0, step=0.1)
        e_coronacion = st.number_input("Espesor en coronación (m)", value=0.3, step=0.05)
        e_base = st.number_input("Espesor en la base del alzado (m)", value=0.3, step=0.05)
        
    with col_g2:
        canto_zapata = st.number_input("Canto de la zapata (m)", value=0.4, step=0.1)
        vuelo_puntera = st.number_input("Vuelo de la puntera (m)", value=0.5, step=0.1)
        vuelo_talon = st.number_input("Vuelo del talón (m)", value=1.0, step=0.1)
        ancho_total = e_base + vuelo_puntera + vuelo_talon
        st.info(f"Ancho total de la zapata calculado: {round(ancho_total, 2)} m")

# PESTAÑA 2: TERRENO Y AGUA
with tab2:
    st.markdown("#### Estratigrafía del Trasdós")
    st.caption("🔒 PLAN PRO: Las estratigrafías multicapa están bloqueadas en la versión gratuita.")
    
    # Capado a 1 solo estrato para la versión gratis
    datos_terreno_base = pd.DataFrame(
        [{"Estrato": "Relleno", "Espesor (m)": h_muro, "Densidad (kN/m3)": 18.0, "Fricción (º)": 30.0, "Cohesión (kPa)": 0.0}]
    )
    estratos_df = st.data_editor(datos_terreno_base, num_rows="fixed", use_container_width=True)
    
    st.divider()
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("#### Superficie y Talud")
        beta = st.slider("Inclinación del talud en trasdós (º)", min_value=0, max_value=45, value=0)
    with col_t2:
        st.markdown("#### Nivel Freático")
        hay_agua = st.checkbox("Presencia de Nivel Freático", disabled=True)
        st.warning("🔒 PLAN PRO: El cálculo con nivel freático requiere suscripción.")

# PESTAÑA 3: CARGAS
with tab3:
    st.markdown("#### Sobrecargas en el Trasdós")
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        hay_q_unif = st.checkbox("Sobrecarga Uniforme (Uso público, tráfico leve)")
        if hay_q_unif:
            q_unif = st.number_input("Valor de la sobrecarga (kN/m2)", value=10.0, step=1.0)
            
    with col_c2:
        hay_q_lineal = st.checkbox("Carga Lineal Paralela (Ej: Eje de camión)")
        if hay_q_lineal:
            q_lineal = st.number_input("Valor de la carga (kN/m)", value=50.0, step=5.0)
            dist_lineal = st.number_input("Distancia desde el trasdós del muro (m)", value=1.0, step=0.1)

# PESTAÑA 4: MATERIALES
with tab4:
    st.markdown("#### Propiedades del Hormigón Armado")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        fck = st.selectbox("Hormigón (fck)", ["HA-25", "HA-30", "HA-35"])
    with col_m2:
        fyk = st.selectbox("Acero (fyk)", ["B-500 S", "B-400 S"])
    with col_m3:
        recubrimiento = st.number_input("Recubrimiento mecánico (mm)", value=50, step=5)

st.divider()

# --- 4. MOTOR DE EJECUCIÓN VISUAL Y CÁLCULO ---
# Botón activado
if st.button("🚀 Ejecutar Cálculo", type="primary", use_container_width=True):
    
    st.success("Cálculo ejecutado correctamente. Mostrando resultados...")
    col_res1, col_res2 = st.columns([1, 1])
    
    with col_res1:
        st.markdown("### Esquema Geométrico")
        
        # Generación del gráfico con Matplotlib
        fig, ax = plt.subplots(figsize=(6, 6))
        
        # Coordenadas (Origen 0,0 en la intersección inferior del trasdós)
        # Zapata
        z_x = [-e_base - vuelo_puntera, vuelo_talon, vuelo_talon, -e_base - vuelo_puntera, -e_base - vuelo_puntera]
        z_y = [-canto_zapata, -canto_zapata, 0, 0, -canto_zapata]
        
        # Alzado
        a_x = [-e_base, 0, 0, -e_coronacion, -e_base]
        a_y = [0, 0, h_muro, h_muro, 0]
        
        # Dibujo
        ax.fill(z_x, z_y, color=COLOR_ACCIO, alpha=0.5, label="Zapata")
        ax.plot(z_x, z_y, color=COLOR_PRINCIPAL, linewidth=2)
        ax.fill(a_x, a_y, color=COLOR_ACCIO, alpha=0.8, label="Alzado")
        ax.plot(a_x, a_y, color=COLOR_PRINCIPAL, linewidth=2)
        
        # Línea de terreno (Trasdós)
        ax.plot([0, max(2, vuelo_talon + 1)], [h_muro, h_muro + math.tan(math.radians(beta))*max(2, vuelo_talon + 1)], 
                color="#8B4513", linewidth=3, linestyle="--", label="Terreno")
        
        ax.set_aspect('equal')
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(loc="upper left")
        st.pyplot(fig)
        
    with col_res2:
        st.markdown("### Resultados Preliminares")
        
        # Extraemos los datos del dataframe para el cálculo básico
        phi_usuario = estratos_df["Fricción (º)"].iloc[0]
        gamma_usuario = estratos_df["Densidad (kN/m3)"].iloc[0]
        
        # Llamada a la función matemática real
        ka = calcular_ka_rankine(phi_usuario, beta)
        empuje_total = 0.5 * gamma_usuario * (h_muro + canto_zapata)**2 * ka
        
        st.metric("Coeficiente Empuje Activo (Ka)", round(ka, 3))
        st.metric("Empuje Total (kN/m)", round(empuje_total, 2))
        
        st.markdown("#### Comprobación de Estabilidad (Estimación)")
        # Valores simulados basados en la geometría para dar feedback inmediato al usuario
        vol_hormigon = (h_muro * (e_base+e_coronacion)/2) + (ancho_total * canto_zapata)
        peso_hormigon = vol_hormigon * 25 # kN/m3
        
        estabilidad = comprobar_estabilidad(
            m_estabilizador=peso_hormigon * (vuelo_puntera + e_base/2), 
            m_desestabilizador=empuje_total * ((h_muro+canto_zapata)/3), 
            f_roce=peso_hormigon * math.tan(math.radians(phi_usuario)), 
            f_deslizamiento=empuje_total
        )
        
        if estabilidad["Cumple_Vuelco"]:
            st.success(f"✅ CS Vuelco: {estabilidad['CS_Vuelco']} (≥ 1.50)")
        else:
            st.error(f"❌ CS Vuelco: {estabilidad['CS_Vuelco']} (< 1.50)")
            
        if estabilidad["Cumple_Deslizamiento"]:
            st.success(f"✅ CS Deslizamiento: {estabilidad['CS_Deslizamiento']} (≥ 1.50)")
        else:
            st.error(f"❌ CS Deslizamiento: {estabilidad['CS_Deslizamiento']} (< 1.50)")
        
        st.info("🔒 PLAN PRO: Suscríbete para descargar la memoria de cálculo en PDF con la armadura necesaria.")
