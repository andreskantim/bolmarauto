#!/usr/bin/env python
from ecmwfapi import ECMWFService
import calendar
import os

# Crea una instancia del servicio ECMWF
server = ECMWFService("mars")

# Define el año y el mes que deseas solicitar
year = "2015"
month = "04"
target_path = f"/home/andreskantim/ecmwf/salidas/{year}{month}.grib"

    # Configura los parámetros de tu solicitud
request_params = {
        "class": "od",
        "date": "20150401/to/20150430",
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

server.execute(request_params, target_path)