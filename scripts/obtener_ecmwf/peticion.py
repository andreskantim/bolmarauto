#!/usr/bin/env python
from ecmwfapi import ECMWFService
import calendar
import os

# Crea una instancia del servicio ECMWF
server = ECMWFService("mars")

# Define el año y el mes que deseas solicitar
year = "2023"
month = "05"
day = "01-02"
target_path = f"../../datos/modelo/cantabria/{year}.grib"

    # Configura los parámetros de tu solicitud
request_params = {
        "class": "od",
        "date": "20230101", #"20140423/to/hoy"
        "domain": "g",
        "expver": "1",
        "param": "234.140/237.140/238.140/245.140/249.140",
        "step": "12/to/36/by/3",
        "stream": "wave",
        "time": "00:00:00",
        "type": "fc",
        "accuracy": "ac",
        "area": "43.84/-4.51/43.46/-3.16",
        "grid": "0.125/0.125",
    }

server.execute(request_params, target_path)