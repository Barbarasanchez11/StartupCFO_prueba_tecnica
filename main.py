from src.loader import get_prepared_data
from src.processor import find_missing_records
from src.classifier import classify_missing_records
from src.writer import save_to_excel
from src.config import INPUT_PL_FILE
from src.logger import setup_logger

logger = setup_logger("StartupCFO", use_rich=True)

def main():
    logger.info("=" * 50)
    logger.info("StartupCFO Tool - Accounting Reconciliation")
    logger.info("=" * 50)

    try:
        input_df, mayor_df = get_prepared_data()
    except ValueError as e:
        logger.error(f"{e}")
        return

    if input_df is not None and mayor_df is not None:
        from src.validator import audit_data_quality
        all_warnings = audit_data_quality(input_df, "InputPL") + audit_data_quality(mayor_df, "Mayor")
        if all_warnings:
            logger.warning("\nSe han detectado problemas de calidad en los datos:")
            for warning in all_warnings:
                logger.warning(f"  {warning}")
            logger.info("")

        has_duplicates = any("duplicados exactos" in warning.lower() for warning in all_warnings)
        if has_duplicates:
            logger.info("\nSe han detectado duplicados exactos en los datos.")
            response = input("¿Desea eliminar duplicados exactos automáticamente? (s/n): ").strip().lower()
            
            if response == 's' or response == 'y' or response == 'yes' or response == 'si':
                from src.validator import remove_exact_duplicates

                input_df, removed_input, msg_input = remove_exact_duplicates(input_df, "InputPL")
                if msg_input:
                    logger.info(f"  {msg_input}")

                mayor_df, removed_mayor, msg_mayor = remove_exact_duplicates(mayor_df, "Mayor")
                if msg_mayor:
                    logger.info(f"  {msg_mayor}")
                
                total_removed = removed_input + removed_mayor
                if total_removed > 0:
                    logger.success(f"Se eliminaron {total_removed} duplicados en total. Continuando con datos limpios...\n")
            else:
                logger.info("Continuando sin eliminar duplicados...\n")

        new_movements = find_missing_records(input_df, mayor_df)

        if new_movements is not None and len(new_movements) > 0:

            classified_df = classify_missing_records(new_movements, input_df)

            save_to_excel(classified_df, INPUT_PL_FILE)
            
        else:
            logger.info("No new records found to add. Everything is up to date!")
            
    else:
        logger.error("Flow stopped because of missing or corrupt files.")

    logger.info("=" * 50)

if __name__ == "__main__":
    main()
