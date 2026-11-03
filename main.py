from hospital import gestion

MENU = """
Hospital Central - Agenda de turnos
1. Registrar paciente
2. Listar pacientes
0. Salir"""


def main():
    datos = gestion.datos_vacios()

    while True:
        print(MENU)
        opcion = input("Opción: ").strip()

        if opcion == "1":
            nombre = input("Nombre del paciente: ")
            _, mensaje = gestion.registrar_paciente(datos, nombre)
            print(mensaje)
        elif opcion == "2":
            pacientes = gestion.listar_pacientes(datos)
            if not pacientes:
                print("No hay pacientes registrados.")
            for paciente in pacientes:
                print(f"{paciente['id']}. {paciente['nombre']}")
        elif opcion == "0":
            print("Hasta luego.")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
