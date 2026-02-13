INPUT_PL_FILE = "data/raw/InputPL.xlsx"
MAYOR_FILE = "data/raw/Mayor_TSCFO.xlsx"
OUTPUT_FILE = "data/output/InputPL_Updated.xlsx"


INPUT_PL_COLS = [
    "Nº Asiento", "Fecha", "Documento", "Concepto", "Cuenta", 
    "Debe", "Haber", "Saldo", "Nombre cuenta", "Neto", 
    "Mes", "Tipo de gasto", "END"
]

COLUMN_MAPPING = {
    "Net": "Neto",
    "Month": "Mes"
}

UNIQUE_IDENTIFIERS = ["Nº Asiento", "Fecha", "Saldo"]
