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
        status.info(" Paso 1: Cargando y normalizando datos...")
        try:
            input_df, mayor_df = get_prepared_data(input_file, mayor_file)
        except ValueError as e:
            status.error(str(e))
            st.stop()
        
        if input_df is not None and mayor_df is not None:
            # 1.1 Auditoría de Calidad
            from src.validator import audit_data_quality
            all_warnings = audit_data_quality(input_df, "InputPL") + audit_data_quality(mayor_df, "Mayor")
            
            if all_warnings:
                with st.expander("**Avisos de Calidad de Datos** (Pulsa para ver detalles)", expanded=False):
                    for warning in all_warnings:
                        st.write(warning)
                    st.caption("Nota: El proceso continuará, pero se recomienda revisar estos puntos.")
            
            # 2. Comparación
            status.info(" Paso 2: Buscando registros faltantes en el histórico...")
            new_movements = find_missing_records(input_df, mayor_df)
            
            if new_movements is not None and len(new_movements) > 0:
                st.success(f" **Análisis finalizado:** Se han detectado **{len(new_movements)}** movimientos nuevos en el Mayor que no estaban en el InputPL.")
                
                # 3. Clasificación
                status.info(" Paso 3: Clasificando nuevos gastos (IA Fuzzy Logic)...")
                classified_df = classify_missing_records(new_movements, input_df)
                
                # Vista completa de lo nuevo
                st.write("###  Nuevos registros clasificados")
                st.info("A continuación se muestran solo los registros que se van a añadir al archivo final:")
                st.dataframe(classified_df, width='stretch')
                
                # 4. Escritura
                status.info(" Paso 4: Generando archivo Excel con formato...")
                # Usamos el archivo de entrada como plantilla directamente
                save_to_excel(classified_df, input_file)
                
                status.success(" ¡Todo listo! El histórico ha sido actualizado.")
                
                st.markdown("---")
                st.write("### Descarga de resultados")
                st.write("El siguiente botón generará el archivo **InputPL completo**, incluyendo los datos originales y estos nuevos registros clasificados en su lugar correspondiente.")
                
                # 5. Botón de Descarga
                with open(OUTPUT_FILE, "rb") as file:
                    st.download_button(
                        label="Descargar Excel Actualizado (.xlsx)",
                        data=file,
                        file_name="InputPL_Actualizado.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width='stretch'
                    )
            else:
                status.warning("No hay registros nuevos que añadir. El histórico ya está actualizado.")
        else:
            status.error("Error crítico al procesar los archivos. Por favor, revisa el formato de los Excel.")
    else:
        st.warning("Por favor, sube ambos archivos para continuar.")
