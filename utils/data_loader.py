import pandas as pd
import streamlit as st
from io import BytesIO
import pyarrow.parquet as pq
import dask.dataframe as dd
from typing import Union, List
import io

def load_data(file: Union[str, List[str], io.BytesIO]) -> pd.DataFrame:
    """
    Carga datos desde diferentes fuentes y formatos.
    
    Args:
        file: Puede ser un archivo individual, lista de archivos o BytesIO
        
    Returns:
        pd.DataFrame: DataFrame con los datos cargados
    """
    try:
        if isinstance(file, list):
            # Si es una lista de archivos, los concatenamos
            dfs = []
            for f in file:
                if f.name.endswith('.csv'):
                    df = pd.read_csv(f)
                elif f.name.endswith('.parquet'):
                    df = pd.read_parquet(f)
                dfs.append(df)
            return pd.concat(dfs, ignore_index=True)
        
        else:
            # Si es un solo archivo
            if file.name.endswith('.csv'):
                return pd.read_csv(file)
            elif file.name.endswith('.parquet'):
                return pd.read_parquet(file)
            else:
                raise ValueError("Formato de archivo no soportado")
                
    except Exception as e:
        st.error(f"Error al cargar el archivo: {str(e)}")
        return None

def detect_column_types(df: pd.DataFrame) -> dict:
    """
    Detecta automáticamente los tipos de columnas y genera estadísticas básicas.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        dict: Diccionario con información de las columnas
    """
    if df is None:
        return {}
        
    column_info = {}
    
    for col in df.columns:
        info = {
            'type': str(df[col].dtype),
            'null_count': df[col].isnull().sum(),
            'unique_count': df[col].nunique(),
            'is_numeric': pd.api.types.is_numeric_dtype(df[col]),
            'is_categorical': pd.api.types.is_categorical_dtype(df[col]),
            'is_datetime': pd.api.types.is_datetime64_any_dtype(df[col])
        }
        
        if info['is_numeric']:
            info.update({
                'min': df[col].min(),
                'max': df[col].max(),
                'mean': df[col].mean(),
                'std': df[col].std()
            })
        
        column_info[col] = info
    
    return column_info

def load_local_file():
    uploaded_file = st.file_uploader(
        "Sube tu archivo de datos", 
        type=["csv", "parquet"],
        accept_multiple_files=True
    )
    
    if not uploaded_file:
        return None
    
    try:
        if uploaded_file.type == "text/csv":
            dfs = [pd.read_csv(file) for file in uploaded_file]
        elif uploaded_file.type == "application/octet-stream":  # Parquet
            dfs = [pq.read_table(BytesIO(file.read())) for file in uploaded_file]
        
        return pd.concat(dfs, ignore_index=True)
    except Exception as e:
        st.error(f"Error al cargar archivo: {e}")
        return None

def load_from_db():
    # Implementar conexión a MongoDB Atlas
    pass

def load_from_api():
    # Implementar conexión a API REST
    pass