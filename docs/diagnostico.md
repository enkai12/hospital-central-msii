# Diagnóstico del Sistema Base (`estado-inicial`)

Este documento registra la evaluación de calidad externa e interna (Etapa 2) y el catálogo de deuda técnica y *code smells* (Etapa 3) realizados sobre la versión inicial de la agenda de turnos del Hospital Central.

---

## 1. Calidad externa vs. calidad interna

### Mirada del usuario final (Calidad externa)
Desde la mirada de quien usa el sistema, la versión inicial funciona bien. El personal de recepción puede operar el menú interactivo por consola para registrar pacientes, listar pacientes, reservar y cancelar turnos, y consultar la agenda de un profesional o el historial de un paciente.

Se cumplen las **12 reglas operativas** definidas en el sistema base:
1. Generación automática e irrepetible de identificadores de paciente y de turno.
2. Validación de nombre de paciente no vacío y recorte de espacios en los extremos (`strip`), permitiendo homónimos con distinto ID.
3. Verificación de existencia previa del paciente y del profesional antes de reservar.
4. Validación estricta de fechas reales bajo el formato `AAAA-MM-DD`.
5. Turnos de duración fija (30 minutos) restringidos a las seis franjas horarias (`09:00`, `09:30`, `10:00`, `10:30`, `11:00` y `11:30`).
6. Rechazo de superposición de turnos activos para el mismo profesional en igual fecha y franja.
7. Rechazo de superposición de turnos activos para el mismo paciente en igual fecha y franja, incluso con distintos profesionales.
8. Conservación del historial al cancelar: el turno pasa de `ACTIVO` a `CANCELADO` y libera la franja.
9. Rechazo seguro al intentar cancelar un turno inexistente o ya cancelado.
10. Atomicidad lógica ante rechazos: una operación rechazada no modifica los datos guardados.
11. Ordenamiento consistente de consultas por fecha, horario y número de turno.
12. Persistencia en `datos/local.json` inicializada desde `datos/ejemplo.json` y protección ante archivo dañado sin sobrescribirlo.

Recorrimos los 7 pasos de la demo completa y todos los resultados coincidieron con lo esperado.

### Mirada del equipo de desarrollo (Calidad interna)
La estructura interna, en cambio, presenta debilidades que no se ven desde la consola:
- **Métodos extensos y acoplamiento en la interfaz:** La función principal del menú (`main()`) tiene 91 líneas: pide los datos, los valida, muestra los resultados y decide cuándo guardar.
- **Duplicación de lógica:** La búsqueda secuencial de un paciente, un profesional o un turno por su número está escrita siete veces, y la validación de la fecha aparece duplicada en dos funciones.
- **Baja cohesión y mezcla de responsabilidades:** El mismo módulo (`hospital/gestion.py`) contiene las reglas de negocio de los turnos y la lectura/escritura del archivo JSON.
- **Manejo frágil de errores:** Las funciones informan los errores devolviendo `False` y un mensaje en una tupla polimórfica, en lugar de lanzar una excepción, obligando a que cada opción del menú revise el resultado antes de seguir.
- **Ausencia de pruebas automatizadas:** La verificación depende exclusivamente de pruebas manuales por consola (0% de cobertura automatizada en el estado inicial).

### Cuadro comparativo sobre `estado-inicial`

| Aspecto | Qué vemos | Cómo afecta |
| :--- | :--- | :--- |
| **Funcionalidad visible** | Las cinco operaciones principales, el listado de pacientes y las 12 reglas se cumplen. | El sistema es útil tal como está para el usuario final. |
| **Legibilidad** | La función del menú es larga (91 líneas) y los bucles de búsqueda usan nombres como `p` y `t`. | Cuesta seguir el flujo de ejecución y ubicar dónde se decide cada cosa. |
| **Mantenibilidad** | La misma búsqueda por ID (7 veces) y la misma validación de fecha (2 veces) están copiadas en varias funciones. | Una corrección hay que hacerla en todos los lugares, y es fácil olvidarse de uno. |
| **Evolución futura** | Las reglas dependen directamente del archivo JSON y cada opción nueva se agrega dentro de la misma función `main()`. | Cambiar la forma de guardar o sumar una operación obliga a tocar código que ya funciona y no cuenta con pruebas automatizadas. |

Estos problemas no rompen nada hoy, pero hacen que cada cambio cueste más y tenga más riesgo. Por eso el trabajo no apunta a agregar funciones, sino a mejorar la estructura interna conservando exactamente el mismo comportamiento visible.

---

## 2. Diagnóstico de deuda técnica y code smells

### Fuentes de diagnóstico empleadas
Revisamos el código de la versión inicial (`estado-inicial`, commit `e5d6927`) combinando tres fuentes complementarias:
1. **Lectura e inspección manual del código:** Revisión estructural de `main.py` y `hospital/gestion.py` evaluando cohesión, acoplamiento, responsabilidades (SOLID) y repetición de lógica.
2. **Ejecución de casos de borde:** Pruebas forzando entradas inesperadas (`EOFError` con `Ctrl+D`), JSON válido pero con estructura ajena (`[]` y `{}`), ausencia simultánea de archivos JSON e inconsistencias referenciales manuales.
3. **Análisis estático con SonarQube:** Ejecución del escáner sobre las 231 líneas de código del tag `estado-inicial` para medir complejidad cognitiva, duplicación de literales y deuda técnica estimada.

### Resumen del catálogo de hallazgos (H1 a H11)

| ID | Problema | Ubicación (`estado-inicial` - `e5d6927`) | Prioridad |
| :--- | :--- | :--- | :--- |
| **H1** | Funciones largas (*Long Method*) | `main.py`: `main()` (líneas 27–117); `hospital/gestion.py`: `reservar_turno` (líneas 39–86) | Alta |
| **H2** | Búsqueda por número duplicada (*Duplicated Code*) | `hospital/gestion.py`, líneas 41, 48, 91, 105, 128, 137 y 146 | Alta |
| **H3** | Reglas y archivo en el mismo módulo (*Large Class* y baja cohesión) | `hospital/gestion.py`: `cargar_datos` y `guardar_datos` (12–21) junto a las reglas (24–150) | Alta |
| **H4** | Errores sin controlar al cargar o leer | `main.py`, líneas 28–33 y 37; `hospital/gestion.py`, líneas 12–16 | Alta |
| **H5** | Validación de fecha duplicada (*Duplicated Code*) | `hospital/gestion.py`, líneas 54–59 y 111–116 | Media |
| **H6** | Demasiados parámetros en la reserva (*Long Parameter List*) | `hospital/gestion.py`, línea 39; `main.py`, líneas 57–66 | Media |
| **H7** | Errores informados con `False` | `hospital/gestion.py`: 14 `return False`; `main.py`: 5 controles de `ok` | Media |
| **H8** | La consola depende de la forma interna de los datos (acoplamiento) | `main.py`, líneas 52–56, 89–96 y 108–112 | Media |
| **H9** | Escritura directa sobre el archivo | `hospital/gestion.py`, líneas 19–21 | Media |
| **H10** | Datos del dominio como texto suelto (*Primitive Obsession*) | `hospital/gestion.py`, líneas 8–9 y 73–80 | Baja |
| **H11** | Agenda y reserva no coinciden con datos inconsistentes | `hospital/gestion.py`, líneas 121–131 | Baja |

---

### Detalle formal de los 11 hallazgos (8 campos)

#### H1 — Funciones largas (*Long Method*)
- **ID:** H1
- **Problema / Code Smell:** Funciones largas (*Long Method*) y alta complejidad cognitiva.
- **Ubicación exacta en `estado-inicial` (`e5d6927`):** `main.py`: `main()` (líneas 27–117); `hospital/gestion.py`: `reservar_turno()` (líneas 39–86).
- **Evidencia:** `main()` tiene 91 líneas y una rama `if/elif` por cada opción del menú. En cada rama pide los datos, los convierte, llama a la regla, decide si guardar y muestra el resultado. `reservar_turno()` tiene 48 líneas y hace seis controles seguidos.
- **Impacto:** Para entender una sola opción hay que leer toda la función, y los controles de la reserva no se pueden probar por separado.
- **Riesgo de mantenimiento:** Cada operación nueva se agrega dentro de la misma función y la hace más larga y propensa a regresiones.
- **Prioridad:** Alta.
- **Acción propuesta:** Extraer una función por opción del menú y una por control de la reserva (*Extract Method*).

#### H2 — Búsqueda por número duplicada (*Duplicated Code*)
- **ID:** H2
- **Problema / Code Smell:** Búsqueda por número duplicada (*Duplicated Code*).
- **Ubicación exacta en `estado-inicial` (`e5d6927`):** `hospital/gestion.py`, líneas 41, 48, 91, 105, 128, 137 y 146.
- **Evidencia:** El mismo bucle `for` que recorre una lista hasta encontrar un número (`id`) aparece siete veces: tres para pacientes, tres para profesionales y una para turnos. Además, el bucle no se corta (`break`/`return`) al encontrar el elemento.
- **Impacto:** Cualquier cambio en la forma de buscar, por ejemplo cortar el bucle o avisar si el número no existe, hay que repetirlo en siete lugares.
- **Riesgo de mantenimiento:** Alto; es fácil corregir uno y olvidarse de los demás.
- **Prioridad:** Alta.
- **Acción propuesta:** Extraer una sola función genérica de búsqueda por ID, reutilizada por todas las operaciones.

#### H3 — Reglas y archivo en el mismo módulo (*Large Class* y baja cohesión)
- **ID:** H3
- **Problema / Code Smell:** Reglas de negocio y persistencia en archivos en el mismo módulo (*Large Class*, baja cohesión, violación de SRP).
- **Ubicación exacta en `estado-inicial` (`e5d6927`):** `hospital/gestion.py`: `cargar_datos()` y `guardar_datos()` (líneas 12–21) junto a las reglas de negocio (líneas 24–150).
- **Evidencia:** `gestion.py` tiene las reglas de los turnos y también la lectura y escritura del JSON, importando `json` y `shutil`. Las reglas no pueden usarse sin ese formato de datos.
- **Impacto:** El módulo cambia por dos motivos distintos (si cambia una regla o si cambia la forma de guardar), y para probar una regla hay que conocer la estructura del archivo.
- **Riesgo de mantenimiento:** Cambiar el mecanismo de almacenamiento obliga a tocar el código de las reglas de negocio.
- **Prioridad:** Alta.
- **Acción propuesta:** Mover la carga y el guardado a un módulo de persistencia propio (*Move Method* / reubicación de responsabilidad).

#### H4 — Errores sin controlar al cargar o leer
- **ID:** H4
- **Problema / Code Smell:** Manejo incompleto de excepciones de entrada/salida y de estructura de datos.
- **Ubicación exacta en `estado-inicial` (`e5d6927`):** `main.py`, líneas 28–33 y 37; `hospital/gestion.py`, líneas 12–16.
- **Evidencia:** Solo se controla el JSON mal escrito (`ValueError`). Si el archivo es JSON válido pero con otra forma, el programa se corta en la primera operación: con `TypeError` si el archivo tiene `[]` y con `KeyError` si tiene `{}`. Si faltan los dos archivos (`local.json` y `ejemplo.json`), se corta con `FileNotFoundError`. Si se cierra la entrada estándar con `Ctrl+D`, termina abruptamente con `EOFError`.
- **Impacto:** Afecta la calidad externa en casos de borde, porque quien usa el sistema ve un *traceback* técnico en lugar de un aviso claro.
- **Riesgo de mantenimiento:** Los fallos aparecen lejos de su causa real y cuesta encontrarlos.
- **Prioridad:** Alta.
- **Acción propuesta:** Validar la estructura de claves al cargar el JSON y atrapar los errores previstos (`EOFError`, `KeyboardInterrupt`, `OSError`) con un mensaje claro.

#### H5 — Validación de fecha duplicada (*Duplicated Code*)
- **ID:** H5
- **Problema / Code Smell:** Validación de fecha duplicada (*Duplicated Code*).
- **Ubicación exacta en `estado-inicial` (`e5d6927`):** `hospital/gestion.py`, líneas 54–59 (`reservar_turno`) y líneas 111–116 (`agenda_profesional`).
- **Evidencia:** `reservar_turno` y `agenda_profesional` repiten exactamente las mismas seis líneas con `datetime.strptime(fecha, "%Y-%m-%d")` y `strftime` para comprobar el formato `AAAA-MM-DD`, duplicando además el literal del mensaje de error cuatro veces.
- **Impacto:** Si cambia el formato aceptado o el texto de error, hay que corregir las dos copias.
- **Riesgo de mantenimiento:** Medio; hoy son dos copias, pero cada consulta nueva con fecha agregaría otra.
- **Prioridad:** Media.
- **Acción propuesta:** Extraer una función `validar_fecha(fecha)` reutilizable.

#### H6 — Demasiados parámetros en la reserva (*Long Parameter List*)
- **ID:** H6
- **Problema / Code Smell:** Lista larga de parámetros en la reserva (*Long Parameter List*).
- **Ubicación exacta en `estado-inicial` (`e5d6927`):** `hospital/gestion.py`, línea 39 (`def reservar_turno(datos, paciente_id, profesional_id, fecha, hora)`); `main.py`, líneas 57–66.
- **Evidencia:** `reservar_turno` recibe cinco parámetros, y cuatro de ellos (`paciente_id`, `profesional_id`, `fecha` y `hora`) viajan siempre juntos desde la consola.
- **Impacto:** La firma es larga y es fácil pasar los datos en otro orden (por ejemplo, invertir `paciente_id` y `profesional_id` o `fecha` y `hora`) sin que nada lo detecte antes de ejecutar.
- **Riesgo de mantenimiento:** Medio; sumar un dato a la solicitud de reserva obliga a cambiar la firma de la función y todas sus llamadas.
- **Prioridad:** Media.
- **Acción propuesta:** Agrupar esos cuatro datos en un solo objeto de solicitud de turno (*Introduce Parameter Object*).

#### H7 — Errores informados con `False`
- **ID:** H7
- **Problema / Code Smell:** Retorno de códigos de estado booleanos y tuplas polimórficas en lugar de excepciones.
- **Ubicación exacta en `estado-inicial` (`e5d6927`):** `hospital/gestion.py` (14 sentencias `return False, ...`); `main.py` (5 controles `if ok:` / `if not ok:`).
- **Evidencia:** Las operaciones devuelven `(False, mensaje)` cuando algo falla; hay 14 retornos así. En las consultas (`agenda_profesional` e `historial_paciente`), el segundo valor de la tupla es un `str` si falló y una `list` si salió bien.
- **Impacto:** Quien llama tiene que revisar la bandera booleana cada vez antes de seguir, y el mismo valor de retorno puede ser de dos tipos distintos.
- **Riesgo de mantenimiento:** Medio; si una nueva llamada se olvida de revisar `ok`, el error pasa desapercibido o se procesa un texto como si fuera una lista.
- **Prioridad:** Media.
- **Acción propuesta:** Lanzar excepciones propias del dominio y atraparlas de forma centralizada en la consola.

#### H8 — La consola depende de la forma interna de los datos (acoplamiento)
- **ID:** H8
- **Problema / Code Smell:** Acoplamiento entre la interfaz de consola y la estructura interna del diccionario.
- **Ubicación exacta en `estado-inicial` (`e5d6927`):** `main.py`, líneas 52–56, 89–96 y 108–112.
- **Evidencia:** `main.py` recorre `datos["profesionales"]` directamente en la opción 3 (a diferencia de los pacientes, donde sí usa una función) y arma los mensajes leyendo claves anidadas internas como `franja["turno"]["turno_id"]`.
- **Impacto:** Cualquier cambio en la estructura interna de los datos rompe la consola, aunque las reglas de negocio sigan iguales.
- **Riesgo de mantenimiento:** Medio; obliga a cambiar dos capas distintas por un solo motivo.
- **Prioridad:** Media.
- **Acción propuesta:** Que la consola use únicamente funciones de consulta expuestas por la capa de negocio y no lea el diccionario de almacenamiento directamente.

#### H9 — Escritura directa sobre el archivo
- **ID:** H9
- **Problema / Code Smell:** Persistencia no atómica por sobrescritura directa del archivo destino.
- **Ubicación exacta en `estado-inicial` (`e5d6927`):** `hospital/gestion.py`, líneas 19–21 (`guardar_datos`).
- **Evidencia:** `guardar_datos` abre `datos/local.json` directamente en modo escritura (`"w"`), truncando el archivo antes de volcar el contenido con `json.dump`.
- **Impacto:** Si la escritura se interrumpe a mitad (corte de energía, cierre forzado o error de serialización), el archivo queda incompleto o vacío y en la próxima apertura se informa como dañado.
- **Riesgo de mantenimiento:** Medio; es un riesgo de pérdida de datos poco probable en uso local, pero grave si ocurre.
- **Prioridad:** Media.
- **Acción propuesta:** Escribir primero en un archivo temporal en el mismo directorio y reemplazar el archivo original de forma atómica al terminar (`os.replace`).

#### H10 — Datos del dominio como texto suelto (*Primitive Obsession*)
- **ID:** H10
- **Problema / Code Smell:** Obsesión por primitivas (*Primitive Obsession*).
- **Ubicación exacta en `estado-inicial` (`e5d6927`):** `hospital/gestion.py`, líneas 8–9 y 73–80.
- **Evidencia:** El turno, el paciente y el profesional son diccionarios genéricos; el estado del turno es el texto `"ACTIVO"` o `"CANCELADO"` y la fecha es un string que se vuelve a validar en cada función.
- **Impacto:** Nada impide que en algún lugar del código se escriba un estado inválido o una clave mal tipeada sin que el intérprete lo advierta.
- **Riesgo de mantenimiento:** Bajo hoy, porque los estados ya están definidos como constantes del módulo, pero crece si se agregan nuevos estados o atributos.
- **Prioridad:** Baja.
- **Acción propuesta:** Representar el turno, las entidades y su estado con tipos propios (`dataclass` / `Enum`), si el resto de los cambios lo justifica.

#### H11 — Agenda y reserva no coinciden con datos inconsistentes
- **ID:** H11
- **Problema / Code Smell:** Asimetría en la verificación de integridad referencial entre consulta de agenda y reserva.
- **Ubicación exacta en `estado-inicial` (`e5d6927`):** `hospital/gestion.py`, líneas 121–131 (`agenda_profesional`).
- **Evidencia:** En `agenda_profesional`, una franja solo se marca como ocupada si el bucle interno encuentra al paciente en `datos["pacientes"]`. Si un turno activo apunta a un `paciente_id` inexistente (por ejemplo, porque se editó `local.json` a mano), la agenda muestra esa franja como `libre`, pero al intentar reservarla `reservar_turno` la rechaza porque el profesional está ocupado.
- **Impacto:** El sistema da dos respuestas contradictorias sobre la disponibilidad de la misma franja horaria.
- **Riesgo de mantenimiento:** Bajo; solo puede ocurrir si el archivo JSON es modificado de forma inconsistente por fuera del programa.
- **Prioridad:** Baja.
- **Acción propuesta:** Que la agenda marque la franja como ocupada aunque falte el registro del paciente, y validar la integridad referencial al cargar los datos.

---

## 3. Análisis estático con SonarQube y alcance de la herramienta

Para completar la revisión pasamos **SonarQube** sobre la versión inicial (tag `estado-inicial`, 231 líneas de código). El análisis no encontró bugs ni vulnerabilidades y aprobó su configuración por defecto (*Quality Gate: Passed* bajo el perfil *Sonar way*), pero reportó **4 *issues* de mantenibilidad de severidad Alta (*High*)** que respaldan cuantitativamente nuestro diagnóstico:

1. **Complejidad cognitiva de `main()` = 76** (`main.py`, línea 27, esfuerzo estimado: 1h 06min): Excede ampliamente el umbral máximo permitido de 15 debido al anidamiento de estructuras `if/elif/else` y bucles para cada opción del menú (sustenta **H1**).
2. **Complejidad cognitiva de `reservar_turno()` = 23** (`hospital/gestion.py`, línea 39, esfuerzo estimado: 13min): Supera el máximo de 15 como consecuencia de la secuencia encadenada de búsquedas y seis validaciones consecutivas (sustenta **H1**).
3. **Complejidad cognitiva de `agenda_profesional()` = 22** (`hospital/gestion.py`, línea 103, esfuerzo estimado: 12min): Supera el máximo de 15 al combinar iteraciones anidadas en búsquedas por ID y validación de fechas (sustenta **H1, H2 y H5**).
4. **Duplicación de literales de fecha** (`hospital/gestion.py`, línea 57, esfuerzo estimado: 8min): Detecta la repetición del literal `"La fecha no es válida. Usá el formato AAAA-MM-DD."` 4 veces en el mismo archivo, evidenciando la falta de centralización en la validación (sustenta **H5**).

### Por qué SonarQube califica con "A" y qué problemas no detecta
A pesar de estos cuatro problemas de severidad alta, el proyecto obtuvo la **calificación A en mantenibilidad** (con 0% de duplicación reportada). Esto se explica por el modelo de cálculo y el alcance de las reglas estáticas:
- **Cálculo del *Technical Debt Ratio*:** SonarQube calcula la calificación comparando el tiempo estimado para corregir los problemas detectados (**1 hora y 39 minutos = 99 minutos**) contra el costo estimado de reescribir desde cero las **231 líneas de código** (a razón de 30 minutos por línea). La proporción da un 1,4% (99 sobre 6.930 minutos) y, como es menor al 5%, la calificación es A. El *Quality Gate* es otro control, y también aprobó.
- **Ceguera ante problemas arquitectónicos (H3 y H8):** Las reglas estáticas de SonarQube analizan la sintaxis y el flujo de control de cada función por separado, pero no comprenden la semántica de capas del dominio; por eso no detectan que `gestion.py` mezcle reglas de negocio con persistencia en archivos JSON (**H3**) ni que la interfaz `main.py` dependa de la estructura interna de los diccionarios (**H8**).
- **Umbral mínimo de bloques duplicados (H2):** SonarQube reportó `0.0% Duplications` y no marcó los siete bucles de búsqueda secuencial (**H2**) porque su detector de clones exige un mínimo de líneas o tokens idénticos consecutivos, mientras que aquí son bucles cortos de 3 líneas donde cambia el nombre de la clave consultada (`"pacientes"`, `"profesionales"`, `"turnos"`).

Por estas razones utilizamos el análisis estático de SonarQube como evidencia cuantitativa complementaria de la lectura crítica del código y de las pruebas de casos de borde, y no como única fuente de diagnóstico.
