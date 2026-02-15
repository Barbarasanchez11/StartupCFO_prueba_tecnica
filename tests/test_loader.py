"""
Unit tests for data loading and normalization functions.
"""
import pandas as pd
import pytest
from datetime import datetime
from src.loader import normalize_data, validate_columns
from src.config import INPUT_PL_COLS, COLUMN_MAPPING


class TestNormalizeData:
    """Tests for the normalize_data function."""
    
    def test_normalize_data_with_valid_mes(self):
        """Test: normalize data preserving Mes values when they are valid dates."""
  
        df = pd.DataFrame({
            'Nº Asiento': [1, 2],
            'Fecha': pd.to_datetime(['2025-01-15', '2025-02-20']),
            'Mes': pd.to_datetime(['2025-01-01', '2025-02-01']),  # Valid dates
            'Concepto': ['A', 'B']
        })
        
        result = normalize_data(df.copy(), is_mayor=False)
        
        assert result is not None
        assert 'Mes' in result.columns
    
        assert result['Mes'].iloc[0] == 'ene/25'
        assert result['Mes'].iloc[1] == 'feb/25'
    
    def test_normalize_data_derives_mes_from_fecha(self, df_with_empty_mes):
        """Test: derive Mes from Fecha when Mes is empty."""
        result = normalize_data(df_with_empty_mes.copy(), is_mayor=False)
        
        assert result is not None
        assert result['Mes'].iloc[0] == 'ene/25'
        assert result['Mes'].iloc[1] == 'feb/25'
        assert result['Mes'].iloc[2] == 'mar/25'
    
    def test_normalize_data_handles_none(self):
        """Test: handle None DataFrame."""
        result = normalize_data(None, is_mayor=False)
        assert result is None
    
    def test_normalize_data_renames_mayor_columns(self):
        """Test: rename columns when is_mayor=True."""
        df = pd.DataFrame({
            'Net': [100, 200],
            'Month': ['ene/25', 'feb/25'],
            'Fecha': pd.to_datetime(['2025-01-15', '2025-02-20'])
        })
        
        result = normalize_data(df.copy(), is_mayor=True)
        
        assert 'Neto' in result.columns
        assert 'Mes' in result.columns
        assert 'Net' not in result.columns
        assert 'Month' not in result.columns
    
    def test_normalize_data_rounds_numeric_columns(self):
        """Test: round numeric columns to 2 decimal places."""
        df = pd.DataFrame({
            'Debe': [100.123456, 200.987654],
            'Haber': [0.0, 0.0],
            'Saldo': [100.123456, 200.987654],
            'Neto': [-100.123456, -200.987654],
            'Fecha': pd.to_datetime(['2025-01-15', '2025-01-20'])
        })
        
        result = normalize_data(df.copy(), is_mayor=False)
        
        assert result['Debe'].iloc[0] == 100.12
        assert result['Haber'].iloc[0] == 0.00
        assert result['Saldo'].iloc[0] == 100.12


class TestValidateColumns:
    """Tests for the validate_columns function."""
    
    def test_validate_columns_success(self, sample_input_df):
        """Test: successful validation when all columns are present."""
       
        validate_columns(sample_input_df, INPUT_PL_COLS, "InputPL")
    
    def test_validate_columns_missing_column(self, sample_input_df):
        """Test: raise ValueError when a column is missing."""
      
        df_missing = sample_input_df.drop(columns=['Concepto'])
        
        with pytest.raises(ValueError) as exc_info:
            validate_columns(df_missing, INPUT_PL_COLS, "InputPL")
        
        assert "Faltan las columnas" in str(exc_info.value)
        assert "Concepto" in str(exc_info.value)
    
    def test_validate_columns_ignores_end(self):
        """Test: ignore 'END' in column validation."""
        df = pd.DataFrame({
            'Nº Asiento': [1, 2],
            'Fecha': pd.to_datetime(['2025-01-15', '2025-01-20']),
            'Concepto': ['A', 'B']
        })
        
       
        required_cols_with_end = ['Nº Asiento', 'Fecha', 'Concepto', 'END']
        validate_columns(df, required_cols_with_end, "Test")

