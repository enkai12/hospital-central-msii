"""Lectura y escritura de los datos de la agenda en un archivo JSON."""

import json
import shutil


def cargar_datos(ruta, ruta_ejemplo):
    if not ruta.exists():
        shutil.copyfile(ruta_ejemplo, ruta)
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_datos(datos, ruta):
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
