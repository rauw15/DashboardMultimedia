# utils/plots.py
import streamlit as st
import pandas as pd
import numpy as np
from utils.visualizations import create_visualization, create_coupled_plot, export_plot

def get_bar_chart_controls(df_columns, key_prefix=""):
    params = {}
    params['orientation'] = st.sidebar.radio(f"Orientación {key_prefix}", ['v', 'h'], index=0, key=f"{key_prefix}bar_orient") # index=0 para default 'v'
    params['barmode'] = st.sidebar.selectbox(f"Modo de Barra {key_prefix}", ['relative', 'group', 'overlay'], key=f"{key_prefix}bar_mode")
    return params

def get_histogram_controls(key_prefix=""):
    params = {}
    params['nbins'] = st.sidebar.slider(f"Número de Bins {key_prefix}", 5, 100, 20, key=f"{key_prefix}hist_nbins")
    params['histnorm'] = st.sidebar.selectbox(f"Normalización {key_prefix}", [None, 'percent', 'probability', 'density'], format_func=lambda x: 'Ninguna' if x is None else x, key=f"{key_prefix}hist_norm")
    params['show_kde'] = st.sidebar.checkbox(f"Mostrar KDE (aprox.) {key_prefix}", key=f"{key_prefix}hist_kde")
    return params

def get_boxplot_controls(key_prefix=""):
    params = {}
    params['points'] = st.sidebar.selectbox(f"Mostrar Puntos {key_prefix}", ['outliers', 'all', False, 'suspectedoutliers'], key=f"{key_prefix}box_points")
    params['show_outliers'] = st.sidebar.checkbox(f"Mostrar Outliers {key_prefix}", True, key=f"{key_prefix}box_showoutliers")
    return params
    
def get_slope_chart_controls(df_columns, key_prefix=""):
    params = {}
    params['slope_marker_color_positive'] = st.sidebar.color_picker(f"Color Positivo {key_prefix}", "#00FF00", key=f"{key_prefix}slope_pos_color")
    params['slope_marker_color_negative'] = st.sidebar.color_picker(f"Color Negativo {key_prefix}", "#FF0000", key=f"{key_prefix}slope_neg_color")
    return params

def get_radar_controls(df_columns, key_prefix=""):
    params = {}
    return params


def render_main_plot_ui(df: pd.DataFrame, plot_area_container):
    if df is None or df.empty:
        plot_area_container.warning("No hay datos cargados para visualizar.")
        return

    plot_area_container.subheader("Gráfico Individual")
    all_cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    plot_type_options = ["bar", "histogram", "box", "violin", "scatter", "heatmap_corr", "heatmap_crosstab", "pie", "pairplot", "slope", "radar", "diverging_bars", "box_violin_combined"]
    selected_plot_type = st.sidebar.selectbox("Tipo de Gráfico Principal", plot_type_options, key="main_plot_type")

    st.sidebar.markdown("---")
    st.sidebar.subheader(f"Configuración: {selected_plot_type.replace('_', ' ').capitalize()}")
    x_col, y_col, y2_col, color_col, size_col = None, None, None, None, None
    specific_params = {}

    if selected_plot_type == "bar":
        x_col = st.sidebar.selectbox("Columna X (Categoría)", all_cols, key="main_bar_x")
        y_col_options = [None] + (numeric_cols if numeric_cols else all_cols)
        y_col = st.sidebar.selectbox("Columna Y (Valor Numérico)", y_col_options, format_func=lambda x: "Frecuencia (Univariado)" if x is None else x, key="main_bar_y")
        color_col = st.sidebar.selectbox("Columna para Color", [None] + all_cols, format_func=lambda x: 'Ninguna' if x is None else x, key="main_bar_color")
        specific_params = get_bar_chart_controls(all_cols)
    
    elif selected_plot_type == "histogram":
        x_col = st.sidebar.selectbox("Columna Numérica X", numeric_cols if numeric_cols else all_cols, key="main_hist_x")
        color_col = st.sidebar.selectbox("Columna para Color (Agrupar)", [None] + all_cols, format_func=lambda x: 'Ninguna' if x is None else x, key="main_hist_color")
        specific_params = get_histogram_controls()

    elif selected_plot_type in ["box", "violin", "box_violin_combined"]:
        y_col_main = st.sidebar.selectbox(f"Columna Numérica Y Principal", numeric_cols if numeric_cols else all_cols, key=f"main_{selected_plot_type}_y")
        x_col_group = st.sidebar.selectbox(f"Columna X (Agrupar por Categoría)", [None] + all_cols, format_func=lambda x: 'Ninguna (Univariado)' if x is None else x, key=f"main_{selected_plot_type}_x")
        color_col = st.sidebar.selectbox("Columna para Color", [None] + all_cols, format_func=lambda x: 'Ninguna' if x is None else x, key=f"main_{selected_plot_type}_color")
        x_col, y_col = (y_col_main, None) if x_col_group is None else (x_col_group, y_col_main)
        if selected_plot_type == "box": specific_params = get_boxplot_controls()
            
    elif selected_plot_type == "scatter":
        x_col = st.sidebar.selectbox("Columna X (Numérica)", numeric_cols if numeric_cols else all_cols, key="main_scatter_x")
        y_col = st.sidebar.selectbox("Columna Y (Numérica)", numeric_cols if numeric_cols else all_cols, key="main_scatter_y")
        color_col = st.sidebar.selectbox("Columna para Color", [None] + all_cols, format_func=lambda x: 'Ninguna' if x is None else x, key="main_scatter_color")
        size_col = st.sidebar.selectbox("Columna para Tamaño (Numérica)", [None] + (numeric_cols if numeric_cols else all_cols), format_func=lambda x: 'Ninguno' if x is None else x, key="main_scatter_size")
        specific_params['trendline'] = st.sidebar.selectbox("Línea de Tendencia", [None, "ols", "lowess"], format_func=lambda x: 'Ninguna' if x is None else x.upper(), key="main_scatter_trend")

    elif selected_plot_type == "heatmap_corr":
        st.sidebar.info("Heatmap de correlación usa columnas numéricas.")
    elif selected_plot_type == "heatmap_crosstab":
        x_col = st.sidebar.selectbox("Columna X (Categórica 1)", all_cols, key="main_heatc_x")
        y_col = st.sidebar.selectbox("Columna Y (Categórica 2)", all_cols, key="main_heatc_y")
    elif selected_plot_type == "pie":
        x_col = st.sidebar.selectbox("Columna de Nombres (Categorías)", all_cols, key="main_pie_names")
        y_col = st.sidebar.selectbox("Columna de Valores (Numérica)", numeric_cols if numeric_cols else all_cols, key="main_pie_values")
        specific_params['hole_pie'] = st.sidebar.slider("Agujero (Donut)", 0.0, 0.8, 0.0, 0.1, key="main_pie_hole")
    elif selected_plot_type == "pairplot":
        if not numeric_cols: st.sidebar.warning("No hay columnas numéricas para Pairplot.")
        else:
            default_dims = numeric_cols[:min(4, len(numeric_cols))]
            selected_dimensions = st.sidebar.multiselect("Dimensiones (Numéricas)", numeric_cols, default=default_dims, key="main_pairplot_dims")
            specific_params['dimensions'] = selected_dimensions
            color_col = st.sidebar.selectbox("Columna para Color (Hue)", [None] + all_cols, format_func=lambda x: 'Ninguna' if x is None else x, key="main_pairplot_color")
    elif selected_plot_type == "slope":
        color_col = st.sidebar.selectbox("Columna de Categorías/Entidades", all_cols, key="main_slope_entity")
        x_col = st.sidebar.selectbox("Columna de Período/Condición (2 valores)", all_cols, key="main_slope_period")
        y_col = st.sidebar.selectbox("Columna de Valores (Numérica)", numeric_cols if numeric_cols else all_cols, key="main_slope_value")
        specific_params = get_slope_chart_controls(all_cols)
    elif selected_plot_type == "radar":
        y_cols_for_radar = st.sidebar.multiselect("Variables para Ejes (Numéricas)", numeric_cols if numeric_cols else all_cols, default=numeric_cols[:min(5, len(numeric_cols))] if numeric_cols else None, key="main_radar_y_cols")
        if not y_cols_for_radar: st.sidebar.warning("Selecciona variables para el radar.")
        else: y_col = y_cols_for_radar # y_col es ahora una lista
        x_col = st.sidebar.selectbox("Agrupar Radares por (Categórica, Opcional)", [None] + all_cols, format_func=lambda x: 'Radar Único' if x is None else x, key="main_radar_group_x")
        specific_params = get_radar_controls(all_cols)
    elif selected_plot_type == "diverging_bars":
        x_col = st.sidebar.selectbox("Columna X (Categoría)", all_cols, key="main_divbar_x")
        y_col = st.sidebar.selectbox("Columna Y (Valor Numérico)", numeric_cols if numeric_cols else all_cols, key="main_divbar_y")

    if not df.empty:
        ready_to_plot = True # Simplificado, create_visualization maneja columnas faltantes
        if ready_to_plot:
            fig = create_visualization(df, selected_plot_type, x=x_col, y=y_col, y2=y2_col, color=color_col, size=size_col, **specific_params)
            if fig.data or fig.layout.annotations:
                plot_area_container.plotly_chart(fig, use_container_width=True)
                # Exportación
                export_container = plot_area_container.expander("Exportar Gráfico Principal")
                col1_exp, col2_exp = export_container.columns(2)
                export_format = col1_exp.selectbox("Formato", ["png", "svg", "pdf", "jpeg"], key="main_export_format")
                dpi_val = 300
                if export_format in ["png", "jpeg"]: dpi_val = col2_exp.slider("DPI/Escala", 100, 600, 300, 50, key="main_export_dpi")
                if export_container.button("Preparar Descarga", key="main_prepare_export"):
                    try:
                        fig_bytes = export_plot(fig, format=export_format, dpi=dpi_val)
                        if fig_bytes:
                            mime = f"image/{export_format}" if export_format != "pdf" else "application/pdf"
                            if export_format == "svg": mime = "image/svg+xml"
                            export_container.download_button(label=f"Descargar como {export_format.upper()}", data=fig_bytes, file_name=f"grafico_{selected_plot_type}.{export_format}", mime=mime)
                        else: export_container.error("No se pudo generar archivo.")
                    except Exception as e: export_container.error(f"Error al exportar: {e}")
            else: plot_area_container.info(f"No se pudo generar '{selected_plot_type}'.")
        else: plot_area_container.info(f"Selecciona columnas para '{selected_plot_type}'.")


def render_coupled_plot_ui(df: pd.DataFrame, plot_area_container):
    if df is None or df.empty:
        plot_area_container.warning("No hay datos cargados para visualizar.")
        return

    plot_area_container.subheader("Gráficos Acoplados (Subplots)")
    num_subplots = st.sidebar.number_input("Número de Subgráficos (1-4)", 1, 4, 2, key="num_subplots")
    plot_configs = []
    
    layout_params = {} # Para pasar a create_coupled_plot
    layout_params['subplot_rows'] = st.sidebar.slider("Filas de Subplots", 1, num_subplots, 1, key="subplot_r")
    # layout_params['subplot_cols'] = st.sidebar.slider("Columnas de Subplots", 1, num_subplots, num_subplots // layout_params['subplot_rows'] if layout_params['subplot_rows'] > 0 else num_subplots, key="subplot_c")


    all_cols = df.columns.tolist()
    plot_type_options_subplot = ["bar", "histogram", "box", "violin", "scatter", "pie", "slope"]

    for i in range(num_subplots):
        st.sidebar.markdown(f"---")
        st.sidebar.subheader(f"Configuración Subgráfico {i+1}")
        config = {}
        config['viz_type'] = st.sidebar.selectbox(f"Tipo Gráfico {i+1}", plot_type_options_subplot, key=f"sub_type_{i}")
        config['x'] = st.sidebar.selectbox(f"Columna X {i+1}", [None] + all_cols, format_func=lambda x: 'Ninguna' if x is None else x, key=f"sub_x_{i}")
        config['y'] = st.sidebar.selectbox(f"Columna Y {i+1}", [None] + all_cols, format_func=lambda x: 'Ninguna' if x is None else x, key=f"sub_y_{i}")
        config['color'] = st.sidebar.selectbox(f"Color {i+1}", [None] + all_cols, format_func=lambda x: 'Ninguna' if x is None else x, key=f"sub_color_{i}")
        plot_configs.append(config)

    if st.sidebar.button("Generar Gráficos Acoplados", key="generate_coupled"):
        if plot_configs:
            coupled_fig = create_coupled_plot(df, plot_configs, **layout_params) # Pasa layout_params aquí
            if coupled_fig.data or coupled_fig.layout.annotations:
                plot_area_container.plotly_chart(coupled_fig, use_container_width=True)
                # Exportación para acoplados
                export_container_coupled = plot_area_container.expander("Exportar Gráficos Acoplados")
                # ... (lógica de exportación similar a la de main_plot_ui) ...
            else: plot_area_container.error("No se pudieron generar gráficos acoplados.")