import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Union

def create_visualization(
    df: pd.DataFrame,
    viz_type: str,
    x: str = None,
    y: str = None,
    color: str = None,
    **kwargs
) -> go.Figure:
    """
    Crea visualizaciones interactivas usando Plotly.
    
    Args:
        df: DataFrame con los datos
        viz_type: Tipo de visualización
        x: Columna para el eje X (o names para pie)
        y: Columna para el eje Y (o values para pie)
        color: Columna para el color/agrupación
        **kwargs: Parámetros adicionales específicos de cada tipo de gráfico
        
    Returns:
        go.Figure: Figura de Plotly
    """
    fig = go.Figure() # Inicializar figura vacía por defecto

    if df.empty:
        # print(f"DataFrame vacío para {viz_type}.") # Para debugging en consola
        return fig # Devuelve figura vacía si no hay datos

    # Validaciones comunes de columnas
    if x and x not in df.columns:
        # print(f"Columna X '{x}' no encontrada en DataFrame para {viz_type}.")
        return fig
    if y and y not in df.columns:
        # print(f"Columna Y '{y}' no encontrada en DataFrame para {viz_type}.")
        return fig
    if color and color not in df.columns:
        # print(f"Columna color '{color}' no encontrada en DataFrame para {viz_type}.")
        # Considerar si 'color' es opcional o si se debe asignar a None
        color = None # Opcional: si la columna de color no existe, no la usamos

    try:
        if viz_type == "bar":
            if not x or not y: return fig
            # Asegurarse que y es numérico si se espera agregación por defecto de px.bar
            # if not pd.api.types.is_numeric_dtype(df[y]): return fig
            fig = px.bar(df, x=x, y=y, color=color, title=f"Gráfico de Barras: {y} por {x}", **kwargs)
        
        elif viz_type == "histogram":
            if not x: return fig
            fig = px.histogram(df, x=x, color=color, title=f"Histograma de {x}", **kwargs)
        
        elif viz_type == "box":
            if not y: return fig # x puede ser None para un boxplot de una sola variable y
            # if x and not pd.api.types.is_numeric_dtype(df[y]): return fig
            # if not x and not pd.api.types.is_numeric_dtype(df[y]): return fig # If y is the only column
            fig = px.box(df, x=x, y=y, color=color, title=f"Boxplot de {y}{f' por {x}' if x else ''}", **kwargs)
        
        elif viz_type == "violin":
            if not y: return fig # Similar to box
            # if x and not pd.api.types.is_numeric_dtype(df[y]): return fig
            # if not x and not pd.api.types.is_numeric_dtype(df[y]): return fig
            fig = px.violin(df, x=x, y=y, color=color, title=f"Violin plot de {y}{f' por {x}' if x else ''}", **kwargs)
        
        elif viz_type == "scatter":
            if not x or not y: return fig
            fig = px.scatter(df, x=x, y=y, color=color, title=f"Dispersión: {y} vs {x}", **kwargs)
        
        elif viz_type == "heatmap":
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.shape[1] < 2:
                # print("Heatmap requiere al menos 2 columnas numéricas.")
                return fig
            corr_matrix = numeric_df.corr()
            fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", title="Heatmap de Correlación", **kwargs)
        
        elif viz_type == "pie":
            if not x or not y: return fig # x es 'names', y es 'values' para pie

            pie_df = df.copy()
            # Asegurarse de que la columna de valores (y) es numérica
            if not pd.api.types.is_numeric_dtype(pie_df[y]):
                # print(f"Columna de valores '{y}' para pie chart no es numérica.")
                return fig
            
            # Manejar NaNs en las columnas relevantes para el pie chart
            pie_df.dropna(subset=[x, y], inplace=True)
            if pie_df.empty:
                # print("DataFrame vacío después de tratar NaNs para pie chart.")
                return fig

            # Agrupar por la columna de etiquetas (x) y sumar los valores (y)
            # Esto es crucial si hay etiquetas duplicadas.
            chart_data = pie_df.groupby(x, as_index=False)[y].sum()

            max_slices = 10  # Número máximo de "porciones" a mostrar directamente
            if len(chart_data) > max_slices:
                # print(f"Demasiadas categorías para pie chart ({len(chart_data)}). Mostrando top {max_slices-1} y 'Otros'.")
                chart_data = chart_data.sort_values(by=y, ascending=False)
                top_n = chart_data.head(max_slices - 1)
                others_sum = chart_data.iloc[max_slices-1:][y].sum()
                if others_sum > 0: # Solo añadir 'Otros' si tiene valor
                    others_df = pd.DataFrame([{x: 'Otros', y: others_sum}])
                    final_chart_data = pd.concat([top_n, others_df], ignore_index=True)
                else:
                    final_chart_data = top_n
            else:
                final_chart_data = chart_data
            
            # Usar 'names=x' y 'values=y'. El 'color' de la función se ignora aquí
            # para un pie chart estándar, px.pie colorea por 'names'.
            # Si quisieras usar la columna 'color' de la función para colorear los segmentos,
            # la lógica de agrupación y el llamado a px.pie necesitarían ajustarse.
            fig = px.pie(final_chart_data, names=x, values=y, title=f"Gráfico de Torta: {y} por {x}", **kwargs)
        
        elif viz_type == "pairplot":
            numeric_df_for_pairplot = df.select_dtypes(include=[np.number])
            if numeric_df_for_pairplot.shape[1] == 0:
                # print("No hay columnas numéricas para Pairplot.")
                return fig
            
            default_dims = numeric_df_for_pairplot.columns[:min(4, len(numeric_df_for_pairplot.columns))]
            dimensions_to_use = kwargs.get('dimensions', default_dims)
            
            # Asegurar que las dimensiones pasadas (si existen) son válidas y están en numeric_df
            if isinstance(dimensions_to_use, list):
                dimensions_to_use = [d for d in dimensions_to_use if d in numeric_df_for_pairplot.columns]
                if not dimensions_to_use: # Si la lista filtrada está vacía, usar default
                    dimensions_to_use = default_dims
            elif not isinstance(dimensions_to_use, list) or not all(d in numeric_df_for_pairplot.columns for d in dimensions_to_use) : # Fallback
                 dimensions_to_use = default_dims

            if not list(dimensions_to_use): # Si dimensions_to_use termina siendo una lista vacía
                 # print("No hay dimensiones válidas para Pairplot después de filtrar.")
                 return fig

            fig = px.scatter_matrix(numeric_df_for_pairplot, dimensions=dimensions_to_use, title="Pairplot (Scatter Matrix)")
        
        elif viz_type == "slope":
            if not x or not y or not color: return fig
            
            # Asegúrate que las columnas x e y son numéricas si es lo esperado para un slope chart
            # if not pd.api.types.is_numeric_dtype(df[x]) or not pd.api.types.is_numeric_dtype(df[y]):
            #     print("Columnas X o Y no numéricas para Slope chart.")
            #     return fig

            fig = go.Figure() # Re-inicializar para slope, ya que usa go.Scatter directamente
            unique_categories = df[color].unique()
            for category_val in unique_categories:
                mask = df[color] == category_val
                trace_df = df[mask]
                if not trace_df.empty:
                    fig.add_trace(go.Scatter(
                        x=trace_df[x],
                        y=trace_df[y],
                        name=str(category_val),  # <--- IMPORTANTE: Convertir 'name' a string
                        mode='lines+markers'
                    ))
            fig.update_layout(title=f"Slope Chart: {y} por {x}, agrupado por {color}")
        
        else:
            # print(f"Tipo de visualización '{viz_type}' no soportado")
            # Se devuelve la figura vacía inicializada al principio
            pass 
            # O podrías levantar un error: raise ValueError(f"Tipo de visualización '{viz_type}' no soportado")
    
    except Exception as e:
        # print(f"Error al crear visualización '{viz_type}': {e}") # Para debugging en consola
        # Devuelve una figura vacía en caso de cualquier otra excepción no controlada
        return go.Figure()

    # Personalización general (solo si fig no es la inicial vacía y tiene datos)
    if fig.data: # Solo aplicar si la figura tiene trazas
        fig.update_layout(
            template="plotly_white", # Puedes cambiar a "plotly_dark" si usas tema oscuro en Streamlit
            showlegend=True,
            height=600,
            # width=800 # Considera dejar que Streamlit maneje el ancho o usa use_container_width=True en st.plotly_chart
            legend_title_text=str(color) if color else None,
            margin=dict(l=50, r=50, t=50, b=50) # Ajustar márgenes si es necesario
        )
    
    return fig

def export_plot(fig: go.Figure, format: str = "png", dpi: int = 300, width: int = 1000, height: int = 600) -> bytes:
    """
    Exporta la figura a diferentes formatos.
    
    Args:
        fig: Figura de Plotly
        format: Formato de exportación ('png', 'pdf', 'svg', 'jpeg')
        dpi: Resolución para PNG
        width: Ancho de la imagen exportada
        height: Alto de la imagen exportada
        
    Returns:
        bytes: Datos de la imagen
    """
    if not fig.data: # No exportar si la figura está vacía
        # print("Intento de exportar figura vacía.")
        return b""

    scale_factor = dpi / 100 # Plotly usa 'scale' para PNG donde 1 = 100 DPI (aprox)
    
    # kaleido es necesario para exportar imágenes estáticas
    try:
        if format in ["png", "jpeg", "webp", "svg", "pdf", "eps"]:
            return fig.to_image(format=format, width=width, height=height, scale=scale_factor if format=='png' else None)
        else:
            # print(f"Formato de exportación '{format}' no soportado.")
            raise ValueError(f"Formato '{format}' no soportado para exportación.")
    except Exception as e:
        # print(f"Error al exportar la figura a {format}: {e}")
        # Esto puede suceder si 'kaleido' no está instalado: pip install kaleido
        # O si hay algún problema con la figura en sí.
        st.error(f"Error al exportar la figura: {e}. Asegúrate de tener 'kaleido' instalado (`pip install kaleido`)")
        return b""

