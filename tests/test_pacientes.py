"""Pruebas de caracterización para la gestión de pacientes."""

import copy
import unittest

from hospital.gestion import listar_pacientes, registrar_paciente


class TestPacientes(unittest.TestCase):
    """Pruebas unitarias para el registro y listado de pacientes."""

    def setUp(self):
        """Inicializa la estructura de datos para cada prueba."""
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

    def test_registrar_paciente_con_espacios_y_nombres_duplicados(self):
        """Registra pacientes recortando espacios y permite nombres duplicados."""
        exito_1, _ = registrar_paciente(self.datos, "  Marta  ")
        self.assertTrue(exito_1)
        self.assertEqual(len(self.datos["pacientes"]), 3)
        self.assertEqual(self.datos["pacientes"][-1], {"id": 3, "nombre": "Marta"})
        self.assertEqual(self.datos["proximo_paciente"], 4)

        exito_2, _ = registrar_paciente(self.datos, "  Marta  ")
        self.assertTrue(exito_2)
        self.assertEqual(len(self.datos["pacientes"]), 4)
        self.assertEqual(self.datos["pacientes"][-1], {"id": 4, "nombre": "Marta"})
        self.assertEqual(self.datos["proximo_paciente"], 5)

    def test_registrar_paciente_rechaza_nombres_vacios_o_espacios(self):
        """Rechaza altas con cadenas vacías o solo espacios sin alterar datos."""
        for nombre_invalido in ["", "   "]:
            with self.subTest(nombre=nombre_invalido):
                datos_previos = copy.deepcopy(self.datos)
                exito, _ = registrar_paciente(self.datos, nombre_invalido)
                self.assertFalse(exito)
                self.assertEqual(self.datos, datos_previos)
                self.assertEqual(
                    self.datos["proximo_paciente"],
                    datos_previos["proximo_paciente"],
                )

    def test_listar_pacientes_orden_numerico_y_no_muta_original(self):
        """Devuelve pacientes ordenados por ID sin alterar el orden original."""
        self.datos["pacientes"] = [
            {"id": 4, "nombre": "Zulema"},
            {"id": 1, "nombre": "Ana"},
            {"id": 3, "nombre": "Marta"},
            {"id": 2, "nombre": "Luis"},
        ]
        orden_original = copy.deepcopy(self.datos["pacientes"])

        resultado = listar_pacientes(self.datos)

        self.assertEqual([p["id"] for p in resultado], [1, 2, 3, 4])
        self.assertEqual(
            resultado,
            [
                {"id": 1, "nombre": "Ana"},
                {"id": 2, "nombre": "Luis"},
                {"id": 3, "nombre": "Marta"},
                {"id": 4, "nombre": "Zulema"},
            ],
        )
        self.assertEqual(self.datos["pacientes"], orden_original)
        self.assertIsNot(resultado, self.datos["pacientes"])


if __name__ == "__main__":
    unittest.main()
