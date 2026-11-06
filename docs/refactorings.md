# Registro Técnico de Refactorings

Este documento constituye el registro técnico formal de los cuatro refactorings principales y la corrección complementaria de persistencia integrados en la agenda de turnos del Hospital Central, tomando como línea de base el diagnóstico de deuda técnica y *code smells* consolidado en [`docs/diagnostico.md`](diagnostico.md) sobre la versión inicial (`estado-inicial`, commit `e5d6927`).

El propósito de los cuatro refactorings es mejorar la calidad interna del código (reducir duplicación, separar responsabilidades y aumentar la cohesión) conservando el comportamiento observable bajo las precondiciones indicadas en cada ficha. H9 se distingue porque corrige un comportamiento observable ante fallos de guardado.

> **Alcance de este documento:**  
> Se documentan los cuatro refactorings acordados (**H2**, **H1 / H5**, **H3** y **H6**) y la corrección complementaria de persistencia (**H9**), integrados en `main` mediante sus Pull Requests. H2 y H3 tuvieron verificación manual reportada; la suite con `unittest` y la integración continua se incorporaron después, en el PR #22. Las cantidades de pruebas y los resultados citados son reportes históricos, no ejecuciones realizadas para esta actualización documental.

---

## Ficha Técnica 1: H2 - Centralización de búsquedas por identificador (*Extract Method*)

### Trazabilidad y metadatos
- **ID de diagnóstico asociado:** [H2 - Búsqueda por número duplicada (*Duplicated Code*)](diagnostico.md#h2--búsqueda-por-número-duplicada-duplicated-code)
- **Técnica de refactoring:** *Extract Method* (Fowler)
- **Issue en GitHub:** [#15 - Refactoring H2: Unificar bucles de búsqueda por ID](https://github.com/enkai12/hospital-central-msii/issues/15)
- **Pull Request:** [#20 - Busco pacientes, profesionales y turnos con una sola función](https://github.com/enkai12/hospital-central-msii/pull/20)
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
1. **Principio DRY (*Don't Repeat Yourself*):** Se centralizó el algoritmo de búsqueda por identificador. Los consumidores siguen trabajando con listas; una futura migración a colecciones indexadas requeriría revisar tanto su representación como los consumidores, no solo cambiar este helper.
2. **Eficiencia y claridad de intención:** La incorporación del retorno temprano (*early exit*) interrumpe la iteración en el instante en que se satisface la condición, reduciendo complejidad cognitiva y evitando operaciones de comparación innecesarias sobre el resto de la lista.
3. **Mantenibilidad:** Las funciones de reserva, cancelación, agenda e historial expresan la intención de buscar una entidad mediante el mismo helper, sin repetir el recorrido.

### Límites de equivalencia
- **Semántica de retorno:** `buscar_por_id` retorna la **primera** coincidencia que cumpla `elemento["id"] == id_buscado` o `None` en caso de no hallarla.
- **Precondición de unicidad:** El bucle previo sin corte retenía la **última** coincidencia; el helper retorna la primera. Ambos seleccionan la misma entidad si los IDs son únicos dentro de cada colección, como se espera de datos válidos. La Regla 1 describe la generación de IDs de pacientes y turnos, no de profesionales. Esa generación no garantiza unicidad ante ediciones arbitrarias del JSON o contadores inconsistentes; la unicidad de profesionales también es una precondición de los datos, no una validación añadida por H2.
- **Comparación sin validación de tipos:** Se conserva `elemento["id"] == id_buscado`; el helper no valida que los operandos sean enteros ni corrige registros inválidos.

### Evidencia histórica y estado de verificación
- **Contexto histórico de validación (PR #20):** En su integración todavía no se había incorporado la suite automatizada del PR #22. Esto no equivale a una medición de cobertura del 0%.
- **Evidencia registrada en el PR:** Se reportaron verificaciones manuales mediante:
  1. El guion interactivo de demostración de 7 pasos (`python main.py`).
  2. Una batería de 16 casos de borde por consola.
- **Pruebas automatizadas posteriores:** El PR #22 incorporó pruebas con `unittest` en [`tests/test_turnos.py`](../tests/test_turnos.py) para reservas, cancelaciones, agenda e historial. Los casos de caracterización aportan evidencia de no regresión en los escenarios comprobados, no una demostración formal ni cobertura exhaustiva.

---

## Ficha Técnica 2: H1 / H5 - Descomposición del menú interactivo y validaciones de reserva (*Extract Method*)

### Trazabilidad y metadatos
- **IDs de diagnóstico asociados:**  
  - [H1 - Funciones largas (*Long Method*)](diagnostico.md#h1--funciones-largas-long-method)  
  - [H5 - Validación de fecha duplicada (*Duplicated Code*)](diagnostico.md#h5--validación-de-fecha-duplicada-duplicated-code)
- **Técnica de refactoring:** *Extract Method* (Fowler)
- **Issue en GitHub:** [#17 - Refactorings H1 y H5: Funciones largas y validaciones duplicadas](https://github.com/enkai12/hospital-central-msii/issues/17)
- **Pull Request:** [#23 - refactor: extraer funciones del menu y controles de reserva (H1, H5)](https://github.com/enkai12/hospital-central-msii/pull/23)
- **Rama de trabajo:** `refactor/17-funciones-cortas`
- **Commit funcional inicial:** [`4f707c61dcd600986a3457d800c878ff34bc9cf6`](https://github.com/enkai12/hospital-central-msii/commit/4f707c61dcd600986a3457d800c878ff34bc9cf6)
- **Commit de merge en `main`:** [`a10ba35e75b9fce235ac91ea0834caceac6ac1e1`](https://github.com/enkai12/hospital-central-msii/commit/a10ba35e75b9fce235ac91ea0834caceac6ac1e1)

### Problema original y *code smells*
1. **H1 - Función interactiva monolítica (`main.py`):**  
   La función `main()` extendía su cuerpo a lo largo de 91 líneas (líneas 27–117 en `e5d6927`), concentrando toda la lógica de control del programa mediante una extensa cascada `if/elif`. Cada rama asumía la captura de datos por consola (`input`), conversión de tipos, invocación a las funciones de negocio en `hospital/gestion.py`, decisión de persistencia en disco e impresión de resultados formateados.
2. **H1 - Lógica de control extensa en reserva (`hospital/gestion.py`):**  
   La función `reservar_turno()` acumulaba 48 líneas de código estructuradas en seis comprobaciones consecutivas fuertemente acopladas antes de concretar la reserva.
3. **H5 - Lógica de validación de fecha duplicada (`hospital/gestion.py`):**  
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
Durante la revisión del Pull Request #23 se identificó que dos pasadas independientes podían cambiar el mensaje ante conflictos en distintos turnos. El commit `c33d459` reunió las comprobaciones en `buscar_conflicto`: recorre la lista en su orden y, dentro de **cada turno** activo de la fecha solicitada, comprueba primero al profesional y luego al paciente. No establece una prioridad global del profesional sobre todos los turnos.

### Fragmentos de código antes y después

#### `hospital/gestion.py` - Validaciones de reserva

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

#### `main.py` - Descomposición del menú

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
2. **Aproximación parcial al principio abierto/cerrado (OCP):** Una opción adicional puede reutilizar el despacho de `main()` mediante un nuevo manejador, pero exige actualizar tanto `OPCIONES` como el texto de `MENU`. Se reduce la modificación del bucle, no se alcanza un cumplimiento absoluto del principio.
3. **Cohesión y pruebas:** La extracción permite comprobar `validar_fecha`, `validar_horario` y `buscar_conflicto` de forma más focalizada. Las reglas ya podían probarse antes; el cambio reduce el tamaño de las unidades bajo prueba.

### Límites de equivalencia
- **Orden estricto de validaciones:** En `reservar_turno`, se preserva rigurosamente el orden de fallo:
  1. Existencia del paciente.
  2. Existencia del profesional.
  3. Formato y validez de la fecha (`validar_fecha`).
  4. Pertenencia del horario a las franjas autorizadas (`validar_horario`).
  5. Ausencia de colisión de turnos (`buscar_conflicto`).
- **Precedencia en conflictos de agenda:** Dentro de cada turno activo de la fecha solicitada se comprueba primero al profesional y luego al paciente. Si ambos conflictos corresponden al mismo turno, se informa el del profesional. Si corresponden a turnos distintos, prevalece el primer conflicto encontrado según el orden de `datos["turnos"]`, aunque sea el del paciente.
- **Flujo de consola:** La extracción conserva las solicitudes de entrada, el tratamiento de números mediante `pedir_numero()` y los mensajes del flujo mostrado.

### Evidencia histórica y estado de verificación
- **Entorno de integración y CI (PR #23):** A diferencia de H2, el PR #23 fue desarrollado e integrado sobre una base de código que ya contaba con integración continua automatizada configurada en GitHub Actions (incorporada en el PR #22).
- **Evidencia registrada en el PR:** El PR #23 reporta **19 pruebas automatizadas** con `unittest`, junto con controles de estilo mediante `flake8` y `black` (commit de formateo `0baf95f`).
- **Alcance de esa evidencia:** Los resultados reportados respaldan la conservación del comportamiento en los casos probados; no demuestran equivalencia formal ni ausencia de regresiones en cualquier entrada.

---

## Ficha Técnica 3: H3 - Reubicación de responsabilidades de persistencia y desacoplamiento (*Extract Module* / *Move Method*)

### Trazabilidad y metadatos
- **ID de diagnóstico asociado:** [H3 - Reglas y archivo en el mismo módulo (*Large Class* y baja cohesión)](diagnostico.md#h3--reglas-y-archivo-en-el-mismo-módulo-large-class-y-baja-cohesión)
- **Técnica de refactoring:** *Extract Module* / *Move Method* (Fowler)
- **Issue en GitHub:** [#18 - Refactoring H3: Separar la persistencia JSON de las reglas de gestión](https://github.com/enkai12/hospital-central-msii/issues/18)
- **Pull Request:** [#21 - Paso la carga y el guardado del JSON a un módulo de persistencia](https://github.com/enkai12/hospital-central-msii/pull/21)
- **Rama de trabajo:** `refactor/18-persistencia`
- **Commit funcional inicial:** [`21a5e2c366eb13cd880c61c216c3bdd77037a533`](https://github.com/enkai12/hospital-central-msii/commit/21a5e2c366eb13cd880c61c216c3bdd77037a533)
- **Commit de merge en `main`:** [`e873b855c77b66b690fc0478bd212f3bd5de9d1e`](https://github.com/enkai12/hospital-central-msii/commit/e873b855c77b66b690fc0478bd212f3bd5de9d1e)

### Problema original y *code smell*
En el sistema base (`e5d6927`), el módulo `hospital/gestion.py` asumía simultáneamente dos responsabilidades de distinta naturaleza arquitectónica:
1. Las reglas de dominio médico de la agenda de turnos (altas de pacientes, validación de turnos, cancelaciones y consultas).
2. Los detalles de infraestructura física y persistencia en disco: importación de `json` y `shutil`, apertura de archivos con codificación UTF-8, carga con `json.load()` y serialización directa con `json.dump()`.

El diagnóstico clasifica históricamente este problema como *Large Class* / baja cohesión por analogía con la literatura orientada a objetos; aquí se trata de un módulo procedimental, no de una clase existente. La mezcla reúne dos motivos de cambio en `hospital/gestion.py`. Las reglas ya operaban sobre diccionarios y listas en memoria, sin necesitar leer o escribir archivos en cada llamada; el problema era la convivencia de responsabilidades en el mismo módulo, no una dependencia de ejecución inseparable.

> **Aclaración crucial de alcance:** Este refactoring consistió exclusivamente en la extracción modular y el desacoplamiento de dependencias. **No introdujo atomicidad ni guardado temporal en disco**; esas mejoras de robustez frente a fallos corresponden a una etapa posterior (ver sección complementaria H9).

### Transformación aplicada
1. **Creación del módulo especializado:** Se creó `hospital/persistencia.py` trasladando de forma íntegra las funciones `cargar_datos(ruta, ruta_ejemplo)` y `guardar_datos(datos, ruta)`.
2. **Separación en `hospital/gestion.py`:** Se eliminaron las importaciones de `json` y `shutil` y las funciones de archivo. Las reglas conservaron su operación sobre diccionarios y listas en memoria, incluida la mutación de esas estructuras.
3. **Migración de consumidores (`main.py`):** Se adaptaron las importaciones (`from hospital import gestion, persistencia`) y se reencaminaron las llamadas de lectura y escritura:
   - Al inicio: `persistencia.cargar_datos(RUTA_LOCAL, RUTA_EJEMPLO)`.
   - En cada operación exitosa: `persistencia.guardar_datos(datos, RUTA_LOCAL)`.

### Fragmentos de código antes y después

#### Antes (`21a5e2c^:hospital/gestion.py`)
Funciones de infraestructura ubicadas dentro de `hospital/gestion.py`:
```python
def cargar_datos(ruta, ruta_ejemplo):
    if not ruta.exists():
        shutil.copyfile(ruta_ejemplo, ruta)
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_datos(datos, ruta):
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
```

#### Después (`e873b85:hospital/persistencia.py`)
Módulo independiente de persistencia `hospital/persistencia.py`:
```python
def cargar_datos(ruta, ruta_ejemplo):
    if not ruta.exists():
        shutil.copyfile(ruta_ejemplo, ruta)
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_datos(datos, ruta):
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
```

#### Migración de llamadas en `main.py`
Antes (`21a5e2c^:main.py`):
```python
def main():
    try:
        datos = gestion.cargar_datos(RUTA_LOCAL, RUTA_EJEMPLO)
    except ValueError:
        print("No se pudo leer datos/local.json: el archivo está dañado.")
        print("Revisalo o borralo para empezar de nuevo con los datos de ejemplo.")
        return
```
Después (`e873b85:main.py`):
```python
def main():
    try:
        datos = persistencia.cargar_datos(RUTA_LOCAL, RUTA_EJEMPLO)
    except ValueError:
        print("No se pudo leer datos/local.json: el archivo está dañado.")
        print("Revisalo o borralo para empezar de nuevo con los datos de ejemplo.")
        return
```

### Justificación arquitectónica y de diseño
1. **Principio de Responsabilidad Única (SRP):** La extracción separa los motivos de cambio de las reglas de turnos y de las operaciones de archivo en módulos distintos.
2. **Organización de pruebas:** Las reglas ya podían probarse en memoria antes de H3. La separación distingue las pruebas de dominio de las que necesitan archivos temporales, sin crear por primera vez esa posibilidad.
3. **Evolución de persistencia:** Los detalles de lectura y escritura quedan localizados en `hospital/persistencia.py`. Sustituir JSON requeriría revisar el contrato de datos y la integración con los consumidores; H3 no elimina toda dependencia de representación ni garantiza una migración sin otros cambios.

### Límites de equivalencia
- **Formato y codificación en disco:** La estructura del JSON resultante (`ensure_ascii=False, indent=2`) y el mecanismo de fallback mediante `shutil.copyfile` desde la ruta de ejemplo permanecieron estrictamente idénticos al estado base.
- **Manejo de errores inicial:** En esta etapa, `guardar_datos` conservó la escritura directa con truncamiento inmediato de archivo (`with open(ruta, "w")`), manteniendo idéntica vulnerabilidad a fallos abruptos que el código original.

### Evidencia histórica y estado de verificación
- **Contexto histórico (PR #21):** Se integró después de H2 (#20) y antes de la suite automatizada del PR #22. La ausencia de esa suite no es una medición porcentual de cobertura.
- **Evidencia registrada en el PR:** Se reportó verificación manual de la demostración y de casos de borde, incluidos los flujos de carga y guardado.
- **Pruebas automatizadas posteriores:** El PR #22 incorporó pruebas con `unittest` en [`tests/test_persistencia.py`](../tests/test_persistencia.py) sobre carga, escritura y uso integrado de los datos. Son casos concretos de caracterización, no una comprobación exhaustiva de la persistencia.

---

## Ficha Técnica 4: H6 - Agrupación de parámetros de reserva en objeto de solicitud (*Introduce Parameter Object*)

### Trazabilidad y metadatos
- **ID de diagnóstico asociado:** [H6 - Demasiados parámetros en la reserva (*Long Parameter List*)](diagnostico.md#h6--demasiados-parámetros-en-la-reserva-long-parameter-list)
- **Técnica de refactoring:** *Introduce Parameter Object* (Fowler)
- **Issue en GitHub:** [#19 - Refactoring H6: Agrupar datos de reserva en un objeto de dominio](https://github.com/enkai12/hospital-central-msii/issues/19)
- **Pull Request:** [#26 - Agrupar los datos de la reserva en un objeto de solicitud (H6)](https://github.com/enkai12/hospital-central-msii/pull/26)
- **Rama de trabajo:** `refactor/19-objeto-solicitud-turno`
- **Commit funcional inicial:** [`8879924aa988b444fdeb07a52ee21f5d7c47acd7`](https://github.com/enkai12/hospital-central-msii/commit/8879924aa988b444fdeb07a52ee21f5d7c47acd7)
- **Commit de merge en `main`:** [`465cc5e28fc7cd0de1f86763c7488f9a7a4fe337`](https://github.com/enkai12/hospital-central-msii/commit/465cc5e28fc7cd0de1f86763c7488f9a7a4fe337)

### Problema original y *code smell*
La función central de reservas en `hospital/gestion.py` exponía la siguiente firma:
```python
def reservar_turno(datos, paciente_id, profesional_id, fecha, hora):
```
Esta signatura presentaba los *code smells* de **Lista larga de parámetros** (*Long Parameter List*) y **Grupo de datos acoplados** (*Data Clumps*):
- Los cuatro parámetros de la reserva (`paciente_id: int`, `profesional_id: int`, `fecha: str`, `hora: str`) viajaban siempre agrupados desde la captura de consola en `main.py` hacia las distintas funciones de control.
- Riesgo de orden posicional: Dos IDs enteros y dos cadenas contiguas facilitan intercambios accidentales al invocar la función. La firma previa no expresa nombres de campos en una llamada posicional ni valida los tipos en ejecución.

### Transformación aplicada
1. **Definición de la dataclass con campos congelados:**  
   Se incorporó en `hospital/gestion.py` la estructura:
   ```python
   @dataclass(frozen=True)
   class SolicitudTurno:
       paciente_id: int
       profesional_id: int
       fecha: str
       hora: str
   ```
2. **Reestructuración de la firma de reserva:**  
   Se actualizó la firma a `reservar_turno(datos, solicitud: SolicitudTurno)`.
3. **Propagación en helpers internos:**  
   La función de detección de solapamientos se adaptó para recibir el objeto: `buscar_conflicto(turnos, solicitud: SolicitudTurno)`.
4. **Migración de consumidores:**  
   - En `main.py` (`opcion_reservar_turno`): se instancia `SolicitudTurno` a partir de los datos ingresados por consola antes de despachar a la regla de negocio.
   - En la suite de pruebas unitarias ([`tests/test_turnos.py`](../tests/test_turnos.py) y [`tests/test_persistencia.py`](../tests/test_persistencia.py)): todas las llamadas de prueba fueron migradas para instanciar `SolicitudTurno`.

### Fragmentos de código antes y después

#### `hospital/gestion.py` - Dataclass y firma de reserva

##### Antes (`8879924^:hospital/gestion.py`)
```python
def reservar_turno(datos, paciente_id, profesional_id, fecha, hora):
    paciente = buscar_por_id(datos["pacientes"], paciente_id)
    if paciente is None:
        return False, "No existe un paciente con ese número."

    profesional = buscar_por_id(datos["profesionales"], profesional_id)
    if profesional is None:
        return False, "No existe un profesional con ese número."

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

##### Después (`465cc5e:hospital/gestion.py`)
```python
@dataclass(frozen=True)
class SolicitudTurno:
    paciente_id: int
    profesional_id: int
    fecha: str
    hora: str
```
```python
def reservar_turno(datos, solicitud: SolicitudTurno):
    paciente = buscar_por_id(datos["pacientes"], solicitud.paciente_id)
    if paciente is None:
        return False, "No existe un paciente con ese número."

    profesional = buscar_por_id(datos["profesionales"], solicitud.profesional_id)
    if profesional is None:
        return False, "No existe un profesional con ese número."

    if not validar_fecha(solicitud.fecha):
        return False, MENSAJE_FECHA_INVALIDA

    if not validar_horario(solicitud.hora):
        return False, "El horario tiene que ser una de las franjas: " + ", ".join(
            FRANJAS
        )

    conflicto = buscar_conflicto(datos["turnos"], solicitud)
    if conflicto is not None:
        return False, conflicto
```

#### `main.py` - Llamada a la reserva

##### Antes (`8879924^:main.py`)
```python
    ok, mensaje = gestion.reservar_turno(
        datos, paciente_id, profesional_id, fecha, hora
    )
    if ok:
        persistencia.guardar_datos(datos, RUTA_LOCAL)
    print(mensaje)
```

##### Después (`465cc5e:main.py`)
```python
    solicitud = gestion.SolicitudTurno(
        paciente_id=paciente_id,
        profesional_id=profesional_id,
        fecha=fecha,
        hora=hora,
    )
    ok, mensaje = gestion.reservar_turno(datos, solicitud)
    if ok:
        persistencia.guardar_datos(datos, RUTA_LOCAL)
    print(mensaje)
```

### Justificación arquitectónica y de diseño
1. **Restricción de reasignación:** `frozen=True` impide la reasignación ordinaria de campos después de construir la solicitud. No es una garantía absoluta de inmutabilidad ni valida los tipos anotados en ejecución.
2. **Agrupación de datos y tipado explícito:** `SolicitudTurno` da nombre al conjunto de datos de una reserva. Las anotaciones documentan los campos; las validaciones de negocio permanecen en las funciones de gestión.
3. **Legibilidad en llamadas:** Las llamadas migradas construyen la solicitud con argumentos nombrados (`paciente_id=...`, `profesional_id=...`), lo que reduce el riesgo de transposición. La dataclass no exige ese estilo: también admite argumentos posicionales y no elimina universalmente el riesgo de asignar valores al campo equivocado.

### Límites de equivalencia
- **Esquema de persistencia conservado:** El turno confirmado sigue almacenándose como un diccionario con las claves `"id"`, `"paciente_id"`, `"profesional_id"`, `"fecha"`, `"hora"` y `"estado"`. La dataclass no se serializa como parte del JSON; este cambio no modifica su representación persistida ni valida archivos preexistentes.
- **Mensajes y reglas operativas:** El cambio de firma conserva las comprobaciones, su orden y los mensajes de reserva de la versión previa.

### Evidencia histórica y estado de verificación
- **CI disponible (PR #26):** El repositorio ya contaba con pruebas y controles en GitHub Actions desde el PR #22.
- **Evidencia registrada en el PR:** El PR #26 reporta la migración de las llamadas de prueba a `SolicitudTurno` y **20 pruebas automatizadas aprobadas** con `unittest`, además de controles con `flake8` y `black`. Son resultados históricos, no una ejecución nueva de esta documentación.

---

## Sección Complementaria: H9 - Corrección de Robustez en Persistencia Atómica

> **Diferenciación conceptual:**  
> Esta intervención no computa dentro de los cuatro refactorings solicitados por la cátedra. Un refactoring busca reestructurar el código interno sin cambiar su comportamiento observable bajo sus precondiciones. H9 es una **corrección de robustez / *defect fix***: cambia el resultado observable de un fallo durante la serialización al evitar que se trunque primero el destino.

### Trazabilidad y metadatos
- **ID de diagnóstico asociado:** [H9 - Escritura directa sobre el archivo](diagnostico.md#h9--escritura-directa-sobre-el-archivo)
- **Naturaleza del cambio:** Corrección de robustez física (*Atomic File Persistence*)
- **Issue en GitHub:** [#24 - Fix H9: Guardado seguro en archivo temporal para evitar pérdida de datos](https://github.com/enkai12/hospital-central-msii/issues/24)
- **Pull Request:** [#25 - Guardo los datos en un archivo temporal y reemplazo el original al terminar](https://github.com/enkai12/hospital-central-msii/pull/25)
- **Rama de trabajo:** `fix/24-guardado-seguro`
- **Commit funcional inicial:** [`1bbe682bf45267306a4e8d7253a14a694bf5f338`](https://github.com/enkai12/hospital-central-msii/commit/1bbe682bf45267306a4e8d7253a14a694bf5f338)
- **Commit de merge en `main`:** [`c6ce82bc4c28e17b77d11228a0beacec678a7abf`](https://github.com/enkai12/hospital-central-msii/commit/c6ce82bc4c28e17b77d11228a0beacec678a7abf)

### Problema original
Tanto en la versión base (`e5d6927`) como tras la extracción inicial de H3 en `hospital/persistencia.py`, la función `guardar_datos` ejecutaba:
```python
with open(ruta, "w", encoding="utf-8") as archivo:
    json.dump(datos, archivo, ensure_ascii=False, indent=2)
```
Abrir un archivo existente en modo `"w"` lo trunca antes de serializar. Si `json.dump()` falla, el destino puede quedar vacío o parcialmente escrito y perder su contenido anterior. La escritura directa también expone los datos a interrupciones del proceso; H9 reduce este riesgo, pero no garantiza recuperación ante cualquier fallo.

### Transformación aplicada
Se implementó escritura en temporal seguida de reemplazo:
1. **Archivo temporal:** Se construye la ruta alternativa `ruta_temporal = ruta.with_name(ruta.name + ".tmp")`.
2. **Escritura previa al reemplazo:** Se serializa el JSON en el temporal y se cierra el archivo antes de invocar `os.replace`.
3. **Reemplazo atómico:** Si `os.replace(ruta_temporal, ruta)` tiene éxito, el cambio del nombre destino es atómico: no expone como destino un estado intermedio de la serialización. Esta propiedad del reemplazo no implica durabilidad ante apagones; el código no ejecuta `fsync` ni coordina escrituras concurrentes sobre el temporal de nombre fijo.
4. **Limpieza y propagación:** Ante una excepción que alcance `except BaseException`, se intenta borrar el temporal con `unlink(missing_ok=True)`. Si esa limpieza termina sin error, `raise` propaga la excepción original. Si `unlink` falla, su excepción pasa a ser la propagada, con la anterior como contexto. No hay limpieza garantizada: `SIGKILL` o un corte de energía no ejecutan ese bloque.
5. **Configuración de repositorio:** Se añadió `datos/local.json.tmp` al archivo `.gitignore`.

### Fragmentos de código antes y después

#### Antes (`1bbe682^:hospital/persistencia.py`)
```python
def guardar_datos(datos, ruta):
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
```

#### Después (`c6ce82b:hospital/persistencia.py`)
```python
def guardar_datos(datos, ruta):
    ruta_temporal = ruta.with_name(ruta.name + ".tmp")
    try:
        with open(ruta_temporal, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
        os.replace(ruta_temporal, ruta)
    except BaseException:
        ruta_temporal.unlink(missing_ok=True)
        raise
```

### Evidencia histórica de verificación
En el PR #25 se incorporó `test_guardar_con_error_no_modifica_destino` en [`tests/test_persistencia.py`](../tests/test_persistencia.py). El test introduce un objeto no serializable y comprueba, en ese escenario:
1. Que se propaga `TypeError`.
2. Que el destino conserva sus bytes originales.
3. Que no queda el temporal en el directorio de la prueba.

El PR reporta **20 pruebas automatizadas** con `unittest`. Ese caso no comprueba fallos de limpieza, interrupciones no capturables, durabilidad ante apagones ni escrituras concurrentes; no se ejecutaron pruebas nuevas para este documento.

---

## Síntesis de Refactorings, Trazabilidad Histórica y Cronología Metodológica

### Tabla consolidada de intervenciones

| ID | Técnica / Naturaleza | Alcance Principal | Issue | Pull Request | Commit Funcional | Commit Merge (`main`) | Verificación registrada en el PR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **H2** | *Extract Method* | Centralización de búsquedas por ID en `buscar_por_id` | [#15](https://github.com/enkai12/hospital-central-msii/issues/15) | [#20](https://github.com/enkai12/hospital-central-msii/pull/20) | [`e3f1d16`](https://github.com/enkai12/hospital-central-msii/commit/e3f1d168e9df51c46d2cf29bce0aff452b56dd19) | [`fc147dc`](https://github.com/enkai12/hospital-central-msii/commit/fc147dcdd0c9a6e6e5bd2d87fedb2de17c3e3a13) | Manual: 7 pasos demo y 16 casos de borde |
| **H3** | *Extract Module* / *Move Method* | Desacoplamiento de persistencia en `hospital/persistencia.py` | [#18](https://github.com/enkai12/hospital-central-msii/issues/18) | [#21](https://github.com/enkai12/hospital-central-msii/pull/21) | [`21a5e2c`](https://github.com/enkai12/hospital-central-msii/commit/21a5e2c366eb13cd880c61c216c3bdd77037a533) | [`e873b85`](https://github.com/enkai12/hospital-central-msii/commit/e873b855c77b66b690fc0478bd212f3bd5de9d1e) | Manual reportada: demo y casos de borde |
| **H1 / H5** | *Extract Method* | Modularización de consola (`main.py`) y validaciones en `gestion.py` | [#17](https://github.com/enkai12/hospital-central-msii/issues/17) | [#23](https://github.com/enkai12/hospital-central-msii/pull/23) | [`4f707c6`](https://github.com/enkai12/hospital-central-msii/commit/4f707c61dcd600986a3457d800c878ff34bc9cf6) | [`a10ba35`](https://github.com/enkai12/hospital-central-msii/commit/a10ba35e75b9fce235ac91ea0834caceac6ac1e1) | Reporte: 19 pruebas con `unittest`; controles `flake8` y `black` |
| **H9** | *Fix / Robustness* *(Complementario)* | Escritura en `.tmp` y reemplazo atómico exitoso con `os.replace` | [#24](https://github.com/enkai12/hospital-central-msii/issues/24) | [#25](https://github.com/enkai12/hospital-central-msii/pull/25) | [`1bbe682`](https://github.com/enkai12/hospital-central-msii/commit/1bbe682bf45267306a4e8d7253a14a694bf5f338) | [`c6ce82b`](https://github.com/enkai12/hospital-central-msii/commit/c6ce82bc4c28e17b77d11228a0beacec678a7abf) | Reporte: 20 pruebas con `unittest`, incluida la de error de serialización |
| **H6** | *Introduce Parameter Object* | Agrupación de datos de reserva en `SolicitudTurno` con campos congelados | [#19](https://github.com/enkai12/hospital-central-msii/issues/19) | [#26](https://github.com/enkai12/hospital-central-msii/pull/26) | [`8879924`](https://github.com/enkai12/hospital-central-msii/commit/8879924aa988b444fdeb07a52ee21f5d7c47acd7) | [`465cc5e`](https://github.com/enkai12/hospital-central-msii/commit/465cc5e28fc7cd0de1f86763c7488f9a7a4fe337) | Reporte: 20 pruebas con `unittest`, con llamadas migradas a `SolicitudTurno` |

### Cronología y metodología en la verificación
El proceso de refactoring atravesó un desarrollo paulatino en su estrategia de aseguramiento de calidad:
1. **Verificación inicial (H2 y H3, PRs #20 y #21):** Antes de incorporar la suite automatizada se reportaron verificaciones manuales de demostración y casos de borde. La ausencia de suite no permite asignar un porcentaje medido de cobertura.
2. **Incorporación de automatización (PR #22):** Se añadieron pruebas de caracterización unitarias y de integración en `tests/` con `unittest` y CI en GitHub Actions, junto con controles `flake8` y `black`.
3. **Cambios posteriores (H1/H5, H9 y H6, PRs #23, #25 y #26):** Sus reportes históricos indican 19 pruebas en #23 y 20 en #25 y #26. Esa evidencia corresponde a los escenarios probados; no demuestra ausencia universal de regresiones ni equivalencia formal de las doce reglas operativas. No son ejecuciones realizadas para esta actualización documental.

