import xarray as xr
import hvplot.xarray
import geopandas as gpd
import geoviews as gv
import panel as pn
from cartopy import crs as ccrs

# Carga los datos de las zonas de aguas costeras
zonas_aguas_costeras = gpd.read_file('zonas_aguas_costeras.geojson')

# Conversión a un objeto de GeoViews para su visualización
gv_zonas_aguas_costeras = gv.Polygons(zonas_aguas_costeras, vdims='nombre_zona').opts(projection=ccrs.PlateCarree(), color=None, line_color='blue', fill_alpha=0.1)

# Ruta al archivo GRIB
archivo_grib = '/home/andreskantim/ecmwf/salidas/201501.grib'

# Abre el archivo GRIB usando xarray y cfgrib como motor
ds = xr.open_dataset(archivo_grib, engine='cfgrib')

variable = 'shww'

# Gráfico de la variable seleccionada
plot = ds[variable].hvplot.quadmesh(
    'longitude', 'latitude',
    cmap='viridis',
    groupby=['time', 'step'],
    widget_type='scrubber',
    widget_location='bottom',
    project=True,
    geo=True,
    coastline=True,
    dynamic=True
)

# Superposición del gráfico con las líneas de costa, zonas de tierra y zonas de aguas costeras
overlay = plot * gv.feature.coastline * gv.feature.land * gv_zonas_aguas_costeras

# Convierte la superposición en un Panel
panel = pn.panel(overlay)

# Sirve tu Panel como una aplicación web
panel.servable()