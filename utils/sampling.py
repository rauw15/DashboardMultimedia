import streamlit as st
import pandas as pd
from utils.data_processing import sample_data

def apply_sampling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica métodos de muestreo según las selecciones del usuario.
    
    Args:
        df: DataFrame original
        
    Returns:
        pd.DataFrame: DataFrame muestreado
    """
    st.subheader("Configuración de Muestreo")
    
    # Selección del método de muestreo
    method = st.selectbox(
        "Método de muestreo",
        ["Ninguno", "Aleatorio Simple", "Estratificado", "Temporal"]
    )
    
    if method == "Ninguno":
        return df
    
    # Configuración del tamaño de la muestra
    sample_type = st.radio(
        "Tipo de tamaño",
        ["Proporción", "Número de registros"]
    )
    
    if sample_type == "Proporción":
        size = st.slider("Proporción de la muestra", 0.1, 1.0, 0.5)
    else:
        size = st.number_input(
            "Número de registros",
            min_value=1,
            max_value=len(df),
            value=min(1000, len(df))
        )
    
    # Configuraciones específicas según el método
    if method == "Estratificado":
        strata_col = st.selectbox(
            "Columna para estratificación",
            df.columns
        )
        return sample_data(df, "stratified", size, strata=strata_col)
    
    elif method == "Temporal":
        date_col = st.selectbox(
            "Columna de fecha",
            df.columns
        )
        return sample_data(df, "temporal", size, date_column=date_col)
    
    else:  # Aleatorio Simple
        return sample_data(df, "random", size)