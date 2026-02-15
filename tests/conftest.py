"""
Shared fixtures for all tests.
"""
import pandas as pd
import pytest
from datetime import datetime


@pytest.fixture
def sample_input_df():
    """Sample DataFrame for InputPL with valid data."""
    return pd.DataFrame({
        'Nº Asiento': [1, 2, 3],
        'Fecha': pd.to_datetime(['2025-01-15', '2025-01-20', '2025-02-10']),
        'Documento': ['DOC1', 'DOC2', 'DOC3'],
        'Concepto': ['Concepto 1', 'Concepto 2', 'Concepto 3'],
        'Cuenta': ['123', '456', '789'],
        'Debe': [100.50, 200.75, 150.00],
        'Haber': [0.00, 0.00, 0.00],
        'Saldo': [100.50, 200.75, 150.00],
        'Nombre cuenta': ['Cuenta 1', 'Cuenta 2', 'Cuenta 3'],
        'Neto': [-100.50, -200.75, -150.00],
        'Mes': ['ene/25', 'ene/25', 'feb/25'],
        'Tipo de gasto': ['Admin', 'IT', 'Sales']
    })


@pytest.fixture
def sample_mayor_df():
    """Sample DataFrame for Mayor with more records than InputPL."""
    return pd.DataFrame({
        'Nº Asiento': [1, 2, 3, 4, 5],  
        'Fecha': pd.to_datetime(['2025-01-15', '2025-01-20', '2025-02-10', '2025-03-15', '2025-03-20']),
        'Documento': ['DOC1', 'DOC2', 'DOC3', 'DOC4', 'DOC5'],
        'Concepto': ['Concepto 1', 'Concepto 2', 'Concepto 3', 'Concepto 4', 'Concepto 5'],
        'Cuenta': ['123', '456', '789', '111', '222'],
        'Debe': [100.50, 200.75, 150.00, 300.00, 400.00],
        'Haber': [0.00, 0.00, 0.00, 0.00, 0.00],
        'Saldo': [100.50, 200.75, 150.00, 300.00, 400.00],
        'Nombre cuenta': ['Cuenta 1', 'Cuenta 2', 'Cuenta 3', 'Cuenta 4', 'Cuenta 5'],
        'Neto': [-100.50, -200.75, -150.00, -300.00, -400.00],
        'Mes': ['ene/25', 'ene/25', 'feb/25', 'mar/25', 'mar/25']
    })


@pytest.fixture
def df_with_duplicates():
    """DataFrame with exact duplicates for testing."""
    return pd.DataFrame({
        'Nº Asiento': [1, 1, 2, 3, 3, 3],
        'Fecha': pd.to_datetime(['2025-01-15', '2025-01-15', '2025-01-20', '2025-02-10', '2025-02-10', '2025-02-10']),
        'Saldo': [100.50, 100.50, 200.75, 150.00, 150.00, 150.00],
        'Concepto': ['A', 'A', 'B', 'C', 'C', 'C'],
        'Debe': [100.50, 100.50, 200.75, 150.00, 150.00, 150.00]
    })


@pytest.fixture
def df_with_end_row():
    """DataFrame that includes an END row."""
    return pd.DataFrame({
        'Nº Asiento': [1, 2, 'END'],
        'Fecha': pd.to_datetime(['2025-01-15', '2025-01-20', None]),
        'Saldo': [100.50, 200.75, 0.00],
        'Concepto': ['A', 'B', 'END']
    })


@pytest.fixture
def df_with_empty_mes():
    """DataFrame with empty or invalid Mes column."""
    return pd.DataFrame({
        'Nº Asiento': [1, 2, 3],
        'Fecha': pd.to_datetime(['2025-01-15', '2025-02-20', '2025-03-10']),
        'Mes': [None, '', 'invalid'],
        'Concepto': ['A', 'B', 'C']
    })


@pytest.fixture
def df_with_negative_values():
    """DataFrame with negative values in Debe or Haber."""
    return pd.DataFrame({
        'Nº Asiento': [1, 2, 3],
        'Fecha': pd.to_datetime(['2025-01-15', '2025-01-20', '2025-02-10']),
        'Debe': [-100.50, 200.75, 150.00], 
        'Haber': [0.00, -50.00, 0.00],  
        'Saldo': [100.50, 200.75, 150.00],
        'Concepto': ['A', 'B', 'C']
    })

