"""
Unit tests for processing and comparison functions.
"""
import pandas as pd
import pytest
from src.processor import find_missing_records
from src.config import UNIQUE_IDENTIFIERS


class TestFindMissingRecords:
    """Tests for the find_missing_records function."""
    
    def test_find_missing_records_finds_new_records(self, sample_input_df, sample_mayor_df):
        """Test: find new records in Mayor that are not in InputPL."""
        missing = find_missing_records(sample_input_df, sample_mayor_df)
        
        assert missing is not None
        assert len(missing) == 2  
        assert 4 in missing['Nº Asiento'].values
        assert 5 in missing['Nº Asiento'].values
    
    def test_find_missing_records_no_new_records(self, sample_input_df):
        """Test: find no new records when Mayor equals InputPL."""
        missing = find_missing_records(sample_input_df, sample_input_df.copy())
        
        assert missing is not None
        assert len(missing) == 0
    
    def test_find_missing_records_handles_none_input(self):
        """Test: handle None in input_df."""
        mayor_df = pd.DataFrame({
            'Nº Asiento': [1, 2],
            'Fecha': pd.to_datetime(['2025-01-15', '2025-01-20']),
            'Saldo': [100.50, 200.75]
        })
        
        missing = find_missing_records(None, mayor_df)
        assert missing is None
    
    def test_find_missing_records_handles_none_mayor(self, sample_input_df):
        """Test: handle None in mayor_df."""
        missing = find_missing_records(sample_input_df, None)
        assert missing is None
    
    def test_find_missing_records_filters_end_rows(self):
        """Test: filter END rows from result."""
        input_df = pd.DataFrame({
            'Nº Asiento': [1, 2],
            'Fecha': pd.to_datetime(['2025-01-15', '2025-01-20']),
            'Saldo': [100.50, 200.75]
        })
        
        mayor_df = pd.DataFrame({
            'Nº Asiento': [1, 2, 'END', 3], 
            'Fecha': pd.to_datetime(['2025-01-15', '2025-01-20', None, '2025-02-10']),
            'Saldo': [100.50, 200.75, 0.00, 150.00]
        })
        
        missing = find_missing_records(input_df, mayor_df)
        
        assert missing is not None
        assert len(missing) == 1 
        assert 'END' not in missing['Nº Asiento'].values
    
    def test_find_missing_records_uses_unique_identifiers(self):
        """Test: use UNIQUE_IDENTIFIERS for comparison."""
        input_df = pd.DataFrame({
            'Nº Asiento': [1, 2],
            'Fecha': pd.to_datetime(['2025-01-15', '2025-01-20']),
            'Saldo': [100.50, 200.75],
            'Concepto': ['A', 'B']  
        })
        
        mayor_df = pd.DataFrame({
            'Nº Asiento': [1, 2, 3],
            'Fecha': pd.to_datetime(['2025-01-15', '2025-01-20', '2025-02-10']),
            'Saldo': [100.50, 200.75, 150.00],
            'Concepto': ['X', 'Y', 'Z'] 
        })
        
        missing = find_missing_records(input_df, mayor_df)

        assert len(missing) == 1
        assert missing['Nº Asiento'].iloc[0] == 3
    
    def test_find_missing_records_empty_dataframes(self):
        """Test: handle empty DataFrames."""
        empty_input = pd.DataFrame(columns=UNIQUE_IDENTIFIERS)
        mayor_df = pd.DataFrame({
            'Nº Asiento': [1, 2],
            'Fecha': pd.to_datetime(['2025-01-15', '2025-01-20']),
            'Saldo': [100.50, 200.75]
        })
        
        missing = find_missing_records(empty_input, mayor_df)
        
        assert missing is not None
        assert len(missing) == 2 

