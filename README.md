# Dashboard Interactivo de Análisis Exploratorio

Este proyecto implementa un dashboard interactivo para el análisis exploratorio de datos complejos, permitiendo cargar, explorar y visualizar datasets con funcionalidades avanzadas de filtrado, partición de datos y generación de visualizaciones dinámicas.

## Características Principales

- **Carga de Datos**
  - Soporte para múltiples formatos (CSV, Parquet)
  - Conexión a MongoDB Atlas
  - Conexión a APIs REST
  - Detección automática de tipos de columnas

- **Interfaz Interactiva**
  - Selectores para columnas
  - Filtros dinámicos
  - Combinación de condiciones (AND/OR)

- **Visualizaciones**
  - Gráficos básicos (barras, histogramas, boxplots, etc.)
  - Gráficos acoplados
  - Gráficos avanzados (pairplot, slope chart, etc.)
  - Exportación a PNG/PDF

- **Partición de Datos**
  - Muestreo aleatorio simple
  - Muestreo estratificado
  - División temporal

## Requisitos

- Python 3.8+
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd dashboard-analitico
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Iniciar la aplicación:
```bash
streamlit run app.py
```

2. Abrir el navegador en `http://localhost:8501`

## Estructura del Proyecto

```
dashboard-analitico/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── README.md          # Documentación
├── data/              # Datos de ejemplo
├── assets/            # Recursos estáticos
└── utils/             # Módulos de utilidad
    ├── data_loader.py
    ├── visualizations.py
    └── data_processing.py
```

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Tu Nombre - [@tutwitter](https://twitter.com/tutwitter) - email@example.com

Link del Proyecto: [https://github.com/tuusuario/dashboard-analitico](https://github.com/tuusuario/dashboard-analitico) 