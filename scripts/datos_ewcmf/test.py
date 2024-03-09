#!/usr/bin/env python
from ecmwfapi import ECMWFService
import calendar
import os

# Crea una instancia del servicio ECMWF
server = ECMWFService("mars")

# Define el año y el mes que deseas solicitar
year = "2015"
month = "01"

# Calcula el número de días en el mes
_, num_days = calendar.monthrange(int(year), int(month))

# Bucle a través de cada día del mes
for day in range(1, num_days + 1):
    # Formatea el día para asegurar el formato correcto (ej. "01", "02", ...)
    day_str = f"{day:02d}"

    # Configura los parámetros de tu solicitud
    request_params = {
        "class": "od",
        "date": f"{year}{month}{day_str}",
        "domain": "g",
        "expver": "1",
        "param": "234.140/235.140/237.140/238.140/245.140/249.140",
        "step": "12/to/36/by/3",
        "stream": "wave",
        "time": "00:00:00",
        "type": "fc",
        "accuracy": "ac",
        "area": "45/-5/44/-3",
        "grid": "0.125/0.125",
    }

    # Define la ruta de destino para el archivo de salida
    target_path = f"/home/andreskantim/ecmwf/datos/modelo/{year}{month}{day_str}.grib"

    # Ejecuta la solicitud con los parámetros definidos
    print(f"Retrieving data for {year}-{month}-{day_str}")
    server.execute(request_params, target_path)