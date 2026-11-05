# ADR 002: Persistencia en archivo JSON local, manejo de errores y alcance de concurrencia

- **Estado:** Aceptado
- **Fecha:** Noviembre de 2026
- **Referencia:** `estado-inicial` (commit `e5d6927`)

## Contexto
El sistema base debe persistir los cambios realizados durante la sesión (altas de pacientes, reservas y cancelaciones de turnos) para que se mantengan al cerrar y volver a abrir el programa, partiendo de un conjunto conocido de datos de prueba con personas ficticias. Además, debe definirse cómo responde el sistema ante operaciones rechazadas por reglas de negocio o ante un archivo de datos dañado.

## Alternativas consideradas
1. **Motor de base de datos relacional (PostgreSQL / MySQL) o embebido (SQLite):** Ofrece transacciones ACID y control de concurrencia, pero añade configuración de esquemas SQL que excede la simplicidad buscada en el prototipo inicial.
2. **Almacenamiento en memoria volátil:** Simplifica el código pero impide verificar la persistencia real entre ejecuciones sucesivas del programa.
3. **Archivo JSON local (`datos/local.json`) inicializado desde una plantilla versionada (`datos/ejemplo.json`):** Utiliza el módulo nativo `json` de Python, permite inspeccionar el estado a simple vista y separa los datos de prueba versionados del archivo de trabajo local.

## Decisión
Implementamos la persistencia mediante archivos JSON con las siguientes reglas en el sistema base:
- **Separación semilla vs. trabajo:** El repositorio incluye `datos/ejemplo.json` (con 4 profesionales precargados y 2 pacientes ficticios). Si al iniciar no existe `datos/local.json`, se crea automáticamente copiando `datos/ejemplo.json`. El archivo `datos/local.json` se ignora en Git.
- **Protección ante archivo dañado:** Si `datos/local.json` contiene JSON inválido, el programa captura el error al iniciar, informa al usuario por consola y finaliza sin sobrescribir el archivo para no destruir información recuperable.
- **Inmutabilidad ante rechazos:** `guardar_datos()` solo se invoca cuando la operación de negocio finaliza con éxito (`ok == True`); cualquier operación rechazada deja intacto el estado persistido.
- **Supuesto de concurrencia:** Se asume ejecución monousuario en un único proceso de consola de recepción; el control de concurrencia multiusuario queda fuera del alcance del prototipo.

## Consecuencias
- **Positivas:** Fácil reinicio del entorno de pruebas para repetir la demo (basta con borrar `datos/local.json`); trazabilidad inmediata del estado guardado; cumplimiento estricto de los criterios de aceptación de persistencia.
- **Negativas / Deuda técnica identificada:** En `estado-inicial`, las funciones `cargar_datos` y `guardar_datos` quedaron mezcladas junto con las reglas de negocio en `hospital/gestion.py` (hallazgo H3), la validación al cargar no verifica la estructura interna si el JSON es sintácticamente válido pero de otro tipo (hallazgo H4), y el guardado sobrescribe el archivo directamente sin paso temporal atómico (hallazgo H9). Estos puntos quedan registrados para su resolución en las etapas siguientes.
