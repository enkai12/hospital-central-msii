"""Operaciones de la agenda de turnos del Hospital Central."""

import json
import shutil
from datetime import datetime

FRANJAS = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"]
ACTIVO = "ACTIVO"
CANCELADO = "CANCELADO"


def cargar_datos(ruta, ruta_ejemplo):
    if not ruta.exists():
        shutil.copyfile(ruta_ejemplo, ruta)
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_datos(datos, ruta):
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def registrar_paciente(datos, nombre):
    nombre = nombre.strip()
    if nombre == "":
        return False, "El nombre no puede estar vacío."

    paciente = {"id": datos["proximo_paciente"], "nombre": nombre}
    datos["pacientes"].append(paciente)
    datos["proximo_paciente"] += 1
    return True, f"Paciente registrado con el número {paciente['id']}."


def listar_pacientes(datos):
    return sorted(datos["pacientes"], key=lambda paciente: paciente["id"])


def reservar_turno(datos, paciente_id, profesional_id, fecha, hora):
    paciente = None
    for p in datos["pacientes"]:
        if p["id"] == paciente_id:
            paciente = p
    if paciente is None:
        return False, "No existe un paciente con ese número."

    profesional = None
    for p in datos["profesionales"]:
        if p["id"] == profesional_id:
            profesional = p
    if profesional is None:
        return False, "No existe un profesional con ese número."

    try:
        fecha_valida = datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        return False, "La fecha no es válida. Usá el formato AAAA-MM-DD."
    if fecha_valida.strftime("%Y-%m-%d") != fecha:
        return False, "La fecha no es válida. Usá el formato AAAA-MM-DD."

    if hora not in FRANJAS:
        return False, "El horario tiene que ser una de las franjas: " + ", ".join(
            FRANJAS
        )

    for turno in datos["turnos"]:
        if turno["estado"] == ACTIVO and turno["fecha"] == fecha:
            if turno["hora"] == hora and turno["profesional_id"] == profesional_id:
                return False, "El profesional ya tiene un turno en esa fecha y horario."
            if turno["hora"] == hora and turno["paciente_id"] == paciente_id:
                return False, "El paciente ya tiene un turno en esa fecha y horario."

    turno = {
        "id": datos["proximo_turno"],
        "paciente_id": paciente_id,
        "profesional_id": profesional_id,
        "fecha": fecha,
        "hora": hora,
        "estado": ACTIVO,
    }
    datos["turnos"].append(turno)
    datos["proximo_turno"] += 1
    return True, (
        f"Turno {turno['id']} reservado: {paciente['nombre']} con "
        f"{profesional['nombre']} el {fecha} a las {hora}."
    )


def cancelar_turno(datos, turno_id):
    turno = None
    for t in datos["turnos"]:
        if t["id"] == turno_id:
            turno = t
    if turno is None:
        return False, "No existe un turno con ese número."
    if turno["estado"] == CANCELADO:
        return False, "Ese turno ya estaba cancelado."

    turno["estado"] = CANCELADO
    return True, f"Turno {turno_id} cancelado. La franja quedó libre."


def agenda_profesional(datos, profesional_id, fecha):
    profesional = None
    for p in datos["profesionales"]:
        if p["id"] == profesional_id:
            profesional = p
    if profesional is None:
        return False, "No existe un profesional con ese número."

    try:
        fecha_valida = datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        return False, "La fecha no es válida. Usá el formato AAAA-MM-DD."
    if fecha_valida.strftime("%Y-%m-%d") != fecha:
        return False, "La fecha no es válida. Usá el formato AAAA-MM-DD."

    agenda = []
    for hora in FRANJAS:
        ocupado_por = None
        for turno in datos["turnos"]:
            if (
                turno["profesional_id"] == profesional_id
                and turno["fecha"] == fecha
                and turno["hora"] == hora
                and turno["estado"] == ACTIVO
            ):
                for p in datos["pacientes"]:
                    if p["id"] == turno["paciente_id"]:
                        ocupado_por = {"turno_id": turno["id"], "paciente": p["nombre"]}
        agenda.append({"hora": hora, "turno": ocupado_por})
    return True, agenda


def historial_paciente(datos, paciente_id):
    paciente = None
    for p in datos["pacientes"]:
        if p["id"] == paciente_id:
            paciente = p
    if paciente is None:
        return False, "No existe un paciente con ese número."

    historial = []
    for turno in datos["turnos"]:
        if turno["paciente_id"] == paciente_id:
            for p in datos["profesionales"]:
                if p["id"] == turno["profesional_id"]:
                    historial.append({**turno, "profesional": p["nombre"]})
    historial.sort(key=lambda t: (t["fecha"], t["hora"], t["id"]))
    return True, historial
