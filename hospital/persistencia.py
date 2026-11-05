"""Lectura y escritura de los datos de la agenda en un archivo JSON."""

import json
import os
import shutil


def cargar_datos(ruta, ruta_ejemplo):
    if not ruta.exists():
        shutil.copyfile(ruta_ejemplo, ruta)
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_datos(datos, ruta):
    ruta_temporal = ruta.with_name(ruta.name + ".tmp")
    try:
        with open(ruta_temporal, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
        os.replace(ruta_temporal, ruta)
    except BaseException:
        ruta_temporal.unlink(missing_ok=True)
        raise
