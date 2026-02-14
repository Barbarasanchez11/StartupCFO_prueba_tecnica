import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="StartupCFO Tool | Automatización Contable",

    layout="centered"
)

# Estilos personalizados para un look premium
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
    }
    .stHeader {
        color: #1e3a8a;
    }
    </style>
    """, unsafe_allow_html=True)

# Título y descripción
st.title("StartupCFO Tool")
st.subheader("Automatización de Conciliación y Clasificación Contable")

st.markdown("""
Esta herramienta permite procesar los archivos de gastos de manera automática. 
Sigue los pasos a continuación para actualizar tu histórico y clasificar nuevos registros.

**Instrucciones:**
1. Sube el archivo **InputPL** (Excel principal).
2. Sube el archivo del **Mayor** (Histórico acumulado).
3. Haz clic en **'Ejecutar Proceso'** para generar el archivo actualizado.
""")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.write("### 1. InputPL")
    input_file = st.file_uploader("Sube el archivo de entrada", type=['xlsx'], key="input")

with col2:
    st.write("### 2. Mayor")
    mayor_file = st.file_uploader("Sube el histórico del Mayor", type=['xlsx'], key="mayor")

st.divider()

if st.button(" Ejecutar Proceso"):
    if input_file and mayor_file:
        st.success("Archivos cargados correctamente. ¡Listo para procesar!")
        # Aquí conectaremos con la lógica en el siguiente paso
    else:
        st.warning("Por favor, sube ambos archivos para continuar.")
