import openpyxl
from openpyxl.styles import PatternFill
import os
from src.config import OUTPUT_FILE, INPUT_PL_FILE, INPUT_PL_COLS
from src.logger import get_logger

logger = get_logger(__name__)

def save_to_excel(classified_df, template_path, input_df=None):
    """
    Open the original Excel, find the END row, and insert new data with styling.
    If input_df is provided, also rewrite existing rows to fix corrupted values.
    """
    if classified_df is None or len(classified_df) == 0:
        logger.info("No data to write.")
        return

    logger.info(f"Opening template: {template_path}")
    wb = openpyxl.load_workbook(template_path, data_only=True, keep_vba=False)
    sheet = wb.active

    end_rows = []
    for row in range(1, sheet.max_row + 1):
        cell_val = str(sheet.cell(row=row, column=1).value).strip().upper()
        if cell_val == 'END':
            end_rows.append(row)

    if not end_rows:
        end_row = sheet.max_row + 1
        first_end_row = end_row
        logger.warning("Could not find 'END' row. Writing at the end of the sheet.")
    else:
        first_end_row = min(end_rows)
        end_row = first_end_row
        
        if len(end_rows) > 1:
            logger.info(f"Found {len(end_rows)} 'END' rows. Removing all except the first one at row {first_end_row}.")
            for row_to_delete in sorted(end_rows[1:], reverse=True):
                sheet.delete_rows(row_to_delete)
            logger.info(f"Cleaned up. Using 'END' at row {end_row} as insertion point.")
        else:
            logger.info(f"Found 'END' at row {end_row}. Inserting {len(classified_df)} rows...")
    
   
    if input_df is not None and first_end_row > 2:  
        logger.info(f"Fixing existing rows (1 to {first_end_row-1}) from normalized DataFrame...")
        for df_idx, (_, row_data) in enumerate(input_df.iterrows(), start=2):  
            if df_idx >= first_end_row:
                break
            if str(row_data.get('Nº Asiento', '')).strip().upper() == 'END':
                continue
            for col_idx, col_name in enumerate(INPUT_PL_COLS, start=1):
                if col_name in row_data:
                    cell_value = row_data[col_name]
                    cell = sheet.cell(row=df_idx, column=col_idx)

                    if col_name == 'Fecha' and hasattr(cell_value, 'to_pydatetime'):
                        cell.value = cell_value.to_pydatetime()
                        cell.number_format = 'DD/MM/YYYY'
                    elif col_name == 'Mes':
                      
                        cell.number_format = '@'
                        cell.value = str(cell_value) if cell_value else ""
                    elif col_name in ['Debe', 'Haber', 'Saldo', 'Neto']:
                        cell.value = cell_value
                        cell.number_format = '#,##0.00'
                    else:
                        cell.value = cell_value

    sheet.insert_rows(end_row, amount=len(classified_df))

    end_row_after_insert = end_row + len(classified_df)
    if end_row_after_insert <= sheet.max_row:
        cell_val_after = str(sheet.cell(row=end_row_after_insert, column=1).value).strip().upper()
        if cell_val_after == 'END':
            logger.info(f"Removing intermediate 'END' row at {end_row_after_insert} (now in the middle after insertion).")
            sheet.delete_rows(end_row_after_insert)

    warning_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")

    for i, (index, row_data) in enumerate(classified_df.iterrows()):
        current_row = end_row + i

        for col_idx, col_name in enumerate(INPUT_PL_COLS, start=1):
            if col_name in row_data:
                cell_value = row_data[col_name]

                if col_name == 'Fecha' and hasattr(cell_value, 'to_pydatetime'):
                    cell_value = cell_value.to_pydatetime()
                
            
                cell = sheet.cell(row=current_row, column=col_idx)

                if col_name == 'Fecha':
                    cell.value = cell_value
                    cell.number_format = 'DD/MM/YYYY'
                
                elif col_name == 'Mes':
                    
                    cell.number_format = '@' 
                    cell.value = str(cell_value) if cell_value else ""
                
                elif col_name in ['Debe', 'Haber', 'Saldo', 'Neto']:
                    cell.value = cell_value
                    cell.number_format = '#,##0.00'
                else:
                    cell.value = cell_value

                if row_data.get('Confidence', 100) < 80:
                    cell.fill = warning_fill

    output_dir = os.path.dirname(OUTPUT_FILE)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logger.info(f"Saving results to: {OUTPUT_FILE}")
    wb.save(OUTPUT_FILE)
    logger.success("Process completed! Check the output folder.")
