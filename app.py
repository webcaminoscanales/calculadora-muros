# app.py
# Interfaz de Usuario Mejorada (SaaS Cálculo Estructural)

import streamlit as st
import normativa
import geotecnia
import hormigon

# 1. Configuración de la página
st.set_page_config(page_title="Acero y Código | Muros", layout="wide", initial_sidebar_state="collapsed")

# 2. Cabecera con Logo y Título
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.info("Espacio para LOGO")

with col_titulo:
    st.title("🏗️ Cálculo Avanzado de Muros de Contención")
    st.markdown("Verificación de estabilidad y armaduras según **Código Estructural**.")

st.divider()

# 3. Panel Central (Bloques Horizontales)
st.markdown("### 🛠️ Parámetros de Entrada")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📏 1. Geometría")
    h_muro = st.number_input("Altura del alzado (m)", value=3.0, step=0.1)
    b_zapata = st.number_input("Ancho total de zapata (m)", value=1.5, step=0.1)
    canto_zapata = st.number_input("Canto de la zapata (m)", value=0.4, step=0.1)

with col2:
    st.markdown("#### 🌍 2. Datos Geotécnicos")
    phi = st.number_input("Ángulo de rozamiento interno (º)", value=30.0, step=1.0)
    c_cohesion = st.number_input("Cohesión (kPa)", value=0.0, step=1.0)
    gamma_terr = st.number_input("Peso específico terreno (kN/m3)", value=18.0, step=0.1)
    beta = st.slider("Inclinación del talud en trasdós (º)", min_value=0, max_value=45, value=0)

with col3:
    st.markdown("#### ⚙️ 3. Armado Propuesto")
    fck = st.selectbox("Resistencia del Hormigón (MPa)", [25, 30, 35, 40])
    fyk = st.selectbox("Límite elástico Acero (MPa)", [500])
    as_propuesto = st.number_input("Cuantía de Acero (cm2/m)", value=12.0, step=0.5)

st.divider()

# 4. Botón de Cálculo Centrado
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    ejecutar = st.button("🚀 Ejecutar Cálculo Normativo", type="primary", use_container_width=True)

if ejecutar:
    estratos = [{"espesor": h_muro, "phi": phi, "c": c_cohesion, "gamma": gamma_terr}]
    
    with st.spinner('Iterando matriz de combinaciones ELU/ELS...'):
        presiones = geotecnia.calcular_presiones_terreno(estratos, beta)
        
        m_est = (gamma_terr * h_muro * b_zapata) * (b_zapata / 2) 
        m_des = presiones[-1]["p_tierra"] * (h_muro**2) / 6 
        f_roce = (gamma_terr * h_muro * b_zapata) * 0.5
        f_desliza = presiones[-1]["p_tierra"] * h_muro / 2
        m_ed_base = m_des * 1.35 
        
        res_estab = hormigon.comprobar_estabilidad(m_est, m_des, f_roce, f_desliza)
        res_flex = hormigon.verificar_cuantia_flexion(m_ed_base, 1.0, b_zapata-0.05, fck, fyk, as_propuesto)

    # 5. Salida de Resultados (El Dashboard de Mando)
    st.subheader("📊 Envolventes Críticas y Estabilidad")
    
    col_res1, col_res2, col_res3 = st.columns(3)
    
    if res_estab["Cumple_Vuelco"]:
        col_res1.success(f"✔️ CS Vuelco: {res_estab['CS_Vuelco']} ≥ 1.50")
    else:
        col_res1.error(f"❌ CS Vuelco: {res_estab['CS_Vuelco']} < 1.50")
        
    if res_estab["Cumple_Deslizamiento"]:
        col_res2.success(f"✔️ CS Desliz: {res_estab['CS_Deslizamiento']} ≥ 1.50")
    else:
        col_res2.error(f"❌ CS Desliz: {res_estab['CS_Deslizamiento']} < 1.50")
        
    if res_flex["Cumple"]:
        col_res3.success(f"✔️ Acero: Propuesto {as_propuesto} cm² ≥ Req {res_flex['As_Definitivo_Requerido']} cm²")
    else:
        col_res3.error(f"❌ Acero Insuficiente: Mínimo {res_flex['As_Definitivo_Requerido']} cm²")

    # Alerta inteligente
    if res_flex["Alerta_Canto"] != "OK":
        st.warning(f"⚠️ Aviso Estructural: {res_flex['Alerta_Canto']}")

    st.divider()
    
    # 6. MEMORIA DE CÁLCULO (Modo Tonto / Educativo)
    st.markdown("### 📄 Memoria de Cálculo Detallada")
    
    with st.expander("Ver justificación paso a paso", expanded=False):
        
        st.markdown("#### 1. Cálculo de Empujes (Geotecnia)")
        st.markdown("Desglose de las presiones efectivas del terreno en el trasdós del muro:")
        st.dataframe(presiones, use_container_width=True)
        
        st.markdown("#### 2. Comprobaciones de Estabilidad (ELS)")
        st.markdown(f"**Momento Estabilizador ($M_{{est}}$):** {round(m_est, 2)} kN·m")
        st.markdown(f"**Momento Desestabilizador ($M_{{des}}$):** {round(m_des, 2)} kN·m")
        
        # Fórmula en LaTeX
        st.latex(r"CS_{vuelco} = \frac{M_{est}}{M_{des}} = \frac{" + str(round(m_est,2)) + "}{" + str(round(m_des,2)) + "} = " + str(round(res_estab['CS_Vuelco'], 2)))
        
        st.markdown("#### 3. Dimensionamiento a Flexión (ELU)")
        st.markdown(f"**Momento de Diseño Mayorado ($M_{{Ed}}$):** {round(m_ed_base, 2)} kN·m")
        st.markdown(f"**Armadura estrictamente necesaria por cálculo:** {res_flex['As_Calculo_Puro_cm2']} cm²/m")
        st.markdown(f"**Armadura mínima geométrica normativa:** {res_flex['As_Minimo_Norma_cm2']} cm²/m")
        
        st.info("💡 **Nota Normativa:** El Código Estructural exige adoptar el valor máximo entre el cálculo puro y los mínimos geométricos para garantizar la ductilidad de la sección y evitar roturas frágiles.")