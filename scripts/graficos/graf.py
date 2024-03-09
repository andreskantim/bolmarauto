import xarray as xr
import matplotlib.pyplot as plt

# Ruta al archivo GRIB
archivo_grib = '/home/andreskantim/ecmwf/datos/modelo/201501.grib'

# Abre el archivo GRIB usando xarray y cfgrib como motor
ds = xr.open_dataset(archivo_grib, engine='cfgrib')

ds_sel = ds.isel(time=7)

# Asegúrate de tener una cuadrícula de longitud y latitud para el plotting
longitudes = ds_sel.longitude
latitudes = ds_sel.latitude

# Obtén todos los steps disponibles
steps = ds_sel.step

# Crea un mapa para cada step
for step in steps:
    plt.figure(figsize=(10, 6))
    
    # Selecciona los datos para el step actual
    data_step = ds_sel.sel(step=step)['shww']
    
    # Utiliza pcolormesh para trazar los datos. Asegúrate de que tus datos estén en las formas correctas.
    plt.pcolormesh(longitudes, latitudes, data_step, shading='auto')
    
    # Agrega características al plot
    plt.colorbar(label='shww (m)')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    plt.title(f'SHWW para step {step.values}')
    plt.show()