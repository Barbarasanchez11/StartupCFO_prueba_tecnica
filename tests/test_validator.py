"""
Unit tests for data validation and cleaning functions.
"""
import pandas as pd
import pytest
from src.validator import audit_data_quality, remove_exact_duplicates
from src.config import UNIQUE_IDENTIFIERS


class TestAuditDataQuality:
    """Tests for the audit_data_quality function."""
    
    def test_audit_data_quality_no_issues(self, sample_input_df):
        """Test: no issues detected in clean data."""
        warnings = audit_data_quality(sample_input_df, "InputPL")
        assert len(warnings) == 0
    
    def test_audit_data_quality_detects_negatives(self, df_with_negative_values):
        """Test: detect negative values in Debe and Haber."""
        warnings = audit_data_quality(df_with_negative_values, "Test")
        
        assert len(warnings) > 0
        assert any("negativos" in w.lower() and "debe" in w.lower() for w in warnings)
        assert any("negativos" in w.lower() and "haber" in w.lower() for w in warnings)
    
    def test_audit_data_quality_detects_empty_cells(self):
        """Test: detect empty cells in critical fields."""
        df = pd.DataFrame({
            'Nº Asiento': [1, None, 3], 
            'Fecha': pd.to_datetime(['2025-01-15', '2025-01-20', None]),  
            'Concepto': ['A', 'B', ''], 
            'Saldo': [100.50, 200.75, 150.00]
        })
        
        warnings = audit_data_quality(df, "Test")
        
        assert len(warnings) > 0
        assert any("vacías" in w.lower() for w in warnings)
    
    def test_audit_data_quality_detects_duplicates(self, df_with_duplicates):
        """Test: detect exact duplicates."""
        warnings = audit_data_quality(df_with_duplicates, "Test")
        
        assert len(warnings) > 0
        assert any("duplicados exactos" in w.lower() for w in warnings)
    
    def test_audit_data_quality_ignores_end_row(self, df_with_end_row):
        """Test: ignore END row in audit."""
        warnings = audit_data_quality(df_with_end_row, "Test")

        end_warnings = [w for w in warnings if "end" in w.lower()]
        assert len(end_warnings) == 0
    
    def test_audit_data_quality_empty_dataframe(self):
        """Test: handle empty DataFrame."""
        df = pd.DataFrame()
        warnings = audit_data_quality(df, "Test")
        assert len(warnings) == 0
    
    def test_audit_data_quality_none_dataframe(self):
        """Test: handle None DataFrame."""
        warnings = audit_data_quality(None, "Test")
        assert len(warnings) == 0


class TestRemoveExactDuplicates:
    """Tests for the remove_exact_duplicates function."""
    
    def test_remove_exact_duplicates_no_duplicates(self, sample_input_df):
        """Test: remove nothing when there are no duplicates."""
        df_cleaned, removed_count, message = remove_exact_duplicates(sample_input_df, "Test")
        
        assert len(df_cleaned) == len(sample_input_df)
        assert removed_count == 0
        assert message == ""
    
    def test_remove_exact_duplicates_removes_duplicates(self, df_with_duplicates):
        """Test: correctly remove exact duplicates."""
        original_size = len(df_with_duplicates)
        df_cleaned, removed_count, message = remove_exact_duplicates(df_with_duplicates, "Test")

        assert len(df_cleaned) == 3
        assert removed_count == 3
        assert "eliminaron" in message.lower()
        assert "3" in message
    
    def test_remove_exact_duplicates_preserves_end_row(self, df_with_end_row):
        """Test: preserve END row when removing duplicates."""
        df_cleaned, removed_count, message = remove_exact_duplicates(df_with_end_row, "Test")

        end_rows = df_cleaned[df_cleaned['Nº Asiento'].astype(str).str.upper() == 'END']
        assert len(end_rows) == 1
    
    def test_remove_exact_duplicates_empty_dataframe(self):
        """Test: handle empty DataFrame."""
        df = pd.DataFrame()
        df_cleaned, removed_count, message = remove_exact_duplicates(df, "Test")
        
        assert df_cleaned.empty
        assert removed_count == 0
        assert message == ""
    
    def test_remove_exact_duplicates_none_dataframe(self):
        """Test: handle None DataFrame."""
        df_cleaned, removed_count, message = remove_exact_duplicates(None, "Test")
        
        assert df_cleaned is None
        assert removed_count == 0
        assert message == ""
    
    def test_remove_exact_duplicates_missing_columns(self):
        """Test: handle DataFrame without required columns."""
        df = pd.DataFrame({
            'Nº Asiento': [1, 2],
            'Fecha': pd.to_datetime(['2025-01-15', '2025-01-20'])

        })
        
        df_cleaned, removed_count, message = remove_exact_duplicates(df, "Test")
        
        assert len(df_cleaned) == len(df)
        assert removed_count == 0
        assert message == ""
    
    def test_remove_exact_duplicates_keeps_first_occurrence(self):
        """Test: keep the first occurrence of duplicates."""
        df = pd.DataFrame({
            'Nº Asiento': [1, 1, 1],
            'Fecha': pd.to_datetime(['2025-01-15', '2025-01-15', '2025-01-15']),
            'Saldo': [100.50, 100.50, 100.50],
            'Concepto': ['Primera', 'Segunda', 'Tercera'] 
        })
        
        df_cleaned, removed_count, message = remove_exact_duplicates(df, "Test")
        
        assert len(df_cleaned) == 1
        assert df_cleaned['Concepto'].iloc[0] == 'Primera' 

