import xarray as xr
import os
from glob import glob

# Rutas a las carpetas
carpeta_entrada = '../../datos/modelo/FQXX41MM/asturias'
carpeta_salida_este = '../../datos/modelo/FQXX41MM/asturias_este'
carpeta_salida_oeste = '../../datos/modelo/FQXX41MM/asturias_oeste'

# Crear carpetas de salida si no existen
os.makedirs(carpeta_salida_este, exist_ok=True)
os.makedirs(carpeta_salida_oeste, exist_ok=True)

# Definir las longitudes
longitudes_oeste = slice(-7.02, -5.85)
longitudes_este = slice(-5.85, -4.51)

# Obtener todos los archivos .grib de la carpeta de entrada
archivos_grib = glob(os.path.join(carpeta_entrada, '*.grib'))

for archivo in archivos_grib:
    # Leer el archivo grib
    ds = xr.open_dataset(archivo, engine='cfgrib')

    # Recortar los datos por longitudes
    ds_oeste = ds.sel(longitude=longitudes_oeste)
    ds_este = ds.sel(longitude=longitudes_este)

    # Nombre del archivo de salida
    nombre_archivo = os.path.basename(archivo)
    archivo_salida_oeste = os.path.join(carpeta_salida_oeste, nombre_archivo)
    archivo_salida_este = os.path.join(carpeta_salida_este, nombre_archivo)

    # Guardar los nuevos archivos grib
    ds_oeste.to_netcdf(archivo_salida_oeste)
    ds_este.to_netcdf(archivo_salida_este)

    # Cerrar los datasets
    ds.close()
    ds_oeste.close()
    ds_este.close()

print("Archivos procesados y guardados exitosamente.")