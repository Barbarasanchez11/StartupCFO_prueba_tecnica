# Tests Unitarios

Este directorio contiene los tests unitarios del proyecto.

## Instalación

Asegúrate de tener `pytest` instalado:

```bash
pip install pytest
```

O instala todas las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecutar Tests

### Ejecutar todos los tests:

```bash
pytest tests/ -v
```

### Ejecutar un archivo específico:

```bash
pytest tests/test_loader.py -v
pytest tests/test_validator.py -v
pytest tests/test_processor.py -v
```

### Ejecutar una clase específica:

```bash
pytest tests/test_loader.py::TestNormalizeData -v
```

### Ejecutar un test específico:

```bash
pytest tests/test_validator.py::TestRemoveExactDuplicates::test_remove_exact_duplicates_removes_duplicates -v
```

### Ejecutar con cobertura:

Primero instala `pytest-cov`:
```bash
pip install pytest-cov
```

Luego ejecuta:
```bash
pytest tests/ --cov=src --cov-report=html
```

## Estructura de Tests

- **`conftest.py`**: Fixtures compartidas (DataFrames de ejemplo)
- **`test_loader.py`**: Tests para carga y normalización de datos
- **`test_validator.py`**: Tests para validación y limpieza de datos
- **`test_processor.py`**: Tests para comparación y procesamiento

## Cobertura de Tests

Los tests cubren:

✅ Normalización de datos (fechas, Mes, columnas)
✅ Validación de columnas
✅ Detección de problemas de calidad (negativos, vacíos, duplicados)
✅ Eliminación de duplicados exactos
✅ Comparación de registros entre InputPL y Mayor
✅ Manejo de casos edge (None, vacíos, END rows)

## Ejemplos de Tests

### Test de Normalización

```python
def test_normalize_data_derives_mes_from_fecha(df_with_empty_mes):
    """Test: derivar Mes desde Fecha cuando Mes está vacío."""
    result = normalize_data(df_with_empty_mes.copy(), is_mayor=False)
    assert result['Mes'].iloc[0] == 'ene/25'
```

### Test de Eliminación de Duplicados

```python
def test_remove_exact_duplicates_removes_duplicates(df_with_duplicates):
    """Test: eliminar duplicados exactos correctamente."""
    df_cleaned, removed_count, message = remove_exact_duplicates(df_with_duplicates, "Test")
    assert removed_count == 3
```

