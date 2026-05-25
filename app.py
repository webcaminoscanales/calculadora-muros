# app.py
# Interfaz de Usuario (SaaS Cálculo Estructural)

import streamlit as st
import normativa
import geotecnia
import hormigon

# 1. Configuración de la página (Modo Pantalla Completa y Título)
st.set_page_config(page_title="Acero y Código | Muros", layout="wide")

st.title("🏗️ Cálculo Avanzado de Muros de Contención")
st.markdown("Verificación de estabilidad y armaduras según **Código Estructural**.")

st.divider()

# 2. Panel Lateral (Entrada de Datos del Usuario)
st.sidebar.header("1. Geometría del Muro")
h_muro = st.sidebar.number_input("Altura del alzado (m)", value=3.0, step=0.1)
b_zapata = st.sidebar.number_input("Ancho total de zapata (m)", value=1.5, step=0.1)
canto_zapata = st.sidebar.number_input("Canto de la zapata (m)", value=0.4, step=0.1)

st.sidebar.header("2. Datos Geotécnicos")
phi = st.sidebar.number_input("Ángulo de rozamiento interno (º)", value=30.0, step=1.0)
c_cohesion = st.sidebar.number_input("Cohesión (kPa)", value=0.0, step=1.0)
gamma_terr = st.sidebar.number_input("Peso específico terreno (kN/m3)", value=18.0, step=0.1)
beta = st.sidebar.slider("Inclinación del talud en trasdós (º)", min_value=0, max_value=45, value=0)

st.sidebar.header("3. Armado Propuesto (Alzado base)")
fck = st.sidebar.selectbox("Resistencia del Hormigón (MPa)", [25, 30, 35, 40])
fyk = st.sidebar.selectbox("Límite elástico Acero (MPa)", [500])
as_propuesto = st.sidebar.number_input("Cuantía de Acero (cm2/m)", value=12.0, step=0.5)

# 3. Botón de Cálculo y Lógica de Conexión
if st.button("Ejecutar Cálculo Normativo", type="primary"):
    
    # Simulación de extracción de datos de nuestros módulos backend
    estratos = [{"espesor": h_muro, "phi": phi, "c": c_cohesion, "gamma": gamma_terr}]
    
    with st.spinner('Iterando matriz de combinaciones ELU/ELS...'):
        # Llamadas a tus propios archivos (magia interna)
        presiones = geotecnia.calcular_presiones_terreno(estratos, beta)
        
        # Para esta versión, pasamos momentos y fuerzas estáticas ficticias 
        # basadas en una proporción del muro para que veas la UI funcionando.
        # En el código final, aquí integraremos el sumatorio de fuerzas real.
        m_est = (gamma_terr * h_muro * b_zapata) * (b_zapata / 2) # Ficticio conservador
        m_des = presiones[-1]["p_tierra"] * (h_muro**2) / 6 # Ficticio conservador
        f_roce = (gamma_terr * h_muro * b_zapata) * 0.5
        f_desliza = presiones[-1]["p_tierra"] * h_muro / 2
        
        m_ed_base = m_des * 1.35 # Mayorado
        
        res_estab = hormigon.comprobar_estabilidad(m_est, m_des, f_roce, f_desliza)
        res_flex = hormigon.verificar_cuantia_flexion(m_ed_base, 1.0, b_zapata-0.05, fck, fyk, as_propuesto)

    # 4. Salida de Resultados (El Dashboard de Mando)
    st.subheader("📊 Envolventes Críticas y Estabilidad")
    
    col1, col2, col3 = st.columns(3)
    
    # Semáforo Vuelco
    if res_estab["Cumple_Vuelco"]:
        col1.success(f"CS Vuelco: {res_estab['CS_Vuelco']} ≥ 1.50 (CUMPLE)")
    else:
        col1.error(f"CS Vuelco: {res_estab['CS_Vuelco']} < 1.50 (FALLA)")
        
    # Semáforo Deslizamiento
    if res_estab["Cumple_Deslizamiento"]:
        col2.success(f"CS Desliz: {res_estab['CS_Deslizamiento']} ≥ 1.50 (CUMPLE)")
    else:
        col2.error(f"CS Desliz: {res_estab['CS_Deslizamiento']} < 1.50 (FALLA)")
        
    # Semáforo Flexión (Acero)
    if res_flex["Cumple"]:
        col3.success(f"Acero: Propuesto {as_propuesto} cm2 ≥ Req {res_flex['As_Definitivo_Requerido']} cm2 (OK)")
    else:
        col3.error(f"Acero Insuficiente: Se requieren mínimo {res_flex['As_Definitivo_Requerido']} cm2")

    st.divider()
    
    # Tabla de presiones generada por el módulo de geotecnia
    st.subheader("Desglose de Presiones Efectivas del Terreno")
    st.dataframe(presiones, use_container_width=True)
    
    # Alerta inteligente
    if res_flex["Alerta_Canto"] != "OK":
        st.warning(f"⚠️ Aviso Estructural: {res_flex['Alerta_Canto']}")