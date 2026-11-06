# Checklist de code review

Usamos este checklist para revisar cada Pull Request.

| Categoría | Qué revisamos |
|---|---|
| Lógica y funcionalidad | Si respeta las reglas de reserva y cancelación, si cubre los casos de borde (fecha inválida, franja ocupada, turno ya cancelado) y si conserva el comportamiento de la versión inicial. |
| Legibilidad | Si los nombres dicen lo que hacen y si cada función se entiende sin tener que preguntarle a quien la escribió. |
| Diseño | Si cada función o clase tiene una sola responsabilidad, si las reglas de turnos quedan separadas de la consola y del JSON y si hay lógica repetida. |
| Manejo de errores | Si los errores se informan con un mensaje claro y si hay excepciones capturadas que se pierden sin aviso. |
| Seguridad y datos | Si se validan las entradas, si se usan solo datos ficticios y si el archivo de trabajo local queda fuera de Git. |
| Rendimiento | Si se lee o se escribe el archivo más veces de las necesarias. |
| Pruebas | Si hay pruebas para lo que cambió y si pasan todas. |

## Criterios de aceptación técnica

Un Pull Request se acepta cuando:

- pasan las pruebas, Black y flake8;
- no rompe funcionalidades existentes ni cambia las reglas acordadas, salvo que el Pull Request lo diga;
- respeta los principios de diseño y las convenciones del proyecto;
- maneja los errores sin ocultarlos;
- no agrega deuda técnica innecesaria;
- lo revisó otro integrante y sus observaciones quedaron resueltas o justificadas.

## Cómo escribimos cada observación

En tres partes: qué vemos en el código, por qué importa y qué proponemos.

## Revisiones de los Pull Requests

Cada Pull Request lo revisó y lo aprobó un integrante distinto del autor. `main` exige una aprobación y que la integración continua esté en verde.

| Pull Request | Autor | Revisó y aprobó | Merge |
|---|---|---|---|
| #7. Entorno de desarrollo | Agustín | Santiago | `587390a` |
| #8. Base funcional | Agustín | Bruno | `e5d6927` |
| #12. Diagnóstico y ADR | Bruno | Agustín | `e60e89c` |
| #14. Diagnóstico alineado, checklist y evidencias | Agustín | Bruno | `0894c42` |
| #20. Búsqueda única (H2) | Agustín | Bruno | `fc147dc` |
| #21. Módulo de persistencia (H3) | Agustín | Bruno | `e873b85` |
| #22. Pruebas de caracterización y CI | Santiago | Agustín (pidió cambios antes de aprobar) | `e94aaad` |
| #23. Funciones del menú y de la reserva (H1 y H5) | Bruno | Agustín (pidió cambios antes de aprobar) | `a10ba35` |
| #25. Guardado seguro (H9) | Agustín | Santiago | `c6ce82b` |
| #26. Objeto de solicitud (H6) | Santiago | Bruno | `465cc5e` |
| #33. Documentación de los refactorings | Santiago | Agustín | `0ed7e4b` |
| #34. SonarQube final y diagnóstico | Agustín | Santiago | `8cb2b40` |
| #35. README final | Santiago | Bruno | `c5e488a` |

**Revisión del #26:** Bruno revisó que `SolicitudTurno` fuera un `dataclass` inmutable, y que se mantuvieran el orden de las validaciones, la precedencia de los mensajes y el formato que se guarda en el JSON. Revisó también que la consola cree la solicitud después de validar los números y que las pruebas usen la nueva forma de llamar. Lo aprobó el 05/11, con las 20 pruebas, Black y flake8 en verde, y lo integró.
