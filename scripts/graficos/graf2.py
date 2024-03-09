#panel serve graf2.py

import xarray as xr
import hvplot.xarray  # Importa hvplot para xarray
import panel as pn

# Ruta al archivo GRIB
archivo_grib = '/home/andreskantim/ecmwf/datos/modelo/201501.grib'

# Abre el archivo GRIB usando xarray y cfgrib como motor
ds = xr.open_dataset(archivo_grib, engine='cfgrib')

variable = 'shww'

# Utiliza hvplot para hacer un gráfico interactivo
# Asegúrate de tener dimensiones 'latitude' y 'longitude' en tu Dataset. Ajusta los nombres según sea necesario.
plot = ds[variable].hvplot.quadmesh(
    'longitude', 'latitude',
    cmap='viridis',  # Esquema de colores
    groupby=['time', 'step'],  # Interactuar con 'time' y 'step'
    widget_type='scrubber',  # Tipo de widget para interacción
    widget_location='bottom',  # Ubicación de los controles interactivos
    project=True,  # Proyectar las coordenadas (útil para datos geográficos)
    geo=True,  # Habilita opciones geográficas, como superponer mapas base
    coastline=True,  # Añade líneas de costa al gráfico
    dynamic=True  # Carga los datos dinámicamente para mejorar el rendimiento con grandes datasets
)
# Convierte tu visualización en un Panel
panel = pn.panel(plot)

# Sirve tu Panel como una aplicación web
panel.servable()
