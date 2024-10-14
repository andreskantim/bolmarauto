import xarray as xr

# Ruta al archivo GRIB
archivo_grib = '../../datos/modelo/FQXX41MM/asturias_este/202403.grib'

# Abre el archivo GRIB usando xarray y cfgrib como motor
ds = xr.open_dataset(archivo_grib, engine='cfgrib')

v1 = 'longitude'
v2 = 'latitude'
v3 = 'time'

print(ds[v1])
print(ds[v2])
# print(ds[v3])