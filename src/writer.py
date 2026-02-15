import openpyxl
from openpyxl.styles import PatternFill
import os
from src.config import OUTPUT_FILE, INPUT_PL_FILE, INPUT_PL_COLS

def save_to_excel(classified_df, template_path, input_df=None):
    """
    Open the original Excel, find the END row, and insert new data with styling.
    If input_df is provided, also rewrite existing rows to fix corrupted values.
    """
    if classified_df is None or len(classified_df) == 0:
        print("[INFO] No data to write.")
        return

    # 1. Abro el Excel original que me sirve de plantilla
    # 🔧 FIX: Usar data_only=True para leer solo valores mostrados (no fórmulas)
    print(f"[INFO] Opening template: {template_path}")
    wb = openpyxl.load_workbook(template_path, data_only=True, keep_vba=False)
    sheet = wb.active

    # 2. Busco en qué fila está el 'END' para saber dónde insertar
    end_row = None
    # Miro en la columna 1 (Nº Asiento) que es donde suele estar el END
    for row in range(1, sheet.max_row + 1):
        cell_val = str(sheet.cell(row=row, column=1).value).strip().upper()
        if cell_val == 'END':
            end_row = row
            break
    
    # Si no lo encuentro, pues escribo al final y ya está
    if end_row is None:
        end_row = sheet.max_row + 1
        print("[WARNING] Could not find 'END' row. Writing at the end of the sheet.")
    else:
        print(f"[INFO] Found 'END' at row {end_row}. Inserting {len(classified_df)} rows...")
    
    # 🔧 FIX: Si tenemos input_df, reescribir las filas existentes para corregir valores corruptos
    if input_df is not None and end_row > 2:  # end_row > 2 porque fila 1 es header
        print(f"[INFO] Fixing existing rows (1 to {end_row-1}) from normalized DataFrame...")
        # Reescribir filas existentes desde el DataFrame normalizado (que tiene valores correctos)
        for df_idx, (_, row_data) in enumerate(input_df.iterrows(), start=2):  # start=2 porque fila 1 es header
            if df_idx >= end_row:  # No tocar las filas que vamos a insertar
                break
            for col_idx, col_name in enumerate(INPUT_PL_COLS, start=1):
                if col_name in row_data:
                    cell_value = row_data[col_name]
                    cell = sheet.cell(row=df_idx, column=col_idx)
                    
                    # Aplicar formatos correctos a filas existentes también
                    if col_name == 'Fecha' and hasattr(cell_value, 'to_pydatetime'):
                        cell.value = cell_value.to_pydatetime()
                        cell.number_format = 'DD/MM/YYYY'
                    elif col_name == 'Mes':
                        # 🔧 FIX CRÍTICO: Formato texto también para filas existentes
                        cell.number_format = '@'
                        cell.value = str(cell_value) if cell_value else ""
                    elif col_name in ['Debe', 'Haber', 'Saldo', 'Neto']:
                        cell.value = cell_value
                        cell.number_format = '#,##0.00'
                    else:
                        cell.value = cell_value

    # 3. 🔧 FIX: Insertar filas pero preservar formatos existentes
    # Primero, desplazamos la fila END hacia abajo insertando filas vacías
    sheet.insert_rows(end_row, amount=len(classified_df))

    # 4. Empiezo a rellenar SOLO las nuevas filas insertadas (no toco las existentes)
    # Creo un estilo amarillo para resaltar los que tienen poca confianza
    warning_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")

    for i, (index, row_data) in enumerate(classified_df.iterrows()):
        current_row = end_row + i
        
        # Voy columna por columna según mi configuración
        for col_idx, col_name in enumerate(INPUT_PL_COLS, start=1):
            if col_name in row_data:
                cell_value = row_data[col_name]
                
                # Si es una fecha la convierto para que Excel no se vuelva loco
                if col_name == 'Fecha' and hasattr(cell_value, 'to_pydatetime'):
                    cell_value = cell_value.to_pydatetime()
                
                # 🔧 FIX: Obtener la celda y establecer valor y formato SOLO para nuevas filas
                cell = sheet.cell(row=current_row, column=col_idx)
                
                # Formateo específico según el tipo de columna (SOLO para nuevas filas)
                if col_name == 'Fecha':
                    cell.value = cell_value
                    cell.number_format = 'DD/MM/YYYY'
                
                elif col_name == 'Mes':
                    # 🔧 FIX CRÍTICO: Formato texto para evitar interpretación como fecha
                    # Excel interpreta "abr/25" como fecha, necesitamos forzar texto
                    # IMPORTANTE: Solo aplicamos esto a las NUEVAS celdas, no tocamos las existentes
                    cell.number_format = '@'  # @ es el código de formato texto en Excel
                    cell.value = str(cell_value) if cell_value else ""
                
                elif col_name in ['Debe', 'Haber', 'Saldo', 'Neto']:
                    cell.value = cell_value
                    cell.number_format = '#,##0.00'
                else:
                    # Para otras columnas, simplemente escribir el valor
                    cell.value = cell_value
                
                # Si la confianza es bajita, lo pinto de amarillo para avisar
                if row_data.get('Confidence', 100) < 80:
                    cell.fill = warning_fill

    # 5. Guardo el archivo final
    # Primero me aseguro de que la carpeta de salida existe
    output_dir = os.path.dirname(OUTPUT_FILE)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"[INFO] Saving results to: {OUTPUT_FILE}")
    wb.save(OUTPUT_FILE)
    print("[SUCCESS] Process completed! Check the output folder.")
