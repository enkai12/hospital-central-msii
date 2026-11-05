"""Pruebas de caracterización para la gestión de turnos."""

import copy
import unittest

from hospital.gestion import (
    ACTIVO,
    CANCELADO,
    FRANJAS,
    agenda_profesional,
    cancelar_turno,
    historial_paciente,
    reservar_turno,
)


class TestTurnos(unittest.TestCase):
    """Pruebas para reserva, cancelación, agenda e historial de turnos."""

    def setUp(self):
        """Inicializa un estado de datos limpio antes de cada prueba."""
        self.datos = {
            "pacientes": [
                {"id": 1, "nombre": "Ana"},
                {"id": 2, "nombre": "Luis"},
            ],
            "profesionales": [
                {"id": 1, "nombre": "Dra. Pérez"},
                {"id": 2, "nombre": "Dr. Díaz"},
            ],
            "turnos": [],
            "proximo_paciente": 3,
            "proximo_turno": 1,
        }

    def test_reserva_valida_crea_turno_y_avanza_contador(self):
        """Una reserva válida crea el registro ACTIVO y avanza proximo_turno."""
        exito, _ = reservar_turno(self.datos, 1, 1, "2026-11-10", "09:00")
        self.assertTrue(exito)
        self.assertEqual(self.datos["proximo_turno"], 2)
        self.assertEqual(len(self.datos["turnos"]), 1)

        turno_esperado = {
            "id": 1,
            "paciente_id": 1,
            "profesional_id": 1,
            "fecha": "2026-11-10",
            "hora": "09:00",
            "estado": ACTIVO,
        }
        self.assertEqual(self.datos["turnos"][0], turno_esperado)

    def test_reserva_valida_en_todas_las_franjas(self):
        """Cada una de las franjas horarias válidas permite reservar con éxito."""
        for franja in FRANJAS:
            with self.subTest(franja=franja):
                datos = copy.deepcopy(self.datos)
                exito, _ = reservar_turno(datos, 1, 1, "2026-11-10", franja)
                self.assertTrue(exito)
                self.assertEqual(datos["proximo_turno"], 2)
                self.assertEqual(len(datos["turnos"]), 1)
                self.assertEqual(datos["turnos"][0]["hora"], franja)
                self.assertEqual(datos["turnos"][0]["estado"], ACTIVO)

    def test_rechazo_entradas_invalidas_no_muta_datos(self):
        """Casos inválidos devuelven False y preservan los datos intactos."""
        casos = [
            ("paciente inexistente", (999, 1, "2026-11-10", "09:00")),
            ("profesional inexistente", (1, 999, "2026-11-10", "09:00")),
            ("fecha no bisiesta o inexistente", (1, 1, "2026-02-30", "09:00")),
            ("fecha con formato incorrecto DD/MM/AAAA", (1, 1, "10/11/2026", "09:00")),
            ("fecha con ceros faltantes AAAA-M-DD", (1, 1, "2026-1-02", "09:00")),
            ("horario fuera de rango inferior", (1, 1, "2026-11-10", "08:30")),
            ("horario intermedio no contemplado", (1, 1, "2026-11-10", "09:15")),
            ("horario fuera de rango superior", (1, 1, "2026-11-10", "12:00")),
        ]
        for descripcion, (paciente_id, prof_id, fecha, hora) in casos:
            with self.subTest(caso=descripcion):
                datos_esperados = copy.deepcopy(self.datos)
                exito, _ = reservar_turno(self.datos, paciente_id, prof_id, fecha, hora)
                self.assertFalse(exito)
                self.assertEqual(self.datos, datos_esperados)

    def test_conflictos_y_concurrencia_de_franjas(self):
        """Superposiciones se rechazan sin mutar; combinaciones libres se permiten."""
        exito_inicial, _ = reservar_turno(self.datos, 1, 1, "2026-11-10", "09:00")
        self.assertTrue(exito_inicial)
        estado_con_un_turno = copy.deepcopy(self.datos)

        # Mismo profesional ocupado en misma fecha y hora
        exito_prof_ocupado, _ = reservar_turno(self.datos, 2, 1, "2026-11-10", "09:00")
        self.assertFalse(exito_prof_ocupado)
        self.assertEqual(self.datos, estado_con_un_turno)

        # Mismo paciente ocupado en misma fecha y hora
        exito_pac_ocupado, _ = reservar_turno(self.datos, 1, 2, "2026-11-10", "09:00")
        self.assertFalse(exito_pac_ocupado)
        self.assertEqual(self.datos, estado_con_un_turno)

        # Mismo profesional con otro paciente en otra franja: permitido
        exito_otra_franja, _ = reservar_turno(self.datos, 2, 1, "2026-11-10", "09:30")
        self.assertTrue(exito_otra_franja)

        # Mismo profesional con otro paciente en la misma franja de otra fecha:
        # permitido
        exito_otra_fecha, _ = reservar_turno(self.datos, 2, 1, "2026-11-11", "09:00")
        self.assertTrue(exito_otra_fecha)

        # Otro profesional con otro paciente en la franja original: permitido
        exito_otro_prof_y_pac, _ = reservar_turno(
            self.datos, 2, 2, "2026-11-10", "09:00"
        )
        self.assertTrue(exito_otro_prof_y_pac)

    def test_cancelacion_libera_franja_y_conserva_historial(self):
        """Cancelar actualiza a CANCELADO y permite reservar de nuevo esa franja."""
        reservar_turno(self.datos, 1, 1, "2026-11-10", "09:00")

        exito_cancel, _ = cancelar_turno(self.datos, 1)
        self.assertTrue(exito_cancel)
        self.assertEqual(len(self.datos["turnos"]), 1)
        self.assertEqual(self.datos["turnos"][0]["estado"], CANCELADO)

        # La misma combinación se puede reservar de nuevo tras la cancelación
        exito_nueva_reserva, _ = reservar_turno(self.datos, 1, 1, "2026-11-10", "09:00")
        self.assertTrue(exito_nueva_reserva)
        self.assertEqual(len(self.datos["turnos"]), 2)
        self.assertEqual(self.datos["turnos"][0]["id"], 1)
        self.assertEqual(self.datos["turnos"][0]["estado"], CANCELADO)
        self.assertEqual(self.datos["turnos"][1]["id"], 2)
        self.assertEqual(self.datos["turnos"][1]["estado"], ACTIVO)

    def test_cancelacion_invalida_no_muta_datos(self):
        """Cancelar un turno inexistente o ya cancelado falla sin alterar datos."""
        reservar_turno(self.datos, 1, 1, "2026-11-10", "09:00")
        cancelar_turno(self.datos, 1)
        estado_esperado = copy.deepcopy(self.datos)

        # Cancelación de turno inexistente
        exito_inexistente, _ = cancelar_turno(self.datos, 999)
        self.assertFalse(exito_inexistente)
        self.assertEqual(self.datos, estado_esperado)

        # Cancelación repetida de turno cancelado
        exito_repetida, _ = cancelar_turno(self.datos, 1)
        self.assertFalse(exito_repetida)
        self.assertEqual(self.datos, estado_esperado)

    def test_agenda_profesional_estructura_ocupacion_y_cancelacion(self):
        """Agenda devuelve las 6 franjas ordenadas, refleja ocupación y cancelados."""
        # Insertar turnos desordenados, para otra fecha y para otro profesional
        reservar_turno(self.datos, 1, 1, "2026-11-10", "11:00")  # ID 1
        reservar_turno(self.datos, 2, 1, "2026-11-10", "09:30")  # ID 2
        reservar_turno(self.datos, 1, 2, "2026-11-10", "09:00")  # ID 3 (otro prof)
        reservar_turno(self.datos, 2, 1, "2026-11-11", "10:00")  # ID 4 (otra fecha)

        exito, agenda = agenda_profesional(self.datos, 1, "2026-11-10")
        self.assertTrue(exito)
        self.assertEqual(len(agenda), 6)
        self.assertEqual([slot["hora"] for slot in agenda], FRANJAS)

        ocupacion_esperada = {
            "09:00": None,
            "09:30": {"turno_id": 2, "paciente": "Luis"},
            "10:00": None,
            "10:30": None,
            "11:00": {"turno_id": 1, "paciente": "Ana"},
            "11:30": None,
        }
        for slot in agenda:
            hora = slot["hora"]
            self.assertEqual(slot["turno"], ocupacion_esperada[hora])

        # Tras cancelar el turno 2, la franja 09:30 vuelve a libre (None)
        cancelar_turno(self.datos, 2)
        _, agenda_actualizada = agenda_profesional(self.datos, 1, "2026-11-10")
        franja_0930 = next(s for s in agenda_actualizada if s["hora"] == "09:30")
        self.assertIsNone(franja_0930["turno"])

    def test_agenda_profesional_invalida_no_muta_datos(self):
        """Consultar agenda con profesional inexistente o fecha inválida no muta."""
        datos_esperados = copy.deepcopy(self.datos)

        exito_prof, _ = agenda_profesional(self.datos, 999, "2026-11-10")
        self.assertFalse(exito_prof)
        self.assertEqual(self.datos, datos_esperados)

        exito_fecha, _ = agenda_profesional(self.datos, 1, "2026-02-30")
        self.assertFalse(exito_fecha)
        self.assertEqual(self.datos, datos_esperados)

    def test_historial_paciente_filtro_y_ordenamiento(self):
        """Historial filtra por paciente, incluye cancelados y ordena
        cronológicamente.
        """
        # Reservar fuera de orden cronológico para paciente 1 y otro para paciente 2
        reservar_turno(self.datos, 1, 1, "2026-11-12", "09:00")  # ID 1
        reservar_turno(self.datos, 1, 2, "2026-11-10", "11:00")  # ID 2
        reservar_turno(self.datos, 2, 1, "2026-11-10", "09:00")  # ID 3 (paciente 2)
        reservar_turno(self.datos, 1, 1, "2026-11-10", "09:30")  # ID 4

        # Cancelar turno 2 para verificar que se incluye en el historial
        cancelar_turno(self.datos, 2)

        exito, historial = historial_paciente(self.datos, 1)
        self.assertTrue(exito)
        self.assertEqual(len(historial), 3)

        # Solo turnos del paciente 1 con nombre del profesional
        for item in historial:
            self.assertEqual(item["paciente_id"], 1)
            self.assertIn("profesional", item)

        self.assertEqual(historial[0]["id"], 4)
        self.assertEqual(historial[0]["fecha"], "2026-11-10")
        self.assertEqual(historial[0]["hora"], "09:30")
        self.assertEqual(historial[0]["profesional"], "Dra. Pérez")
        self.assertEqual(historial[0]["estado"], ACTIVO)

        self.assertEqual(historial[1]["id"], 2)
        self.assertEqual(historial[1]["fecha"], "2026-11-10")
        self.assertEqual(historial[1]["hora"], "11:00")
        self.assertEqual(historial[1]["profesional"], "Dr. Díaz")
        self.assertEqual(historial[1]["estado"], CANCELADO)

        self.assertEqual(historial[2]["id"], 1)
        self.assertEqual(historial[2]["fecha"], "2026-11-12")
        self.assertEqual(historial[2]["hora"], "09:00")
        self.assertEqual(historial[2]["profesional"], "Dra. Pérez")
        self.assertEqual(historial[2]["estado"], ACTIVO)

    def test_historial_paciente_desempate_por_id(self):
        """Ante misma fecha y hora, el historial desempata por ID ascendentemente."""
        reservar_turno(self.datos, 1, 1, "2026-11-15", "09:00")  # ID 1
        cancelar_turno(self.datos, 1)
        reservar_turno(self.datos, 1, 1, "2026-11-15", "09:00")  # ID 2

        # Invertir el orden físico en turnos para comprobar que el orden final no
        # depende del orden de inserción sino del criterio (fecha, hora, id)
        self.datos["turnos"].reverse()

        exito, historial = historial_paciente(self.datos, 1)
        self.assertTrue(exito)
        self.assertEqual(len(historial), 2)
        self.assertEqual([t["id"] for t in historial], [1, 2])

    def test_historial_paciente_invalido_no_muta_datos(self):
        """Consultar historial con paciente inexistente devuelve False y no muta."""
        datos_esperados = copy.deepcopy(self.datos)
        exito, _ = historial_paciente(self.datos, 999)
        self.assertFalse(exito)
        self.assertEqual(self.datos, datos_esperados)


if __name__ == "__main__":
    unittest.main()
