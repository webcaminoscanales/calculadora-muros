# app.py
# Interfaz de Usuario Maquetación Definitiva

import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Acero y Código | Muros", layout="wide")

# 2. Cabecera
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    st.info("Espacio LOGO")
with col_titulo:
    st.title("🏗️ Cálculo Avanzado de Muros de Contención")
    st.markdown("Definición completa de geometría, terreno y cargas.")

st.divider()

# 3. CONTENEDOR DE PESTAÑAS (El secreto para no agobiar al usuario)
tab1, tab2, tab3, tab4 = st.tabs(["📏 1. Geometría", "🌍 2. Terreno y Agua", "⬇️ 3. Cargas", "⚙️ 4. Materiales"])

# --- PESTAÑA 1: GEOMETRÍA ---
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
        st.info(f"Ancho total de la zapata calculado: {round(e_base + vuelo_puntera + vuelo_talon, 2)} m")

# --- PESTAÑA 2: TERRENO Y AGUA ---
with tab2:
    st.markdown("#### Estratigrafía del Trasdós")
    st.caption("Añade o elimina las capas de terreno que necesites. El espesor total debe igualar o superar la altura del muro.")
    
    # Creamos un DataFrame base para que el usuario edite
    datos_terreno_base = pd.DataFrame(
        [
            {"Estrato": "Relleno", "Espesor (m)": 3.4, "Densidad (kN/m3)": 18.0, "Fricción (º)": 30.0, "Cohesión (kPa)": 0.0},
        ]
    )
    # st.data_editor es la magia: un mini-excel editable en la web
    estratos_df = st.data_editor(datos_terreno_base, num_rows="dynamic", use_container_width=True)
    
    st.divider()
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("#### Superficie y Talud")
        beta = st.slider("Inclinación del talud en trasdós (º)", min_value=0, max_value=45, value=0)
    with col_t2:
        st.markdown("#### Nivel Freático")
        hay_agua = st.checkbox("Presencia de Nivel Freático")
        if hay_agua:
            cota_agua = st.number_input("Profundidad del agua desde coronación (m)", value=2.0, step=0.1)
            st.warning("⚠️ El empuje hidrostático se sumará al empuje de tierras.")

# --- PESTAÑA 3: CARGAS ---
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

# --- PESTAÑA 4: MATERIALES ---
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

# Botón de ejecución temporalmente visual
st.button("🚀 Ejecutar Cálculo Completo (Desactivado por ahora)", type="primary", use_container_width=True, disabled=True)