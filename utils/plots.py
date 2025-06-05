# plots.py (o el nombre que le hayas dado a este archivo)
import streamlit as st
import pandas as pd
import numpy as np # Para np.number
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
    plot_type_options = ["bar", "histogram", "box", "violin", "scatter", "heatmap", "pie", "pairplot", "slope"]
    plot_type = st.selectbox(
        "Tipo de gráfico",
        plot_type_options
    )
    
    # Obtener listas de columnas
    all_cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    # Podrías definir categorical_cols si quieres ser más específico en algunas selecciones
    # categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # Inicializar variables para los parámetros del gráfico
    x_col, y_col, color_col, names_col, values_col = None, None, None, None, None
    kwargs_for_create_viz = {} # Para parámetros especiales como 'dimensions'

    # --- Selección de columnas según el tipo de gráfico ---
    
    if plot_type == "bar":
        st.write("Selecciona columnas para el gráfico de barras:")
        x_col = st.selectbox("Columna X (categorías)", all_cols, key="bar_x")
        y_col = st.selectbox("Columna Y (valores, usualmente numérica)", numeric_cols if numeric_cols else all_cols, key="bar_y")
        color_col_options = [None] + all_cols
        color_col = st.selectbox("Columna para color (opcional)", color_col_options, format_func=lambda x: 'Ninguna' if x is None else x, key="bar_color")

    elif plot_type == "histogram":
        st.write("Selecciona columna para el histograma:")
        x_col = st.selectbox("Columna X (usualmente numérica)", numeric_cols if numeric_cols else all_cols, key="hist_x")
        color_col_options = [None] + all_cols
        color_col = st.selectbox("Columna para agrupar por color (opcional)", color_col_options, format_func=lambda x: 'Ninguna' if x is None else x, key="hist_color")

    elif plot_type == "box" or plot_type == "violin":
        st.write(f"Selecciona columnas para el gráfico {plot_type}:")
        y_col = st.selectbox("Columna Y (valores, usualmente numérica)", numeric_cols if numeric_cols else all_cols, key=f"{plot_type}_y")
        x_col_options = [None] + all_cols # X puede ser categórica o None
        x_col = st.selectbox("Columna X (categorías, opcional)", x_col_options, format_func=lambda x: 'Ninguna' if x is None else x, key=f"{plot_type}_x")
        color_col_options = [None] + all_cols
        color_col = st.selectbox("Columna para color (opcional)", color_col_options, format_func=lambda x: 'Ninguna' if x is None else x, key=f"{plot_type}_color")
        
    elif plot_type == "scatter":
        st.write("Selecciona columnas para el gráfico de dispersión:")
        x_col = st.selectbox("Columna X", all_cols, key="scatter_x")
        y_col = st.selectbox("Columna Y (usualmente numérica)", numeric_cols if numeric_cols else all_cols, key="scatter_y")
        color_col_options = [None] + all_cols
        color_col = st.selectbox("Columna para color (opcional)", color_col_options, format_func=lambda x: 'Ninguna' if x is None else x, key="scatter_color")
        
    elif plot_type == "heatmap":
        st.write("El heatmap se generará usando las columnas numéricas para calcular la correlación.")
        # No se necesitan selecciones de columnas específicas aquí, create_visualization lo maneja
        
    elif plot_type == "pie":
        st.write("Selecciona columnas para el gráfico de torta:")
        names_col = st.selectbox("Columna para nombres/etiquetas", all_cols, key="pie_names")
        values_col = st.selectbox("Columna para valores (numérica)", numeric_cols if numeric_cols else all_cols, key="pie_values")
        # El parámetro 'color' en px.pie es un poco diferente, usualmente se colorea por 'names'.
        # Si quieres pasar un 'color' específico a create_visualization para que lo maneje, puedes añadirlo:
        # color_col_options_pie = [None] + all_cols
        # color_col = st.selectbox("Columna para color (avanzado, opcional)", color_col_options_pie, format_func=lambda x: 'Ninguna' if x is None else x, key="pie_color")
        x_col = names_col # En create_visualization, x se usa para names
        y_col = values_col # En create_visualization, y se usa para values

    elif plot_type == "pairplot":
        st.write("Selecciona columnas para el pairplot (se usarán solo las numéricas de tu selección):")
        if not numeric_cols:
            st.warning("No hay columnas numéricas disponibles para Pairplot.")
            fig = create_visualization(pd.DataFrame(), "pairplot") # Devuelve fig vacía
        else:
            # Usar solo columnas numéricas como opciones y default
            default_pairplot_dims = numeric_cols[:min(4, len(numeric_cols))] # Default a las primeras 4 numéricas o menos
            
            selected_dimensions = st.multiselect(
                "Selecciona las columnas para el pairplot",
                options=numeric_cols, # Opciones son solo numéricas
                default=default_pairplot_dims,
                key="pairplot_dims"
            )
            kwargs_for_create_viz['dimensions'] = selected_dimensions
            
            # Opcional: columna para colorear en pairplot
            color_options_pairplot = [None] + all_cols # Puede ser categórica o numérica
            color_col = st.selectbox(
                "Columna para colorear puntos (opcional)", 
                options=color_options_pairplot, 
                format_func=lambda x: 'Ninguna' if x is None else x,
                key="pairplot_color"
            )
        
    elif plot_type == "slope":
        st.write("Selecciona columnas para el gráfico de pendiente:")
        x_col = st.selectbox("Columna X (usualmente dos puntos de tiempo o categorías ordenadas)", all_cols, key="slope_x")
        y_col = st.selectbox("Columna Y (valores numéricos)", numeric_cols if numeric_cols else all_cols, key="slope_y")
        color_col = st.selectbox("Columna para líneas/categorías", all_cols, key="slope_color") # Debe ser categórica

    # --- Crear y mostrar el gráfico ---
    # Solo intentar crear la figura si las columnas necesarias están disponibles
    # (esto es una simplificación, podrías necesitar validaciones más estrictas por tipo de gráfico)
    
    # Para pairplot, la figura se maneja dentro del if, si no hay numeric_cols
    if plot_type == "pairplot" and not numeric_cols:
        pass # fig ya está definida como vacía
    else:
        fig = create_visualization(
            df,
            plot_type,
            x=x_col,
            y=y_col,
            color=color_col,
            **kwargs_for_create_viz # Pasa 'dimensions' para pairplot, etc.
        )
    
    # Mostrar el gráfico si tiene datos
    if fig.data:
        st.plotly_chart(fig, use_container_width=True)
        
        # Opciones de exportación
        st.subheader("Exportar Gráfico")
        export_container = st.container() # Usar un container para agrupar widgets de exportación
        
        # Usar columnas para organizar mejor
        col1, col2 = export_container.columns(2)

        export_format = col1.selectbox("Formato", ["png", "svg", "pdf", "jpeg"], key="export_format")
        
        dpi = 300 # Default DPI
        if export_format == "png" or export_format == "jpeg":
            dpi = col2.slider("DPI/Escala", 100, 600, 300, 50, key="export_dpi")
        
        # El botón de exportar ahora está más visible
        if export_container.button("Preparar Descarga", key="prepare_export"):
            try:
                fig_bytes = export_plot(fig, format=export_format, dpi=dpi) # dpi se usa internamente para scale en export_plot
                if fig_bytes:
                    file_extension = export_format
                    mime_type = f"image/{file_extension}"
                    if export_format == "pdf":
                        mime_type = "application/pdf"
                    elif export_format == "svg":
                        mime_type = "image/svg+xml"
                        
                    export_container.download_button(
                        label=f"Descargar como {export_format.upper()}",
                        data=fig_bytes,
                        file_name=f"grafico_{plot_type}.{file_extension}",
                        mime=mime_type,
                        key="download_button"
                    )
                else:
                    export_container.error("No se pudo generar el archivo para descargar.")
            except Exception as e:
                export_container.error(f"Error al exportar: {e}")
    elif plot_type: # Si se seleccionó un tipo de gráfico pero fig.data está vacío
        st.info(f"No se pudo generar el gráfico '{plot_type}'. Verifica las selecciones de columnas o los datos (p.ej., ¿hay suficientes datos numéricos para este gráfico?).")