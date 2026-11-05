"""Operaciones de la agenda de turnos del Hospital Central."""

from datetime import datetime

FRANJAS = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"]
ACTIVO = "ACTIVO"
CANCELADO = "CANCELADO"


def buscar_por_id(elementos, id_buscado):
    for elemento in elementos:
        if elemento["id"] == id_buscado:
            return elemento
    return None


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
    paciente = buscar_por_id(datos["pacientes"], paciente_id)
    if paciente is None:
        return False, "No existe un paciente con ese número."

    profesional = buscar_por_id(datos["profesionales"], profesional_id)
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
    turno = buscar_por_id(datos["turnos"], turno_id)
    if turno is None:
        return False, "No existe un turno con ese número."
    if turno["estado"] == CANCELADO:
        return False, "Ese turno ya estaba cancelado."

    turno["estado"] = CANCELADO
    return True, f"Turno {turno_id} cancelado. La franja quedó libre."


def agenda_profesional(datos, profesional_id, fecha):
    profesional = buscar_por_id(datos["profesionales"], profesional_id)
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
                paciente = buscar_por_id(datos["pacientes"], turno["paciente_id"])
                if paciente is not None:
                    ocupado_por = {
                        "turno_id": turno["id"],
                        "paciente": paciente["nombre"],
                    }
        agenda.append({"hora": hora, "turno": ocupado_por})
    return True, agenda


def historial_paciente(datos, paciente_id):
    paciente = buscar_por_id(datos["pacientes"], paciente_id)
    if paciente is None:
        return False, "No existe un paciente con ese número."

    historial = []
    for turno in datos["turnos"]:
        if turno["paciente_id"] == paciente_id:
            profesional = buscar_por_id(datos["profesionales"], turno["profesional_id"])
            if profesional is not None:
                historial.append({**turno, "profesional": profesional["nombre"]})
    historial.sort(key=lambda t: (t["fecha"], t["hora"], t["id"]))
    return True, historial
