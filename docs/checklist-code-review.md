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
