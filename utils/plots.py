import streamlit as st
import pandas as pd
from utils.visualizations import create_visualization, export_plot

def render_plots(df: pd.DataFrame):
    """
    Renderiza las visualizaciones según el tipo seleccionado.
    
    Args:
        df: DataFrame con los datos a visualizar
    """
    if df is None or df.empty:
        st.warning("No hay datos para visualizar. Por favor, carga un conjunto de datos primero.")
        return

    st.subheader("Configuración de Visualización")
    
    # Selección de tipo de gráfico
    plot_type = st.selectbox(
        "Tipo de gráfico",
        ["bar", "histogram", "box", "violin", "scatter", "heatmap", "pie", "pairplot", "slope"]
    )
    
    # Selección de columnas según el tipo de gráfico
    if plot_type in ["bar", "histogram", "box", "violin"]:
        x_col = st.selectbox("Columna X", df.columns)
        y_col = st.selectbox("Columna Y", df.columns) if plot_type != "histogram" else None
        color_col = st.selectbox("Columna para color", ["Ninguna"] + list(df.columns))
        color_col = None if color_col == "Ninguna" else color_col
        
        fig = create_visualization(
            df,
            plot_type,
            x=x_col,
            y=y_col,
            color=color_col
        )
        
    elif plot_type == "scatter":
        x_col = st.selectbox("Columna X", df.columns)
        y_col = st.selectbox("Columna Y", df.columns)
        color_col = st.selectbox("Columna para color", ["Ninguna"] + list(df.columns))
        color_col = None if color_col == "Ninguna" else color_col
        
        fig = create_visualization(
            df,
            plot_type,
            x=x_col,
            y=y_col,
            color=color_col
        )
        
    elif plot_type == "heatmap":
        fig = create_visualization(df, plot_type)
        
    elif plot_type == "pie":
        names_col = st.selectbox("Columna para nombres", df.columns)
        values_col = st.selectbox("Columna para valores", df.columns)
        color_col = st.selectbox("Columna para color", ["Ninguna"] + list(df.columns))
        color_col = None if color_col == "Ninguna" else color_col
        
        fig = create_visualization(
            df,
            plot_type,
            x=names_col,
            y=values_col,
            color=color_col
        )
        
    elif plot_type == "pairplot":
        dimensions = st.multiselect(
            "Selecciona las columnas para el pairplot",
            df.columns,
            default=df.columns[:4]
        )
        
        fig = create_visualization(
            df,
            plot_type,
            dimensions=dimensions
        )
        
    elif plot_type == "slope":
        x_col = st.selectbox("Columna X", df.columns)
        y_col = st.selectbox("Columna Y", df.columns)
        color_col = st.selectbox("Columna para color", df.columns)
        
        fig = create_visualization(
            df,
            plot_type,
            x=x_col,
            y=y_col,
            color=color_col
        )
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Opciones de exportación
    if st.button("Exportar gráfico"):
        export_format = st.selectbox("Formato de exportación", ["png", "pdf"])
        dpi = st.slider("DPI", 100, 600, 300) if export_format == "png" else None
        
        fig_bytes = export_plot(fig, format=export_format, dpi=dpi)
        st.download_button(
            "Descargar gráfico",
            fig_bytes,
            file_name=f"grafico.{export_format}",
            mime=f"image/{export_format}"
        )