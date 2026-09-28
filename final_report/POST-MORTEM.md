## My response to the jury 

Agradezco la retroalimentación brindada durante la predefensa, a partir de la cual les presento las generalidades de mi proyecto de forma más clara.



Síntesis del problema y justificación

La fragmentación de evidencia en las etapas tempranas de diseño de sistemas de potencia eléctrica para nanosatélites, dificulta establecer la trazabilidad entre una necesidad o requisito, las decisiones de arquitectura asociadas y la evidencia analítica que las sustenta. Asimismo, dificulta reproducir los análisis y detectar inconsistencias antes de avanzar hacia etapas de verificación y validación física.
 
El proyecto se justifica por la limitada integración en la evidencia existente sobre el uso de ingeniería de sistemas basada en modelos (MBSE) en el diseño de sistemas de potencia eléctrica (EPS) de nanosatélites. Aunque la literatura reporta beneficios en trazabilidad, consistencia e integración, son pocos los trabajos específicos para EPS y la evidencia que respalda dichos beneficios es limitada. Por ello surge la necesidad de un marco que integre requisitos, arquitectura, análisis y verificación temprana mediante evidencia trazable y reproducible, favoreciendo la justificación de decisiones de diseño y la detección temprana de inconsistencias.

Entregable final

Obj.

Objetivo

Entregable

Indicador

1

Caracterizar necesidades, restricciones, interfaces y criterios técnicos del EPS de nanosatélites.

Matriz trazable de caracterización del EPS, que consolide necesidades, restricciones, interfaces y criterios técnicos, indicando fuente o justificación y su relación con los elementos que deberá contemplar el marco.

100 % de los elementos incorporados a la caracterización cuentan con fuente o justificación trazable y clasificación.

2

Definir el flujo operativo de modelado, análisis y gestión de evidencia del marco MBSE mediante la evaluación y selección justificada de métodos, lenguajes y herramientas aplicables.

Flujo operativo definido y justificado del marco MBSE, incluyendo fases con actividades, entradas, salidas, herramientas/interfaces y mecanismos para conservar trazabilidad y reproducibilidad de la evidencia.

100 % de las fases requeridas para implementar el flujo cuentan con alternativas evaluadas y una decisión documentada, incluyendo criterio y justificación de selección.

3

Modelar la arquitectura genérica del EPS con funciones, componentes lógicos, interfaces, modos de operación y restricciones.

Modelo MBSE de arquitectura genérica del EPS, independiente de una misión particular y trazable hacia los requisitos seleccionados.

100 % de los requisitos seleccionados están vinculados con uno o más elementos de la arquitectura, y la cobertura del modelo genérico se contrasta con dos casos de estudio, uno tradicional basado en BIRDS-4 y otro de alta autonomía.

4

Caracterizar la verificación temprana de requisitos del EPS dentro del marco MBSE.

Matriz de verificación temprana, compuesto por requisitos seleccionados, métodos de verificación, criterios de aceptación, evidencia requerida y mecanismos para registrar resultados.

100 % de los requisitos seleccionados para verificación cuentan con método, criterio de aceptación y evidencia asociada, manteniendo trazabilidad de requisito a método a resultado.

5

Evaluar el marco MBSE en dos casos de estudio contrastantes de EPS.

Informe de evaluación del marco mediante dos casos contrastantes, uno tradicional basado en BIRDS-4 y otro de alta autonomía, incluyendo resultados de aceptación y desempeño.

Los 2 casos se completan utilizando el mismo núcleo del marco, con evidencia trazable y reproducible y sin modifcaciones post hoc. Además se reportan las medidas de aceptación y desempeño definidas para la evaluación.


Validación

Se verificará que el marco implementado satisfaga los requisitos establecidos para su funcionamiento. Esto incluye, entre otros aspectos, mantener cadenas válidas de evidencia, reproducir los análisis de EPS, identificar y gestionar discrepancias críticas y completar los dos casos de estudio sin introducir modificaciones post hoc al marco.
El cumplimiento de requisitos está asociado a métricas cuantitativas. Entre ellas se contemplan el tiempo requerido para procesar correctamente un cambio, el esfuerzo (tiempo dedicado por una persona) requerido para adaptar el marco a un caso particular, el esfuerzo necesario para reproducir independientemente un análisis, el esfuerzo de adopción, el costo directo de utilización y la efectividad para detectar inconsistencias (comparado a una persona cualificada).

Los dos casos de estudio permitirán comprobar si un mismo núcleo del marco puede aplicarse a configuraciones de EPS contrastantes manteniendo la trazabilidad y reproducibilidad de la evidencia.

Metodología de diseño de ingeniería

La metodología de diseño de ingeniería que aplico es Object-Oriented Systems Engineering Method (OOSEM).
Sus etapas principales, y sus equivalentes del libro Diseño y desarrollo de productos de Ulrich y Eppinger entre paréntesis, son las siguientes:

- Análisis de las necesidades de las partes interesadas (Identificación de las necesidades del cliente)
- Análisis de requerimientos del sistema (Especificaciones del producto)
- Definición de la arquitectura lógica (Especificaciones del producto y Generación de conceptos)
- Síntesis de arquitecturas físicas candidatas (Generación de conceptos y Selección del concepto)

Por qué es un proyecto de mecatrónica

Aunque la implementación tecnológica del marco contiene una componente importante de software, el proyecto no se limita al desarrollo de una aplicación informática. El objeto de ingeniería sobre el cual opera el marco es el sistema de potencia eléctrica de un nanosatélite. Su representación y análisis requieren integrar aspectos propios de distintas áreas de Mecatrónica: sistemas eléctricos y electrónicos de potencia, adquisición y monitoreo de variables, interfaces entre subsistemas, modos y estados de operación, modelado y simulación, control y automatización, y herramientas computacionales para integrar y verificar información de ingeniería.

Quedo atento en caso de que deseen confirmar el correo como recibido o como aprobado, o si desean externar otra retroalimentación.
