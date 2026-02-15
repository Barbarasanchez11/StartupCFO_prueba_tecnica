import pandas as pd
from thefuzz import process, fuzz
from src.logger import get_logger

logger = get_logger(__name__)

def create_knowledge_base(historical_df):
    """
    Create a mapping dictionary between Concept and Expense Type based on historical data.
    """
   
    clean_history = historical_df.dropna(subset=['Concepto', 'Tipo de gasto'])
    
    mapping = dict(zip(clean_history['Concepto'], clean_history['Tipo de gasto']))
    
    return mapping

def get_suggestion(concept, mapping, threshold=70):
    """
    Find the best category match for a new concept using fuzzy string matching.
    """
   
    if concept in mapping:
        return mapping[concept], 100

    concepts_known = list(mapping.keys())
    
    if not concepts_known:
        return "NEW - NEEDS REVIEW", 0

    best_match, score = process.extractOne(concept, concepts_known, scorer=fuzz.token_set_ratio)

    if score >= threshold:
        return mapping[best_match], score
    
    return "NEW - NEEDS REVIEW", score

def classify_missing_records(new_df, historical_df):
    """
    Main function to fill 'Tipo de gasto' and 'Confidence' for new accounting movements.
    """
    if new_df is None or len(new_df) == 0:
        return new_df

    logger.info("Learning from historical accounting movements...")
    knowledge_base = create_knowledge_base(historical_df)

    logger.info(f"Classifying {len(new_df)} new movements...")

    results = new_df['Concepto'].apply(lambda x: get_suggestion(str(x), knowledge_base))

    new_df['Tipo de gasto'] = [res[0] for res in results]
    new_df['Confidence'] = [res[1] for res in results]

    logger.success("Classification finished successfully.")
    
    return new_df
