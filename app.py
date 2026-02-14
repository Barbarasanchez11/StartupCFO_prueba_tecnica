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

from src.loader import get_prepared_data
from src.processor import find_missing_records
from src.classifier import classify_missing_records
from src.writer import save_to_excel
from src.config import OUTPUT_FILE

if st.button(" Ejecutar Proceso"):
    if input_file and mayor_file:
        # Contenedor para ir mostrando el progreso
        status = st.empty()
        
        # 1. Carga y Normalización
        status.info("⏳ Paso 1: Cargando y normalizando datos...")
        input_df, mayor_df = get_prepared_data(input_file, mayor_file)
        
        if input_df is not None and mayor_df is not None:
            
            # 2. Comparación
            status.info("⏳ Paso 2: Buscando registros faltantes en el histórico...")
            new_movements = find_missing_records(input_df, mayor_df)
            
            if new_movements is not None and len(new_movements) > 0:
                st.write(f"✅ Se han encontrado **{len(new_movements)}** nuevos movimientos.")
                
                # 3. Clasificación
                status.info("⏳ Paso 3: Clasificando nuevos gastos (IA Fuzzy Logic)...")
                classified_df = classify_missing_records(new_movements, input_df)
                
                # Vista previa de lo nuevo
                st.write("**Vista previa de los registros clasificados:**")
                st.dataframe(classified_df.head(10))
                
                # 4. Escritura
                status.info("⏳ Paso 4: Generando archivo Excel con formato...")
                # Usamos el archivo de entrada como plantilla directamente
                save_to_excel(classified_df, input_file)
                
                status.success("🚀 ¡Proceso completado con éxito!")
                
                # 5. Botón de Descarga
                with open(OUTPUT_FILE, "rb") as file:
                    st.download_button(
                        label="📥 Descargar Excel Actualizado",
                        data=file,
                        file_name="InputPL_Actualizado.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                status.warning("No hay registros nuevos que añadir. El histórico ya está actualizado.")
        else:
            status.error("Error crítico al procesar los archivos. Por favor, revisa el formato de los Excel.")
    else:
        st.warning("Por favor, sube ambos archivos para continuar.")
