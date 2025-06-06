# utils/visualizations.py
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Union
from plotly.subplots import make_subplots

def create_visualization(
    df: pd.DataFrame,
    viz_type: str,
    x: str = None,
    y: Union[str, List[str]] = None, # y puede ser string o lista (para radar)
    y2: str = None,
    color: str = None,
    size: str = None,
    facet_row: str = None,
    facet_col: str = None,
    orientation: str = 'v',
    barmode: str = 'relative',
    nbins: int = None,
    histnorm: str = None,
    show_kde: bool = False,
    boxmode: str = 'overlay',
    points: Union[str, bool] = 'outliers',
    show_outliers: bool = True,
    violinmode: str = 'overlay',
    inner_violin: str = None,
    marker_shape: str = None,
    opacity_scatter: float = None,
    annot_heatmap: bool = True,
    cmap_heatmap: str = "viridis",
    hole_pie: float = 0,
    slope_marker_color_positive: str = 'green',
    slope_marker_color_negative: str = 'red',
    **kwargs
) -> go.Figure:
    
    fig = go.Figure()
    if df.empty and viz_type not in ["heatmap_corr_empty_ok"]:
        return fig

    if x and x not in df.columns: return fig
    
    # Corrección para y (puede ser lista para radar)
    if y:
        if isinstance(y, list): # Caso Radar u otro que use lista para Y
            for col_y_item in y:
                if col_y_item not in df.columns: return fig # Si alguna columna de la lista no existe
        elif y not in df.columns: # Caso y es un string
            return fig
            
    if y2 and y2 not in df.columns: return fig
    if color and color not in df.columns: color = None
    if size and size not in df.columns: size = None

    try:
        if viz_type == "bar":
            if not x: return fig
            if not y:
                bar_df = df[x].value_counts().reset_index()
                bar_df.columns = [x, 'count']
                fig = px.bar(bar_df, x=x, y='count', color=color if color in bar_df.columns else None,
                             orientation=orientation, barmode=barmode, title=f"Frecuencia de {x}")
            else:
                fig = px.bar(df, x=x, y=y, color=color, orientation=orientation, barmode=barmode,
                             title=f"Gráfico de Barras: {y} por {x}")

        elif viz_type == "histogram":
            if not x: return fig
            fig = px.histogram(df, x=x, color=color, nbins=nbins, histnorm=histnorm,
                               title=f"Histograma de {x}", opacity=kwargs.get('opacity', None))

        elif viz_type == "box":
            if not y: 
                if not x or x not in df.columns: return fig 
                fig = px.box(df, y=x, points=points, title=f"Boxplot de {x}", color=color)
            else: 
                if x and x not in df.columns: x = None 
                fig = px.box(df, x=x, y=y, color=color, points=points,
                             title=f"Boxplot de {y}{f' por {x}' if x else ''}")
            if not show_outliers and points == 'outliers': 
                fig.update_traces(boxpoints=False) 

        elif viz_type == "violin":
            if not y: 
                if not x or x not in df.columns: return fig
                fig = px.violin(df, y=x, points=points, box=(inner_violin=='box'), 
                                title=f"Violin Plot de {x}", color=color)
            else: 
                if x and x not in df.columns: x = None
                fig = px.violin(df, x=x, y=y, color=color, points=points, box=(inner_violin=='box'),
                                title=f"Violin Plot de {y}{f' por {x}' if x else ''}")

        elif viz_type == "scatter":
            if not x or not y: return fig
            fig = px.scatter(df, x=x, y=y, color=color, size=size,
                             opacity=opacity_scatter, symbol=marker_shape,
                             title=f"Dispersión: {y} vs {x}",
                             trendline=kwargs.get("trendline", None), 
                             facet_row=facet_row, facet_col=facet_col)

        elif viz_type == "heatmap_corr":
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.shape[1] < 2: return fig
            corr_matrix = numeric_df.corr()
            fig = px.imshow(corr_matrix, text_auto=annot_heatmap, aspect="auto",
                            color_continuous_scale=cmap_heatmap, title="Heatmap de Correlación")

        elif viz_type == "heatmap_crosstab":
            if not x or not y: return fig
            crosstab_df = pd.crosstab(df[x], df[y])
            fig = px.imshow(crosstab_df, text_auto=annot_heatmap, aspect="auto",
                            color_continuous_scale=cmap_heatmap, title=f"Heatmap: Frecuencias de {x} vs {y}")
        
        elif viz_type == "pie":
            if not x or not y : return fig
            pie_df_prep = df.copy()
            if not pd.api.types.is_numeric_dtype(pie_df_prep[y]): return fig
            pie_df_prep.dropna(subset=[x, y], inplace=True)
            if pie_df_prep.empty: return fig
            chart_data = pie_df_prep.groupby(x, as_index=False)[y].sum()
            fig = px.pie(chart_data, names=x, values=y, title=f"Gráfico Circular de {y} por {x}",
                         hole=hole_pie, color=color if color in chart_data.columns else None)
            fig.update_traces(textinfo='percent+label+value', pull=kwargs.get('pull_pie', None))

        elif viz_type == "pairplot":
            numeric_df_for_pairplot = df.select_dtypes(include=[np.number])
            if numeric_df_for_pairplot.shape[1] == 0: return fig
            default_dims = list(numeric_df_for_pairplot.columns[:min(5, len(numeric_df_for_pairplot.columns))])
            dimensions_to_use = kwargs.get('dimensions', default_dims)
            valid_dimensions = [d for d in dimensions_to_use if d in numeric_df_for_pairplot.columns]
            if not valid_dimensions: valid_dimensions = default_dims
            if not valid_dimensions: return fig
            fig = px.scatter_matrix(numeric_df_for_pairplot, dimensions=valid_dimensions, color=color,
                                    title="Pairplot (Matriz de Dispersión)")
        
        elif viz_type == "slope":
            if not x or not y or not color: return fig # y2 no se usa directamente, se espera que x tenga 2 puntos
            df_slope = df[[x, y, color]].copy()
            time_points = df_slope[x].unique()
            if len(time_points) != 2:
                return go.Figure(layout={"title_text": "Slope Chart: Error - Se requieren 2 puntos en X"})
            try:
                slope_pivot = df_slope.pivot(index=color, columns=x, values=y).reset_index()
                if slope_pivot.shape[1] !=3: 
                    raise ValueError("Pivot no resultó en 3 columnas")
                val_col_A, val_col_B = slope_pivot.columns[1], slope_pivot.columns[2]
            except Exception as e:
                return go.Figure(layout={"title_text": f"Slope Chart: Error pivoteando datos ({e})"})

            fig_slope = go.Figure()
            for _, row in slope_pivot.iterrows():
                entity, val_a, val_b = row[color], row[val_col_A], row[val_col_B]
                line_color = 'grey'
                if pd.notna(val_a) and pd.notna(val_b):
                    if val_b > val_a: line_color = slope_marker_color_positive
                    elif val_b < val_a: line_color = slope_marker_color_negative
                fig_slope.add_trace(go.Scatter(
                    x=[time_points[0], time_points[1]], y=[val_a, val_b], mode='lines+markers+text',
                    name=str(entity), line=dict(color=line_color, width=2), marker=dict(size=8),
                    text=[f"{val_a:.2f}" if pd.notna(val_a) else "", f"{val_b:.2f}" if pd.notna(val_b) else ""], 
                    textposition="top right"
                ))
            fig_slope.update_layout(title=f"Slope Chart: {y} de {time_points[0]} a {time_points[1]} por {color}",
                                  xaxis_title=str(x), yaxis_title=str(y), showlegend=True)
            fig = fig_slope
            
        elif viz_type == "radar":
            if not y or not isinstance(y, list): # y DEBE ser una lista de columnas
                return go.Figure(layout={"title_text": "Radar Chart: 'y' debe ser lista de columnas"})

            radar_df = df.copy()
            fig_radar = go.Figure()
            
            if x and x in radar_df.columns:
                if color and color == x: color = None
                grouped_radar = radar_df.groupby(x)[y].mean().reset_index()
                for i, row in grouped_radar.iterrows():
                    category_name = str(row[x])
                    values = row[y].values.flatten().tolist()
                    fig_radar.add_trace(go.Scatterpolar(r=values + [values[0]], theta=y + [y[0]],
                                                       fill='toself', name=category_name))
            elif len(df) >= 1 or not x : 
                if radar_df.empty: return fig
                values_series = radar_df[y].mean() if len(radar_df) > 1 and not x else radar_df[y].iloc[0] # Promedio o primera fila
                values = values_series.values.flatten().tolist()

                fig_radar.add_trace(go.Scatterpolar(r=values + [values[0]], theta=y + [y[0]],
                                                   fill='toself', name=kwargs.get('radar_trace_name', 'Radar')))
            else:
                 return go.Figure(layout={"title_text": "Radar Chart: Configuración no válida para 'x'"})

            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=kwargs.get('radar_range', None))),
                                  showlegend=True if x and len(grouped_radar)>1 else False, 
                                  title=f"Radar Chart" + (f" por {x}" if x else ""))
            fig = fig_radar

        elif viz_type == "diverging_bars":
            if not x or not y: return fig
            fig = px.bar(df, x=x, y=y, color=y, 
                         color_continuous_scale=px.colors.diverging.RdBu,
                         color_continuous_midpoint=0, 
                         title=f"Barras Divergentes: {y} por {x}")
        
        elif viz_type == "box_violin_combined":
            y_col_for_combined, x_col_for_combined, title_suffix = (x, None, x) if not y else (y, x if x in df.columns else None, f"{y}{f' por {x}' if x else ''}")

            fig_combined = go.Figure()
            if x_col_for_combined:
                for i, cat_val in enumerate(df[x_col_for_combined].unique()):
                    df_cat = df[df[x_col_for_combined] == cat_val]
                    fig_combined.add_trace(go.Violin(y=df_cat[y_col_for_combined], name=str(cat_val) + " (Violin)", legendgroup=str(cat_val), scalegroup=str(cat_val), points=points, side='positive', line_color=px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]))
                    fig_combined.add_trace(go.Box(y=df_cat[y_col_for_combined], name=str(cat_val) + " (Box)", legendgroup=str(cat_val), marker_color=px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)], boxpoints=False, width=0.2))
            else:
                 fig_combined.add_trace(go.Violin(y=df[y_col_for_combined], name="Violin", points=points))
                 fig_combined.add_trace(go.Box(y=df[y_col_for_combined], name="Box", boxpoints=False, width=0.2))
            
            fig_combined.update_layout(title=f"Boxplot + Violin Combinado: {title_suffix}", showlegend=True if x_col_for_combined else False, yaxis_title=y_col_for_combined, xaxis_title=x_col_for_combined if x_col_for_combined else "")
            fig = fig_combined
        else:
            pass 
    except Exception as e:
        return go.Figure(layout=go.Layout(title=go.layout.Title(text=f"Error generando {viz_type}: {e}")))

    if fig.data and not viz_type in ["slope", "radar", "box_violin_combined"]:
        fig.update_layout(template=kwargs.get("plotly_template", "plotly_white"), showlegend=True,
                          height=kwargs.get("fig_height", 600), legend_title_text=str(color) if color else None,
                          margin=dict(l=60, r=50, t=70, b=60), title_x=0.5)
    return fig


def create_coupled_plot(df: pd.DataFrame, plot_configs: List[Dict[str, Any]], **kwargs) -> go.Figure: # Añadido **kwargs
    if not plot_configs or len(plot_configs) > 4:
        return go.Figure(layout={"title_text":"Configuración de gráficos acoplados inválida"})

    rows = kwargs.get("subplot_rows", 1) # Extraer de kwargs
    cols = kwargs.get("subplot_cols", len(plot_configs)) # Extraer de kwargs
    if rows * cols < len(plot_configs):
        cols = int(np.ceil(len(plot_configs)/rows))
        if rows * cols < len(plot_configs) and rows < len(plot_configs) : # Si sigue sin caber, aumentar filas
            rows = int(np.ceil(len(plot_configs)/cols))


    subplot_titles = [f"{config.get('viz_type', '').capitalize()}{f' de {config.get('x')}' if config.get('x') else ''}{f' vs {config.get('y')}' if config.get('y') else ''}" for config in plot_configs]

    try:
        fig_subplots = make_subplots(rows=rows, cols=cols, subplot_titles=subplot_titles)
    except Exception as e:
        return go.Figure(layout={"title_text": f"Error creando subplots: {e}"})

    for i, config in enumerate(plot_configs):
        row_idx = (i // cols) + 1
        col_idx = (i % cols) + 1
        params_for_subfig = {k: v for k, v in config.items() if k != 'viz_type'}
        sub_fig = create_visualization(df, viz_type=config['viz_type'], **params_for_subfig)
        
        if not sub_fig.data:
            fig_subplots.add_annotation(text=f"No data for {config['viz_type']}", xref="paper", yref="paper",
                                        x= (col_idx - 0.5) / cols, y= 1 - ((row_idx - 0.5) / rows), 
                                        showarrow=False, row=row_idx, col=col_idx)
            continue
        for trace in sub_fig.data:
            fig_subplots.add_trace(trace, row=row_idx, col=col_idx)

    fig_subplots.update_layout(height=kwargs.get("coupled_fig_height", 700), 
                               showlegend=kwargs.get("showlegend_coupled", True),
                               title_text=kwargs.get("coupled_plot_title", "Gráficos Acoplados"))
    return fig_subplots


def export_plot(fig: go.Figure, format: str = "png", dpi: int = 300, width: int = 1000, height: int = 600) -> bytes:
    if not fig.data and not fig.layout.annotations: 
        return b""
    scale_factor = dpi / 100 
    try:
        if format in ["png", "jpeg", "webp", "svg", "pdf", "eps"]:
            return fig.to_image(format=format, width=width, height=height, scale=scale_factor if format=='png' else None)
        else:
            raise ValueError(f"Formato '{format}' no soportado para exportación.")
    except Exception as e:
        raise