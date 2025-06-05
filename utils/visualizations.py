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
        x: Columna para el eje X
        y: Columna para el eje Y
        color: Columna para el color
        **kwargs: Parámetros adicionales específicos de cada tipo de gráfico
        
    Returns:
        go.Figure: Figura de Plotly
    """
    if viz_type == "bar":
        fig = px.bar(df, x=x, y=y, color=color, **kwargs)
    
    elif viz_type == "histogram":
        fig = px.histogram(df, x=x, color=color, **kwargs)
    
    elif viz_type == "box":
        fig = px.box(df, x=x, y=y, color=color, **kwargs)
    
    elif viz_type == "violin":
        fig = px.violin(df, x=x, y=y, color=color, **kwargs)
    
    elif viz_type == "scatter":
        fig = px.scatter(df, x=x, y=y, color=color, **kwargs)
    
    elif viz_type == "heatmap":
        corr_matrix = df.select_dtypes(include=[np.number]).corr()
        fig = px.imshow(corr_matrix, **kwargs)
    
    elif viz_type == "pie":
        fig = px.pie(df, names=x, values=y, color=color, **kwargs)
    
    elif viz_type == "pairplot":
        fig = px.scatter_matrix(df, dimensions=kwargs.get('dimensions', df.columns[:4]))
    
    elif viz_type == "slope":
        fig = go.Figure()
        for category in df[color].unique():
            mask = df[color] == category
            fig.add_trace(go.Scatter(
                x=df[mask][x],
                y=df[mask][y],
                name=category,
                mode='lines+markers'
            ))
    
    else:
        raise ValueError(f"Tipo de visualización '{viz_type}' no soportado")
    
    # Personalización general
    fig.update_layout(
        template="plotly_white",
        showlegend=True,
        height=600,
        width=800
    )
    
    return fig

def export_plot(fig: go.Figure, format: str = "png", dpi: int = 300) -> bytes:
    """
    Exporta la figura a diferentes formatos.
    
    Args:
        fig: Figura de Plotly
        format: Formato de exportación ('png' o 'pdf')
        dpi: Resolución para PNG
        
    Returns:
        bytes: Datos de la imagen
    """
    if format == "png":
        return fig.to_image(format="png", width=800, height=600, scale=dpi/100)
    elif format == "pdf":
        return fig.to_image(format="pdf", width=800, height=600)
    else:
        raise ValueError(f"Formato '{format}' no soportado") 