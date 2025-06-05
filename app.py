import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import os
from dotenv import load_dotenv
from utils.data_loader import load_data
from utils.filters import apply_filters
from utils.plots import render_plots
from utils.sampling import apply_sampling
from utils.visualizations import create_visualization
from utils.data_processing import process_data

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Análisis Exploratorio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título y descripción
st.title("📊 Dashboard de Análisis Exploratorio")
st.markdown("""
    Esta aplicación permite cargar, explorar y visualizar datasets complejos con funcionalidades avanzadas
    de filtrado, partición de datos y generación de visualizaciones dinámicas.
""")

# Inicializar el estado de la sesión
if 'df' not in st.session_state:
    st.session_state.df = None

# Sidebar para carga de datos
with st.sidebar:
    st.header("📁 Carga de Datos")
    data_source = st.radio(
        "Seleccione la fuente de datos:",
        ["Archivo Local", "MongoDB Atlas", "API REST"]
    )
    
    if data_source == "Archivo Local":
        uploaded_file = st.file_uploader(
            "Cargar archivo CSV/Parquet",
            type=["csv", "parquet"],
            accept_multiple_files=False
        )
    elif data_source == "MongoDB Atlas":
        st.text_input("URI de MongoDB", type="password")
        st.text_input("Nombre de la colección")
    else:  # API REST
        st.text_input("URL de la API")
        st.text_input("API Key", type="password")

# Función para cargar datos
def load_dataset():
    if data_source == "Archivo Local" and uploaded_file is not None:
        try:
            df = load_data(uploaded_file)
            if df is not None:
                st.session_state.df = df
                st.success("¡Datos cargados exitosamente!")
                st.write("Vista previa de los datos:")
                st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error al cargar los datos: {str(e)}")

# Botón para cargar datos
if st.sidebar.button("Cargar Datos"):
    load_dataset()

# Mostrar datos si están cargados
if st.session_state.df is not None:
    # Pestañas para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["📈 Visualizaciones", "🔍 Análisis", "📤 Exportación"])
    
    with tab1:
        st.header("Visualizaciones")
        # Aplicar filtros
        filtered_df = apply_filters(st.session_state.df)
        
        # Aplicar muestreo
        sampled_df = apply_sampling(filtered_df)
        
        # Visualizaciones
        render_plots(sampled_df)
        
    with tab2:
        st.header("Análisis de Datos")
        st.write("Estadísticas descriptivas:")
        st.write(st.session_state.df.describe())
        
    with tab3:
        st.header("Exportación")
        if st.button("Exportar DataFrame a CSV"):
            csv = st.session_state.df.to_csv(index=False)
            st.download_button(
                "Descargar CSV",
                csv,
                "datos_exportados.csv",
                "text/csv",
                key='download-csv'
            )