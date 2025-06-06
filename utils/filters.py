# utils/filters.py
import streamlit as st
import pandas as pd
import numpy as np

def apply_filters_ui(df: pd.DataFrame, key_prefix="filter_"):
    """
    Genera widgets de Streamlit en la sidebar para filtrar el DataFrame.
    Devuelve un diccionario con las configuraciones de filtro seleccionadas.
    """
    if df is None or df.empty:
        st.sidebar.warning("No hay datos para aplicar filtros.")
        return {}

    filters = {}
    st.sidebar.markdown("#### Filtros de Columnas")

    for col in df.columns:
        col_key = f"{key_prefix}{col}"
        
        # Filtro para columnas numéricas (rango)
        if pd.api.types.is_numeric_dtype(df[col]):
            if len(df[col].unique()) > 1: # Solo si hay más de un valor único
                min_val, max_val = float(df[col].min()), float(df[col].max())
                selected_range = st.sidebar.slider(
                    f"Rango para '{col}'",
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val),
                    key=f"{col_key}_range"
                )
                if selected_range != (min_val, max_val): # Si el usuario cambió el default
                    filters[col] = {"type": "numeric_range", "range": selected_range}
        
        # Filtro para columnas categóricas (selección múltiple)
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
            unique_values = df[col].unique().tolist()
            if len(unique_values) < 1: continue # Saltar si no hay valores o solo NaNs
            
            # Quitar NaNs de las opciones si existen y no son la única opción
            options = [val for val in unique_values if pd.notna(val)]
            if not options and any(pd.isna(val) for val in unique_values): # Solo si solo hay NaNs
                options = [np.nan] # Permitir filtrar por NaN si es la única opción
            elif not options: # Si no hay opciones después de quitar NaNs (columna vacía)
                continue

            selected_values = st.sidebar.multiselect(
                f"Valores para '{col}'",
                options=options,
                default=options, # Seleccionar todos por defecto
                key=f"{col_key}_multiselect"
            )
            if set(selected_values) != set(options): # Si el usuario deseleccionó algo
                filters[col] = {"type": "categorical_multiselect", "values": selected_values}

        # Filtro para columnas de fecha/datetime (rango de fechas) - BÁSICO
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            try:
                min_date, max_date = df[col].min(), df[col].max()
                if pd.isna(min_date) or pd.isna(max_date): continue # Si hay NaTs que impiden rango

                selected_date_range = st.sidebar.date_input(
                    f"Rango de fechas para '{col}'",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key=f"{col_key}_daterange"
                )
                if len(selected_date_range) == 2:
                     # Convertir a pd.Timestamp para comparación si es necesario
                    start_date = pd.Timestamp(selected_date_range[0])
                    end_date = pd.Timestamp(selected_date_range[1])
                    if start_date != min_date or end_date != max_date:
                        filters[col] = {"type": "datetime_range", "range": (start_date, end_date)}
            except Exception as e:
                st.sidebar.warning(f"No se pudo crear filtro de fecha para {col}: {e}")
                
    # Aquí podrías añadir la lógica para condiciones combinadas (AND/OR)
    # Esto es más complejo y requeriría una UI para construir expresiones.
    # Por ahora, los filtros aplicados son implícitamente AND.

    return filters

def get_filtered_df(df: pd.DataFrame, filter_configs: dict) -> pd.DataFrame:
    """
    Aplica las configuraciones de filtro al DataFrame y devuelve el DataFrame filtrado.
    """
    if not filter_configs or df is None or df.empty:
        return df

    filtered_df = df.copy()

    for col, config in filter_configs.items():
        if config["type"] == "numeric_range":
            min_val, max_val = config["range"]
            filtered_df = filtered_df[(filtered_df[col] >= min_val) & (filtered_df[col] <= max_val)]
        
        elif config["type"] == "categorical_multiselect":
            selected_values = config["values"]
            # Manejar NaNs si fueron una opción seleccionable
            if any(pd.isna(val) for val in selected_values):
                # Crear una máscara que incluya NaNs si np.nan está en selected_values
                # y también incluya los no-NaNs seleccionados.
                is_nan_selected = np.nan in selected_values
                non_nan_selected_values = [v for v in selected_values if pd.notna(v)]
                
                mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
                if non_nan_selected_values:
                    mask = mask | filtered_df[col].isin(non_nan_selected_values)
                if is_nan_selected:
                    mask = mask | filtered_df[col].isna()
                filtered_df = filtered_df[mask]
            else:
                filtered_df = filtered_df[filtered_df[col].isin(selected_values)]

        elif config["type"] == "datetime_range":
            start_date, end_date = config["range"]
            # Asegurarse que la columna es datetime
            if not pd.api.types.is_datetime64_any_dtype(filtered_df[col]):
                try:
                    filtered_df[col] = pd.to_datetime(filtered_df[col])
                except Exception:
                    st.warning(f"No se pudo convertir la columna {col} a datetime para filtrar.")
                    continue
            filtered_df = filtered_df[(filtered_df[col] >= start_date) & (filtered_df[col] <= end_date)]
    
    return filtered_df