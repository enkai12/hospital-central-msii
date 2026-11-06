"""Pruebas de caracterización para la persistencia e integración del sistema."""

import json
from pathlib import Path
import tempfile
import unittest

from hospital.gestion import (
    ACTIVO,
    SolicitudTurno,
    agenda_profesional,
    historial_paciente,
    registrar_paciente,
    reservar_turno,
)
from hospital.persistencia import cargar_datos, guardar_datos


class TestPersistencia(unittest.TestCase):
    """Pruebas para carga, guardado e integración de reservas en disco."""

    def setUp(self):
        """Inicializa directorio temporal, rutas y fixture en memoria."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.ruta_datos = Path(self.temp_dir.name) / "local.json"
        self.ruta_ejemplo = Path(self.temp_dir.name) / "ejemplo.json"
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

    def test_guardar_y_recargar_conserva_datos(self):
        """Guardar y recargar conserva la totalidad de los datos y caracteres."""
        ejemplo_vacio = {
            "pacientes": [],
            "profesionales": [],
            "turnos": [],
            "proximo_paciente": 1,
            "proximo_turno": 1,
        }
        self.ruta_ejemplo.write_text(
            json.dumps(ejemplo_vacio, ensure_ascii=False),
            encoding="utf-8",
        )

        exito, _ = registrar_paciente(self.datos, "  María  ")
        self.assertTrue(exito)

        guardar_datos(self.datos, self.ruta_datos)
        datos_recargados = cargar_datos(self.ruta_datos, self.ruta_ejemplo)

        self.assertEqual(datos_recargados, self.datos)
        self.assertIn({"id": 3, "nombre": "María"}, datos_recargados["pacientes"])
        self.assertEqual(datos_recargados["proximo_paciente"], 4)
        self.assertEqual(
            datos_recargados["profesionales"],
            [{"id": 1, "nombre": "Dra. Pérez"}, {"id": 2, "nombre": "Dr. Díaz"}],
        )
        self.assertEqual(datos_recargados["proximo_turno"], 1)

        datos_en_disco = json.loads(self.ruta_datos.read_text(encoding="utf-8"))
        self.assertEqual(datos_en_disco, self.datos)

    def test_cargar_crea_destino_desde_ejemplo(self):
        """Cargar crea el archivo destino a partir del ejemplo si no existe."""
        self.ruta_ejemplo.write_text(
            json.dumps(self.datos, ensure_ascii=False),
            encoding="utf-8",
        )
        bytes_ejemplo = self.ruta_ejemplo.read_bytes()

        self.assertFalse(self.ruta_datos.exists())
        datos_cargados = cargar_datos(self.ruta_datos, self.ruta_ejemplo)

        self.assertEqual(datos_cargados, self.datos)
        self.assertTrue(self.ruta_datos.exists())
        datos_destino = json.loads(self.ruta_datos.read_text(encoding="utf-8"))
        self.assertEqual(datos_destino, self.datos)
        self.assertEqual(self.ruta_ejemplo.read_bytes(), bytes_ejemplo)

    def test_cargar_json_invalido_no_reemplaza_destino(self):
        """Cargar un archivo con JSON inválido propaga error y preserva archivos."""
        ejemplo_valido = {
            "pacientes": [],
            "profesionales": [],
            "turnos": [],
            "proximo_paciente": 1,
            "proximo_turno": 1,
        }
        self.ruta_ejemplo.write_text(
            json.dumps(ejemplo_valido, ensure_ascii=False),
            encoding="utf-8",
        )
        bytes_ejemplo = self.ruta_ejemplo.read_bytes()

        self.ruta_datos.write_text('{"pacientes":', encoding="utf-8")
        bytes_datos = self.ruta_datos.read_bytes()

        with self.assertRaises(json.JSONDecodeError):
            cargar_datos(self.ruta_datos, self.ruta_ejemplo)

        self.assertEqual(self.ruta_datos.read_bytes(), bytes_datos)
        self.assertEqual(self.ruta_ejemplo.read_bytes(), bytes_ejemplo)

    def test_guardar_con_error_no_modifica_destino(self):
        """Si el guardado falla, el archivo anterior queda igual y sin temporales."""
        guardar_datos(self.datos, self.ruta_datos)
        bytes_datos = self.ruta_datos.read_bytes()

        datos_invalidos = dict(self.datos, turnos=[object()])
        with self.assertRaises(TypeError):
            guardar_datos(datos_invalidos, self.ruta_datos)

        self.assertEqual(self.ruta_datos.read_bytes(), bytes_datos)
        self.assertEqual(
            sorted(p.name for p in Path(self.temp_dir.name).iterdir()),
            ["local.json"],
        )

    def test_reserva_persistida_aparece_en_agenda_e_historial(self):
        """Una reserva guardada y recargada se refleja en agenda e historial."""
        ejemplo_valido = {
            "pacientes": [],
            "profesionales": [],
            "turnos": [],
            "proximo_paciente": 1,
            "proximo_turno": 1,
        }
        self.ruta_ejemplo.write_text(
            json.dumps(ejemplo_valido, ensure_ascii=False),
            encoding="utf-8",
        )

        solicitud = SolicitudTurno(
            paciente_id=1, profesional_id=1, fecha="2026-11-10", hora="09:00"
        )
        exito_reserva, _ = reservar_turno(self.datos, solicitud)
        self.assertTrue(exito_reserva)

        guardar_datos(self.datos, self.ruta_datos)
        datos_recargados = cargar_datos(self.ruta_datos, self.ruta_ejemplo)

        datos_en_disco = json.loads(self.ruta_datos.read_text(encoding="utf-8"))
        self.assertEqual(datos_en_disco, self.datos)
        self.assertEqual(datos_recargados, self.datos)

        self.assertEqual(datos_recargados["proximo_turno"], 2)
        turno_esperado = {
            "id": 1,
            "paciente_id": 1,
            "profesional_id": 1,
            "fecha": "2026-11-10",
            "hora": "09:00",
            "estado": ACTIVO,
        }
        self.assertEqual(datos_recargados["turnos"], [turno_esperado])

        exito_agenda, agenda = agenda_profesional(datos_recargados, 1, "2026-11-10")
        self.assertTrue(exito_agenda)

        exito_historial, historial = historial_paciente(datos_recargados, 1)
        self.assertTrue(exito_historial)

        agenda_esperada = [
            {"hora": "09:00", "turno": {"turno_id": 1, "paciente": "Ana"}},
            {"hora": "09:30", "turno": None},
            {"hora": "10:00", "turno": None},
            {"hora": "10:30", "turno": None},
            {"hora": "11:00", "turno": None},
            {"hora": "11:30", "turno": None},
        ]
        self.assertEqual(agenda, agenda_esperada)

        historial_esperado = [{**turno_esperado, "profesional": "Dra. Pérez"}]
        self.assertEqual(historial, historial_esperado)
