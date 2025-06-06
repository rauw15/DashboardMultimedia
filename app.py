# app.py
import streamlit as st
from utils.data_loader import load_data # Asumiendo que tienes esta función
from utils.sampling import sample_data # Necesitarás crear este módulo/función
from utils.filters import apply_filters_ui, get_filtered_df # Necesitarás crear este módulo/función
from utils.plots import render_main_plot_ui, render_coupled_plot_ui

# --- Configuración de Página ---
st.set_page_config(layout="wide", page_title="Dashboard Multimedia")

# --- Carga de Datos ---
st.sidebar.title("Panel de Control")
uploaded_file = st.sidebar.file_uploader("Carga tu archivo CSV o Excel", type=["csv", "xlsx"])

if 'raw_df' not in st.session_state:
    st.session_state.raw_df = None
if 'sampled_df' not in st.session_state:
    st.session_state.sampled_df = None
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None

if uploaded_file:
    raw_df = load_data(uploaded_file)
    if raw_df is not None:
        st.session_state.raw_df = raw_df
        st.session_state.sampled_df = raw_df # Inicialmente, muestreado es igual a raw
        st.session_state.filtered_df = raw_df # Inicialmente, filtrado es igual a raw
        st.sidebar.success("Archivo cargado exitosamente!")
        st.sidebar.metric("Filas Totales", len(raw_df))
    else:
        st.sidebar.error("No se pudo cargar el archivo.")
        st.session_state.raw_df = None # Resetear si falla la carga

if st.session_state.raw_df is not None:
    current_df_for_processing = st.session_state.raw_df

    # --- Muestreo / Partición de Datos (utils/sampling.py) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Muestreo / Partición")
    # Aquí irían los controles para seleccionar el método de muestreo
    # y st.session_state.sampled_df se actualizaría.
    # Ejemplo:
    # sampling_method = st.sidebar.selectbox("Método de Muestreo", ["Ninguno", "Aleatorio", "Estratificado", "Temporal"])
    # if sampling_method != "Ninguno":
    #     st.session_state.sampled_df = sample_data(st.session_state.raw_df, method=sampling_method, ...) # Implementar sample_data
    # else:
    #     st.session_state.sampled_df = st.session_state.raw_df
    # current_df_for_processing = st.session_state.sampled_df
    
    # Por ahora, asumimos que usamos el raw_df o el último df procesado
    # Debes implementar la lógica de muestreo y actualizar current_df_for_processing

    # --- Filtrado Dinámico (utils/filters.py) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtros Dinámicos")
    # filter_configs = apply_filters_ui(current_df_for_processing) # apply_filters_ui devuelve los widgets y configuraciones
    # if st.sidebar.button("Aplicar Filtros"):
    #     st.session_state.filtered_df = get_filtered_df(current_df_for_processing, filter_configs)
    # else:
    #      # Si no se aplican filtros nuevos, usar el df procesado anteriormente (muestreado o raw)
    #      st.session_state.filtered_df = current_df_for_processing 
    # df_to_visualize = st.session_state.filtered_df

    # Simplificación por ahora: usar el raw_df directamente
    df_to_visualize = st.session_state.raw_df

    if df_to_visualize is not None and not df_to_visualize.empty:
        st.metric("Filas para Visualizar", len(df_to_visualize))
        
        # --- Renderizar Visualizaciones ---
        # Opción 1: Una función que maneja ambas UIs
        # render_all_visualizations_ui(df_to_visualize)

        # Opción 2: Llamar a cada UI por separado
        main_plot_container = st.container()
        with main_plot_container:
            render_main_plot_ui(df_to_visualize, st) # Pasamos 'st' como el contenedor

        st.markdown("---") 

        coupled_plot_container = st.container()
        with coupled_plot_container:
            render_coupled_plot_ui(df_to_visualize, st) # Pasamos 'st' como el contenedor
            
    elif st.session_state.raw_df is not None : # Hay datos cargados pero están vacíos después de filtrar/muestrear
        st.warning("El conjunto de datos actual (después de filtros/muestreo) está vacío.")
else:
    st.info("Por favor, carga un archivo de datos para comenzar.")