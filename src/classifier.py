import pandas as pd
from thefuzz import process, fuzz

def create_knowledge_base(historical_df):
    """
    Create a mapping dictionary between Concept and Expense Type based on historical data.
    """
    # Me quedo solo con lo que ya está clasificado
    clean_history = historical_df.dropna(subset=['Concepto', 'Tipo de gasto'])
    
    # Hago el mapa de Concepto -> Tipo de gasto
    mapping = dict(zip(clean_history['Concepto'], clean_history['Tipo de gasto']))
    
    return mapping

def get_suggestion(concept, mapping, threshold=70):
    """
    Find the best category match for a new concept using fuzzy string matching.
    """
    # Primero pruebo si está clavado el nombre
    if concept in mapping:
        return mapping[concept], 100

    # Si no es exacto, tiro de fuzzy logic con el resto de conceptos que conozco
    concepts_known = list(mapping.keys())
    
    if not concepts_known:
        return "NEW - NEEDS REVIEW", 0

    # Busco el que más se parezca ignorando el orden de las palabras
    best_match, score = process.extractOne(concept, concepts_known, scorer=fuzz.token_set_ratio)

    # Si se parece bastante (mas del 70%) lo sugiero
    if score >= threshold:
        return mapping[best_match], score
    
    # Si es muy raro mejor marcarlo para revisar a mano
    return "NEW - NEEDS REVIEW", score

def classify_missing_records(new_df, historical_df):
    """
    Main function to fill 'Tipo de gasto' and 'Confidence' for new accounting movements.
    """
    if new_df is None or len(new_df) == 0:
        return new_df

    print("[INFO] Learning from historical accounting movements...")
    knowledge_base = create_knowledge_base(historical_df)

    print(f"[INFO] Classifying {len(new_df)} new movements...")
    
    # Ejecuto la sugerencia para cada concepto nuevo
    results = new_df['Concepto'].apply(lambda x: get_suggestion(str(x), knowledge_base))
    
    # Guardo la categoria y la confianza en columnas nuevas
    new_df['Tipo de gasto'] = [res[0] for res in results]
    new_df['Confidence'] = [res[1] for res in results]

    print("[SUCCESS] Classification finished successfully.")
    
    return new_df
