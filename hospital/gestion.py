"""Operaciones de la agenda de turnos del Hospital Central."""


def datos_vacios():
    return {
        "proximo_paciente": 1,
        "proximo_turno": 1,
        "pacientes": [],
        "profesionales": [],
        "turnos": [],
    }


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
