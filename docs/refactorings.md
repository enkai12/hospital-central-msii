# Registro Técnico de Refactorings

Este documento constituye el registro técnico formal de los refactorings aplicados sobre la agenda de turnos del Hospital Central, tomando como línea de base el diagnóstico de deuda técnica y *code smells* consolidado en [`docs/diagnostico.md`](diagnostico.md) sobre la versión inicial (`estado-inicial`, commit `e5d6927`).

El propósito de estas transformaciones es elevar la calidad interna de la base de código (reduciendo duplicación, desacoplando responsabilidades y aumentando la cohesión y mantenibilidad) preservando de manera estricta el comportamiento observable y las doce reglas operativas de negocio.

> **Alcance de esta entrega (Bloque 1):**  
> Esta primera revisión documenta en detalle los refactorings **H2** (búsqueda centralizada por identificador) y **H1 / H5** (descomposición del menú interactivo y extracción de validaciones de reserva), ambos integrados en `main` mediante sus correspondientes Pull Requests revisados por pares. Las transformaciones restantes (H3 y H6) y las correcciones complementarias de persistencia (H9) se integrarán en una entrega posterior.

---

## Ficha Técnica 1: H2 — Centralización de búsquedas por identificador (*Extract Method*)

### Trazabilidad y metadatos
- **ID de diagnóstico asociado:** [H2 — Búsqueda por número duplicada (*Duplicated Code*)](diagnostico.md#h2--búsqueda-por-número-duplicada-duplicated-code)
- **Técnica de refactoring:** *Extract Method* (Fowler)
- **Issue en GitHub:** [#15 — Refactoring H2: Unificar bucles de búsqueda por ID](https://github.com/enkai12/hospital-central-msii/issues/15)
- **Pull Request:** [#20 — Busco pacientes, profesionales y turnos con una sola función](https://github.com/enkai12/hospital-central-msii/pull/20)
- **Rama de trabajo:** `refactor/15-busqueda-unica`
- **Commit funcional inicial:** [`e3f1d168e9df51c46d2cf29bce0aff452b56dd19`](https://github.com/enkai12/hospital-central-msii/commit/e3f1d168e9df51c46d2cf29bce0aff452b56dd19)
- **Commit de merge en `main`:** [`fc147dcdd0c9a6e6e5bd2d87fedb2de17c3e3a13`](https://github.com/enkai12/hospital-central-msii/commit/fc147dcdd0c9a6e6e5bd2d87fedb2de17c3e3a13)

### Problema original y *code smell*
En la versión inicial (`e5d6927`), el módulo `hospital/gestion.py` repetía exactamente el mismo patrón algorítmico de búsqueda secuencial en siete ubicaciones distintas (líneas 41, 48, 91, 105, 128, 137 y 146):
- Tres búsquedas sobre `datos["pacientes"]` (en `reservar_turno`, `agenda_profesional` e `historial_paciente`).
- Tres búsquedas sobre `datos["profesionales"]` (en `reservar_turno`, `agenda_profesional` e `historial_paciente`).
- Una búsqueda sobre `datos["turnos"]` (en `cancelar_turno`).

Dicho patrón consistía en inicializar una variable auxiliar en `None`, iterar mediante un bucle `for` sobre la colección y comparar `item["id"] == id_buscado`. Además de la duplicación manifiesta (*Duplicated Code*), el bucle carecía de sentencia de corte temprano (`break` o `return`), obligando a recorrer la totalidad de la lista incluso tras haber hallado la entidad buscada.

### Transformación aplicada
Se extrajo la función auxiliar pura `buscar_por_id(elementos, id_buscado)` al inicio de `hospital/gestion.py`, dotándola de retorno inmediato (*early return*):

```python
def buscar_por_id(elementos, id_buscado):
    for elemento in elementos:
        if elemento["id"] == id_buscado:
            return elemento
    return None
```

A continuación, se reemplazaron de manera homogénea los siete bloques de bucles manuales por invocaciones directas a `buscar_por_id`:
1. `reservar_turno`: obtención y validación de existencia de `paciente`.
2. `reservar_turno`: obtención y validación de existencia de `profesional`.
3. `cancelar_turno`: localización de la entidad en `datos["turnos"]`.
4. `agenda_profesional`: verificación de existencia de `profesional`.
5. `agenda_profesional`: resolución de nombre del paciente asignado a cada franja horaria ocupada.
6. `historial_paciente`: verificación de existencia de `paciente`.
7. `historial_paciente`: resolución del nombre del profesional vinculado a cada turno del historial.

### Fragmentos de código antes y después

#### Antes (`e3f1d16^:hospital/gestion.py`)
Fragmento ilustrativo en la función `reservar_turno`:
```python
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
```

#### Después (`fc147dc:hospital/gestion.py`)
Definición del método extraído y su consumo en `reservar_turno`:
```python
def buscar_por_id(elementos, id_buscado):
    for elemento in elementos:
        if elemento["id"] == id_buscado:
            return elemento
    return None
```
```python
    paciente = buscar_por_id(datos["pacientes"], paciente_id)
    if paciente is None:
        return False, "No existe un paciente con ese número."

    profesional = buscar_por_id(datos["profesionales"], profesional_id)
    if profesional is None:
        return False, "No existe un profesional con ese número."
```

### Justificación arquitectónica y de diseño
1. **Principio DRY (*Don't Repeat Yourself*):** Se eliminó la dispersión del algoritmo de localización de entidades por clave primaria. Si en el futuro cambiara la representación de las colecciones (por ejemplo, a indexación asociativa por diccionario o mapeo O(1)), la modificación queda confinada a un único punto de cambio.
2. **Eficiencia y claridad de intención:** La incorporación del retorno temprano (*early exit*) interrumpe la iteración en el instante en que se satisface la condición, reduciendo complejidad cognitiva y evitando operaciones de comparación innecesarias sobre el resto de la lista.
3. **Mantenibilidad:** El balance neto del cambio en `hospital/gestion.py` fue de +21 líneas agregadas y -26 eliminadas, con una simplificación sustancial de la legibilidad en las funciones que orquestan las reglas de turnos.

### Límites de equivalencia
- **Semántica de retorno:** `buscar_por_id` retorna la **primera** coincidencia que cumpla `elemento["id"] == id_buscado` o `None` en caso de no hallarla.
- **Invariante de unicidad:** En el código previo sin sentencia de corte, si una lista hubiera contenido elementos con identificadores duplicados, la variable auxiliar habría terminado almacenando la **última** coincidencia tras recorrer la lista entera. La equivalencia estricta de comportamiento se fundamenta en la **Regla 1 del sistema** (generación secuencial e irrepetible de identificadores), la cual garantiza que los identificadores de pacientes, profesionales y turnos son invariablemente únicos en el almacén de datos.
- **Tipado dinámico tolerante:** La comparación `elemento["id"] == id_buscado` se apoya en igualdad por valor (`==`). La llamada asume que ambos operandos son numéricos enteros conforme a los contratos establecidos en la capa de interfaz.

### Evidencia histórica y estado de verificación
- **Contexto histórico de validación (PR #20):** Al momento de la integración del PR #20 en `main`, el repositorio no contaba con una suite de pruebas automatizadas configurada (cobertura automatizada 0%).
- **Evidencia reportada en la época:** La verificación fue ejecutada manualmente por el equipo mediante:
  1. Ejecución completa del guión interactivo de demostración de 7 pasos (`python main.py`), corroborando la persistencia y la consistencia de cada mensaje de salida.
  2. Batería manual de 16 casos de borde por consola (cancelación de turnos inexistentes o cancelados, números fuera de rango, consultas sin coincidencias).
- **Cobertura automatizada posterior:** La equivalencia formal fue ratificada con posterioridad mediante la suite automatizada introducida en el PR #22 ([`tests/test_turnos.py`](../tests/test_turnos.py)), donde las funciones `reservar_turno`, `cancelar_turno`, `agenda_profesional` e `historial_paciente` son evaluadas exhaustivamente frente a casos válidos y de error.

---

## Ficha Técnica 2: H1 / H5 — Descomposición del menú interactivo y validaciones de reserva (*Extract Method*)

### Trazabilidad y metadatos
- **IDs de diagnóstico asociados:**  
  - [H1 — Funciones largas (*Long Method*)](diagnostico.md#h1--funciones-largas-long-method)  
  - [H5 — Validación de fecha duplicada (*Duplicated Code*)](diagnostico.md#h5--validación-de-fecha-duplicada-duplicated-code)
- **Técnica de refactoring:** *Extract Method* (Fowler)
- **Issue en GitHub:** [#17 — Refactorings H1 y H5: Funciones largas y validaciones duplicadas](https://github.com/enkai12/hospital-central-msii/issues/17)
- **Pull Request:** [#23 — refactor: extraer funciones del menu y controles de reserva (H1, H5)](https://github.com/enkai12/hospital-central-msii/pull/23)
- **Rama de trabajo:** `refactor/17-funciones-cortas`
- **Commit funcional inicial:** [`4f707c61dcd600986a3457d800c878ff34bc9cf6`](https://github.com/enkai12/hospital-central-msii/commit/4f707c61dcd600986a3457d800c878ff34bc9cf6)
- **Commit de merge en `main`:** [`a10ba35e75b9fce235ac91ea0834caceac6ac1e1`](https://github.com/enkai12/hospital-central-msii/commit/a10ba35e75b9fce235ac91ea0834caceac6ac1e1)

### Problema original y *code smells*
1. **H1 — Función interactiva monolítica (`main.py`):**  
   La función `main()` extendía su cuerpo a lo largo de 91 líneas (líneas 27–117 en `e5d6927`), concentrando toda la lógica de control del programa mediante una extensa cascada `if/elif`. Cada rama asumía la captura de datos por consola (`input`), conversión de tipos, invocación a las funciones de negocio en `hospital/gestion.py`, decisión de persistencia en disco e impresión de resultados formateados.
2. **H1 — Lógica de control extensa en reserva (`hospital/gestion.py`):**  
   La función `reservar_turno()` acumulaba 48 líneas de código estructuradas en seis comprobaciones consecutivas fuertemente acopladas antes de concretar la reserva.
3. **H5 — Lógica de validación de fecha duplicada (`hospital/gestion.py`):**  
   Tanto `reservar_turno()` (líneas 54–59) como `agenda_profesional()` (líneas 111–116) repetían idéntico bloque de seis líneas con `datetime.strptime(fecha, "%Y-%m-%d")` y su posterior recomprobación con `strftime`, duplicando cuatro veces el literal de error `"La fecha no es válida. Usá el formato AAAA-MM-DD."`.

### Transformación aplicada

#### 1. Descomposición de la interfaz de consola (`main.py`)
Se extrajeron funciones manejadoras especializadas para cada una de las opciones del menú:
- `opcion_registrar_paciente(datos)`
- `opcion_listar_pacientes(datos)`
- `opcion_reservar_turno(datos)`
- `opcion_cancelar_turno(datos)`
- `opcion_consultar_agenda(datos)`
- `opcion_consultar_historial(datos)`

La estructura monolítica de control por `if/elif` fue reemplazada por una tabla de despacho (*dispatch dictionary*) basada en el mapeo `OPCIONES`:

```python
OPCIONES = {
    "1": opcion_registrar_paciente,
    "2": opcion_listar_pacientes,
    "3": opcion_reservar_turno,
    "4": opcion_cancelar_turno,
    "5": opcion_consultar_agenda,
    "6": opcion_consultar_historial,
}
```

La función `main()` quedó reducida a orquestar el bucle de presentación del menú, despachando la acción seleccionada mediante `accion = OPCIONES.get(opcion)`.

#### 2. Centralización de validaciones de dominio (`hospital/gestion.py`)
Se extrajeron componentes dedicados para desacoplar la orquestación de la reserva:
- **Constante representativa:** `MENSAJE_FECHA_INVALIDA = "La fecha no es válida. Usá el formato AAAA-MM-DD."`.
- **`validar_fecha(fecha)`:** Encapsula el bloque `try/except` con `strptime` y la confirmación estricta de formato, reutilizada en `reservar_turno` y `agenda_profesional`.
- **`validar_horario(hora)`:** Encapsula la pertenencia de la cadena horaria a la lista admisible de `FRANJAS`.
- **`buscar_conflicto(turnos, paciente_id, profesional_id, fecha, hora)`:** Centraliza la verificación de superposición de turnos activos para la fecha y franja solicitadas.

#### Evolución durante Code Review (commit `c33d459`)
En el commit funcional inicial (`4f707c6`), la propuesta original descomponía la búsqueda de conflictos en dos funciones separadas: `profesional_ocupado()` y `paciente_ocupado()`.  
Durante la revisión del Pull Request #23, se identificó que evaluar ambas condiciones en dos pasadas independientes sobre la lista de turnos podía romper la estricta precedencia histórica de mensajes ante escenarios con múltiples conflictos en distintos turnos. Para preservar la semántica original exacta, el commit `c33d459` unificó ambas comprobaciones en la función `buscar_conflicto`, realizando una única pasada sobre `turnos` y respetando el orden secuencial de evaluación: primero el conflicto del profesional y luego el del paciente.

### Fragmentos de código antes y después

#### `hospital/gestion.py` — Validaciones de reserva

##### Antes (`a10ba35e^1:hospital/gestion.py`)
```python
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
```

##### Después (`a10ba35e:hospital/gestion.py`)
Métodos auxiliares extraídos:
```python
def validar_fecha(fecha):
    try:
        fecha_valida = datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        return False
    return fecha_valida.strftime("%Y-%m-%d") == fecha


def validar_horario(hora):
    return hora in FRANJAS


def buscar_conflicto(turnos, paciente_id, profesional_id, fecha, hora):
    for turno in turnos:
        if turno["estado"] == ACTIVO and turno["fecha"] == fecha:
            if turno["hora"] == hora and turno["profesional_id"] == profesional_id:
                return "El profesional ya tiene un turno en esa fecha y horario."
            if turno["hora"] == hora and turno["paciente_id"] == paciente_id:
                return "El paciente ya tiene un turno en esa fecha y horario."
    return None
```
Invocación sintetizada en `reservar_turno`:
```python
    if not validar_fecha(fecha):
        return False, MENSAJE_FECHA_INVALIDA

    if not validar_horario(hora):
        return False, "El horario tiene que ser una de las franjas: " + ", ".join(
            FRANJAS
        )

    conflicto = buscar_conflicto(
        datos["turnos"], paciente_id, profesional_id, fecha, hora
    )
    if conflicto is not None:
        return False, conflicto
```

#### `main.py` — Descomposición del menú

##### Antes (`a10ba35e^1:main.py`)
Fragmento de la opción 3 dentro del `main()` monolítico:
```python
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
```

##### Después (`a10ba35e:main.py`)
Manejador extraído `opcion_reservar_turno` y despacho en bucle `main()`:
```python
def opcion_reservar_turno(datos):
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
        return
    ok, mensaje = gestion.reservar_turno(
        datos, paciente_id, profesional_id, fecha, hora
    )
    if ok:
        persistencia.guardar_datos(datos, RUTA_LOCAL)
    print(mensaje)
```
```python
        if opcion == "0":
            print("Hasta luego.")
            break
        accion = OPCIONES.get(opcion)
        if accion is None:
            print("Opción inválida.")
        else:
            accion(datos)
```

### Justificación arquitectónica y de diseño
1. **Principio de Responsabilidad Única (SRP):** `main()` deja de actuar como orquestador masivo de entrada/salida y lógica de flujo, acotándose a coordinar el ciclo de vida de la sesión interactiva. Cada manejador `opcion_*` asume exclusivamente la interacción de su caso de uso.
2. **Abierto para extensión, cerrado para modificación (OCP):** La incorporación de una nueva opción en la consola (por ejemplo, reportes o estadísticas) ya no requiere alterar la lógica interna de `main()`; basta con implementar un nuevo manejador y agregarlo al diccionario `OPCIONES`.
3. **Cohesión y testeabilidad:** Al aislar `validar_fecha`, `validar_horario` y `buscar_conflicto`, las reglas de consistencia de turnos quedan disponibles para verificación unitaria aislada sin necesidad de orquestar estructuras completas de datos ni simular flujos de consola.

### Límites de equivalencia
- **Orden estricto de validaciones:** En `reservar_turno`, se preserva rigurosamente el orden de fallo:
  1. Existencia del paciente.
  2. Existencia del profesional.
  3. Formato y validez de la fecha (`validar_fecha`).
  4. Pertenencia del horario a las franjas autorizadas (`validar_horario`).
  5. Ausencia de colisión de turnos (`buscar_conflicto`).
- **Precedencia en conflictos de agenda:** Si para un mismo turno activo coinciden simultáneamente el paciente y el profesional, `buscar_conflicto` reporta en primer término `"El profesional ya tiene un turno en esa fecha y horario."`, replicando con exactitud la precedencia del bucle original. Asimismo, la iteración en una sola pasada garantiza que ante turnos con conflictos disjuntos, el orden de aparición en la lista `datos["turnos"]` determina qué rechazo se produce primero.
- **Flujo de consola:** Las cadenas solicitadas en `input()`, el tratamiento de cadenas vacías o no enteras mediante `pedir_numero()`, y la salida por terminal permanecen completamente inalterados.

### Evidencia histórica y estado de verificación
- **Entorno de integración y CI (PR #23):** A diferencia de H2, el PR #23 fue desarrollado e integrado sobre una base de código que ya contaba con integración continua automatizada configurada en GitHub Actions (incorporada en el PR #22).
- **Evidencia reportada en ese momento:** Se ejecutó la suite de pruebas unitarias compuesta en ese estadío por **19 pruebas automatizadas** (`pytest`), cubriendo todas las reglas de negocio de `hospital/gestion.py`, junto con la validación de estilo y análisis estático mediante `flake8` y `black` (commit de formateo `0baf95f`).
- **Comprobación de no-regresión:** Todos los casos de prueba superaron la verificación de forma transparente en CI, confirmando la equivalencia del comportamiento refactorizado.
