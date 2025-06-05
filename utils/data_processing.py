import pandas as pd
import numpy as np
from typing import List, Dict, Any, Union
from sklearn.model_selection import train_test_split
from datetime import datetime

def process_data(
    df: pd.DataFrame,
    filters: Dict[str, Any] = None,
    columns: List[str] = None
) -> pd.DataFrame:
    """
    Procesa los datos aplicando filtros y selección de columnas.
    
    Args:
        df: DataFrame original
        filters: Diccionario con filtros a aplicar
        columns: Lista de columnas a mantener
        
    Returns:
        pd.DataFrame: DataFrame procesado
    """
    # Copiar el DataFrame para no modificar el original
    processed_df = df.copy()
    
    # Aplicar filtros si existen
    if filters:
        for col, condition in filters.items():
            if isinstance(condition, dict):
                if 'range' in condition:
                    min_val, max_val = condition['range']
                    processed_df = processed_df[
                        (processed_df[col] >= min_val) & 
                        (processed_df[col] <= max_val)
                    ]
                elif 'categories' in condition:
                    processed_df = processed_df[processed_df[col].isin(condition['categories'])]
    
    # Seleccionar columnas si se especifican
    if columns:
        processed_df = processed_df[columns]
    
    return processed_df

def sample_data(
    df: pd.DataFrame,
    method: str,
    size: Union[int, float],
    **kwargs
) -> pd.DataFrame:
    """
    Aplica diferentes métodos de muestreo a los datos.
    
    Args:
        df: DataFrame original
        method: Método de muestreo ('random', 'stratified', 'temporal')
        size: Tamaño de la muestra (número o proporción)
        **kwargs: Parámetros adicionales específicos del método
        
    Returns:
        pd.DataFrame: DataFrame muestreado
    """
    if method == "random":
        if isinstance(size, float):
            return df.sample(frac=size, random_state=42)
        return df.sample(n=size, random_state=42)
    
    elif method == "stratified":
        if 'strata' not in kwargs:
            raise ValueError("Se requiere la columna 'strata' para muestreo estratificado")
        
        strata = kwargs['strata']
        if isinstance(size, float):
            return df.groupby(strata).apply(
                lambda x: x.sample(frac=size, random_state=42)
            ).reset_index(drop=True)
        return df.groupby(strata).apply(
            lambda x: x.sample(n=size, random_state=42)
        ).reset_index(drop=True)
    
    elif method == "temporal":
        if 'date_column' not in kwargs:
            raise ValueError("Se requiere la columna 'date_column' para muestreo temporal")
        
        date_col = kwargs['date_column']
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df[date_col] = pd.to_datetime(df[date_col])
        
        # Ordenar por fecha
        df = df.sort_values(date_col)
        
        if isinstance(size, float):
            return df.sample(frac=size, random_state=42)
        return df.sample(n=size, random_state=42)
    
    else:
        raise ValueError(f"Método de muestreo '{method}' no soportado")

def generate_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Genera un resumen estadístico del DataFrame.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        dict: Diccionario con estadísticas resumidas
    """
    summary = {
        'general': {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2  # MB
        },
        'columns': {}
    }
    
    for col in df.columns:
        col_info = {
            'type': str(df[col].dtype),
            'null_count': df[col].isnull().sum(),
            'unique_count': df[col].nunique()
        }
        
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info.update({
                'min': df[col].min(),
                'max': df[col].max(),
                'mean': df[col].mean(),
                'std': df[col].std(),
                'percentiles': {
                    '25%': df[col].quantile(0.25),
                    '50%': df[col].quantile(0.50),
                    '75%': df[col].quantile(0.75)
                }
            })
        
        summary['columns'][col] = col_info
    
    return summary 