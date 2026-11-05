from pathlib import Path

from hospital import gestion, persistencia

RUTA_EJEMPLO = Path(__file__).parent / "datos" / "ejemplo.json"
RUTA_LOCAL = Path(__file__).parent / "datos" / "local.json"

MENU = """
Hospital Central - Agenda de turnos
1. Registrar paciente
2. Listar pacientes
3. Reservar turno
4. Cancelar turno
5. Consultar la agenda de un profesional
6. Consultar los turnos de un paciente
0. Salir"""


def pedir_numero(texto):
    valor = input(texto).strip()
    try:
        return int(valor)
    except ValueError:
        return None


def main():
    try:
        datos = persistencia.cargar_datos(RUTA_LOCAL, RUTA_EJEMPLO)
    except ValueError:
        print("No se pudo leer datos/local.json: el archivo está dañado.")
        print("Revisalo o borralo para empezar de nuevo con los datos de ejemplo.")
        return

    while True:
        print(MENU)
        opcion = input("Opción: ").strip()

        if opcion == "1":
            nombre = input("Nombre del paciente: ")
            ok, mensaje = gestion.registrar_paciente(datos, nombre)
            if ok:
                persistencia.guardar_datos(datos, RUTA_LOCAL)
            print(mensaje)
        elif opcion == "2":
            pacientes = gestion.listar_pacientes(datos)
            if not pacientes:
                print("No hay pacientes registrados.")
            for paciente in pacientes:
                print(f"{paciente['id']}. {paciente['nombre']}")
        elif opcion == "3":
            for profesional in datos["profesionales"]:
                print(
                    f"{profesional['id']}. {profesional['nombre']} "
                    f"({profesional['especialidad']})"
                )
            paciente_id = pedir_numero("Número de paciente: ")
            profesional_id = pedir_numero("Número de profesional: ")
            fecha = input("Fecha (AAAA-MM-DD): ").strip()
            hora = input("Horario (HH:MM): ").strip()
            if paciente_id is None or profesional_id is None:
                print("El número de paciente y de profesional tiene que ser entero.")
            else:
                ok, mensaje = gestion.reservar_turno(
                    datos, paciente_id, profesional_id, fecha, hora
                )
                if ok:
                    persistencia.guardar_datos(datos, RUTA_LOCAL)
                print(mensaje)
        elif opcion == "4":
            turno_id = pedir_numero("Número de turno: ")
            if turno_id is None:
                print("El número de turno tiene que ser entero.")
            else:
                ok, mensaje = gestion.cancelar_turno(datos, turno_id)
                if ok:
                    persistencia.guardar_datos(datos, RUTA_LOCAL)
                print(mensaje)
        elif opcion == "5":
            profesional_id = pedir_numero("Número de profesional: ")
            fecha = input("Fecha (AAAA-MM-DD): ").strip()
            if profesional_id is None:
                print("El número de profesional tiene que ser entero.")
            else:
                ok, resultado = gestion.agenda_profesional(datos, profesional_id, fecha)
                if not ok:
                    print(resultado)
                else:
                    for franja in resultado:
                        if franja["turno"] is None:
                            print(f"{franja['hora']}  libre")
                        else:
                            print(
                                f"{franja['hora']}  turno {franja['turno']['turno_id']}"
                                f" - {franja['turno']['paciente']}"
                            )
        elif opcion == "6":
            paciente_id = pedir_numero("Número de paciente: ")
            if paciente_id is None:
                print("El número de paciente tiene que ser entero.")
            else:
                ok, resultado = gestion.historial_paciente(datos, paciente_id)
                if not ok:
                    print(resultado)
                elif not resultado:
                    print("El paciente no tiene turnos.")
                else:
                    for turno in resultado:
                        print(
                            f"Turno {turno['id']}: {turno['fecha']} {turno['hora']} "
                            f"con {turno['profesional']} - {turno['estado']}"
                        )
        elif opcion == "0":
            print("Hasta luego.")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
