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

# Inicializar session_state si no existe
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'input_df' not in st.session_state:
    st.session_state.input_df = None
if 'mayor_df' not in st.session_state:
    st.session_state.mayor_df = None
if 'all_warnings' not in st.session_state:
    st.session_state.all_warnings = []

# Botón para cargar y analizar datos
if st.button(" Ejecutar Proceso"):
    if input_file and mayor_file:
        # Contenedor para ir mostrando el progreso
        status = st.empty()
        
        # 1. Carga y Normalización
        status.info(" Paso 1: Cargando y normalizando datos...")
        try:
            input_df, mayor_df = get_prepared_data(input_file, mayor_file)
            
            # Guardar en session_state
            st.session_state.input_df = input_df
            st.session_state.mayor_df = mayor_df
            st.session_state.data_loaded = True
            
            # 1.1 Auditoría de Calidad
            from src.validator import audit_data_quality
            all_warnings = audit_data_quality(input_df, "InputPL") + audit_data_quality(mayor_df, "Mayor")
            st.session_state.all_warnings = all_warnings
            
        except ValueError as e:
            status.error(str(e))
            st.session_state.data_loaded = False
            st.stop()
    else:
        st.warning("Por favor, sube ambos archivos para continuar.")
        st.session_state.data_loaded = False

# Si los datos están cargados, mostrar avisos y opciones de limpieza
if st.session_state.data_loaded and st.session_state.input_df is not None and st.session_state.mayor_df is not None:
    input_df = st.session_state.input_df
    mayor_df = st.session_state.mayor_df
    all_warnings = st.session_state.all_warnings
    
    if all_warnings:
        with st.expander("**Avisos de Calidad de Datos** (Pulsa para ver detalles)", expanded=False):
            for warning in all_warnings:
                st.write(warning)
            st.caption("Nota: El proceso continuará, pero se recomienda revisar estos puntos.")
    
    # Opción de Limpieza de Duplicados
    has_duplicates = any("duplicados exactos" in warning.lower() for warning in all_warnings)
    if has_duplicates:
        st.markdown("### Opciones de Limpieza")
        remove_duplicates = st.checkbox(
            "Eliminar duplicados exactos automáticamente",
            value=False,
            key="remove_duplicates_checkbox",
            help="Se eliminarán los registros con mismo Nº Asiento, Fecha y Saldo. Se mantendrá solo la primera ocurrencia de cada grupo."
        )
        
        if remove_duplicates:
            from src.validator import remove_exact_duplicates
            
            # Limpiar InputPL
            input_df, removed_input, msg_input = remove_exact_duplicates(input_df, "InputPL")
            if msg_input:
                st.info(msg_input)
            
            # Limpiar Mayor
            mayor_df, removed_mayor, msg_mayor = remove_exact_duplicates(mayor_df, "Mayor")
            if msg_mayor:
                st.info(msg_mayor)
            
            total_removed = removed_input + removed_mayor
            if total_removed > 0:
                st.success(f"✅ Se eliminaron {total_removed} duplicados en total. Los datos están listos para procesar.")
                # Actualizar session_state con datos limpios
                st.session_state.input_df = input_df
                st.session_state.mayor_df = mayor_df
    
    # Botón para continuar con el procesamiento
    if st.button("Continuar con el Procesamiento", key="continue_button"):
        status = st.empty()
        
        # Usar los datos actuales (pueden estar limpios si se marcó el checkbox)
        input_df = st.session_state.input_df
        mayor_df = st.session_state.mayor_df
        
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
               
                save_to_excel(classified_df, input_file, input_df=input_df)
                
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
            
