from src.loader import get_prepared_data

def main():
    print("--- Startup CFO Automation Tool ---")
    
    # Step 1: Loading and Normalizing data
    # We call the function from loader.py
    input_df, mayor_df = get_prepared_data()
    
    # Quick check: How do our dataframes look?
    if input_df is not None:
        print("[DEBUG] InputPL is ready in memory.")
    else:
        print("[DEBUG] InputPL is missing (Expected for now).")
        
    if mayor_df is not None:
        print("[DEBUG] Mayor is ready and normalized.")
    else:
        print("[DEBUG] Mayor is missing (Expected for now).")

    print("-----------------------------------")
    print("End of data loading step.")

if __name__ == "__main__":
    main()
