import openpyxl
from openpyxl.styles import PatternFill
import os
from src.config import OUTPUT_FILE, INPUT_PL_FILE, INPUT_PL_COLS

def save_to_excel(classified_df, template_path):
    """
    Open the original Excel, find the END row, and insert new data with styling.
    """
    if classified_df is None or len(classified_df) == 0:
        print("[INFO] No data to write.")
        return

    # 1. Abro el Excel original que me sirve de plantilla
    print(f"[INFO] Opening template: {template_path}")
    wb = openpyxl.load_workbook(template_path)
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

    # 3. Hago el hueco insertando filas vacías arriba del END
    sheet.insert_rows(end_row, amount=len(classified_df))

    # 4. Empiezo a rellenar celda por celda
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
                
                # Meto el valor en la celda
                cell = sheet.cell(row=current_row, column=col_idx, value=cell_value)
                
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
