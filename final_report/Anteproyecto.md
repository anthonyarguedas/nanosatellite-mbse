---
source: "Projects/PFG/Anteproyecto_Arguedas_Rodríguez_Anthony_José.pdf"
title: "Anteproyecto_Arguedas_Rodríguez_Anthony_José"
page_count: 34
converted_at: "2026-09-04T20:29:04Z"
---

<!-- PDF_PAGE: 1 -->

Instituto Tecnológico de Costa Rica

Escuela de Ingeniería Mecatrónica

TEC

Tecnológico de Costa Rica

Marco de Ingeniería de Sistemas Basada en Modelos para la Justificación Temprana del Diseño de Sistemas de Potencia Eléctrica en Nanosatélites

<div align="center">

# Anteproyecto de graduación para optar por el título de Ingeniero en Mecatrónica con el grado académico de Licenciatura

</div>

Anthony José Arguedas Rodríguez

2022218504

Cartago, agosto de 2026

<!-- PDF_PAGE: 2 -->

## Contenido

Contenido...2

Entorno del Proyecto...3

Definición del problema...4

Generalidades...4

Justificación...5

Diagrama Causa–Efecto (Ishikawa)...8

Síntesis del problema...9

Procedimientos para la ejecución del proyecto...9

Ruta de ejecución basada en OOSEM...10

Control de alcance y evidencias...13

Objetivo General...13

Objetivos Específicos...13

Enfoque de la solución...15

Dirección técnica y tipo de solución...15

Arquitectura Funcional...18

Validación esperada...20

Cronograma...23

Lista de actividades...23

Diagrama de Gantt...25

Uso de recursos...28

Presupuesto...29

Referencias...31

Anexo A. Carta de Aceptación por parte de la Empresa...33

Anexo B. Hoja de Información del Proyecto...34

<!-- PDF_PAGE: 3 -->

## Entorno del Proyecto

La Escuela Superior de Tecnología (École de technologie supérieure, ÉTS), ubicada en Montréal, Canadá, es una institución de educación superior especializada en la enseñanza de la ingeniería y la transferencia tecnológica a la industria. Dentro de la ÉTS, el Departamento de Ingeniería Aeroespacial atiende las necesidades del sector aeroespacial canadiense, consolidado pero aún en crecimiento. El departamento impulsa planes de estudio y líneas de investigación relacionadas con sistemas inteligentes y autónomos, materiales innovadores y fabricación avanzada. Entre su equipamiento especializado de investigación se destacan diversos sistemas aeroespaciales reacondicionados como bancos de prueba o simuladores, entre ellos una aeronave Piaggio Avanti P-80 y parte de una constelación de satélites GlobalStar, con los cuales pueden verificarse sistemas de aviónica o telecomunicaciones, entre otros [1]. Estos elementos describen la capacidad institucional disponible, pero no implican por sí mismos el uso directo de un laboratorio, banco de prueba o equipo específico al momento en que este anteproyecto fue definido.

La dirección académica del proyecto estará a cargo del profesor Jesús David González Llorente, Ph.D., del Departamento de Ingeniería Aeroespacial de la ÉTS. Su perfil institucional lo vincula con sistemas espaciales, pequeños satélites, calificación espacial, sistemas de alimentación eléctrica para vehículos espaciales, modelado y control, conversión y almacenamiento de energía, sistemas inteligentes y autónomos, sistemas ciberfísicos, e inteligencia artificial y aprendizaje automático en el espacio [2]. Además, una publicación reciente de su autoría propone validar sistemas de potencia eléctrica (Electrical Power System, EPS) de CubeSat con componentes comerciales disponibles (Commercial Off-The-Shelf, COTS) mediante análisis de presupuesto de potencia alineado con requisitos de misión [3], antecedente directamente relacionado con la formulación de este proyecto.

El trabajo también se enmarca en una colaboración académica entre ÉTS, el Tecnológico de Costa Rica (TEC) y universidades aliadas en temas de sistemas

<!-- PDF_PAGE: 4 -->

espaciales confiables. Dicha alianza se evidencia en publicaciones conjuntas y visitas de docentes del TEC a ÉTS como profesores invitados.

En este documento, los casos, datos, modelos, restricciones institucionales y comentarios técnicos se documentarán como evidencia académica del proyecto, según la disponibilidad de información y los acuerdos de trabajo con el director académico. Se presenta una revisión sistemática como antecedente la cual delimita el entorno técnico a literatura sobre CubeSat/nanosatélites con ingeniería de sistemas basada en modelos (Model-Based Systems Engineering, MBSE), evidencia relacionada con EPS y potencia eléctrica, y verificación previa a pruebas físicas.

## Definición del problema

## Generalidades

El presente proyecto aborda el diseño de sistemas de potencia eléctrica (EPS) para nanosatélites desde una perspectiva de ingeniería mecatrónica y MBSE. Un EPS integra generación, almacenamiento, conversión, regulación y distribución de energía; electrónica de potencia; sensores; mecanismos de protección; software de supervisión; modos de operación; restricciones orbitales; interfaces de alimentación, control y datos con otros subsistemas; y criterios de verificación. Por tanto, su diseño no puede tratarse únicamente como un problema eléctrico, sino como un sistema mecatrónico complejo acoplado a la misión completa del nanosatélite. En esta propuesta, la misión y el nanosatélite constituyen el sistema mayor; el EPS es el subsistema intervenido; y la frontera del proyecto se sitúa en los artefactos de requisitos, arquitectura, análisis de potencia/energía, modos de operación e interfaces que permiten justificar el EPS sin extenderse al diseño completo de la misión ni a la fabricación de hardware de vuelo.

En las etapas tempranas de diseño, las decisiones sobre el EPS se toman antes de disponer de una construcción física completa. Estas decisiones condicionan la

<!-- PDF_PAGE: 5 -->

arquitectura de potencia, la factibilidad de los modos de operación, la integración con cargas, la seguridad eléctrica, la gestión de energía y la posibilidad de generar evidencia antes de pruebas físicas. La situación negativa identificada en la literatura revisada, la cual se interpreta como un diagnóstico representativo del campo de aplicación, no se reduce a la falta de una herramienta o de un marco MBSE, sino a la fragmentación de la evidencia técnica: requisitos, modelos, presupuestos de potencia, simulaciones y procedimientos de verificación aparecen con frecuencia como artefactos parciales o débilmente conectados. Bajo esas condiciones, el equipo de desarrollo pierde trazabilidad y se dificulta justificar por qué una arquitectura de EPS satisface las necesidades de misión dentro de las restricciones del nanosatélite.

## Justificacion

La necesidad del proyecto surge de la revisión sistemática de literatura realizada como primera etapa de la investigación. La revisión se basó principalmente en búsquedas por palabras clave a través de Scopus e IEEE Xplore, e identificó 199 registros de los cuales se eliminaron 118 duplicados, se examinaron 81 registros únicos, se intentó recuperar el texto completo de 44 trabajos, de los cuales 4 no estuvieron disponibles, y se sintetizaron 40 trabajos publicados entre 2013 y 2025. El conjunto extraído comprendió 21 estudios núcleo y 19 de apoyo, con puntuaciones de calidad entre 5.0 y 7.5 sobre 8 y una media de 6.21. De esos 40 estudios, 34 presentaron alguna relación con EPS o potencia eléctrica: 19 con presupuestos de potencia o arquitectura eléctrica, 13 adyacentes a EPS y solamente 2 específicos de EPS. Esta distribución constituye evidencia preliminar de que el subsistema de potencia aparece con frecuencia dentro de modelos de nanosatélite o flujos de diseño preliminar, pero con menor tratamiento específico e integrado como problema de diseño del EPS.

La revisión también muestra que los beneficios atribuidos a MBSE suelen relacionarse con trazabilidad, consistencia, integración, interoperabilidad, reutilización, estandarización, automatización, continuidad del ciclo de vida y

<!-- PDF_PAGE: 6 -->

confiabilidad. Sin embargo, la base de evidencia es débil: de 270 afirmaciones de valor extraídas, 52 se clasificaron como no sustentadas, 139 como débiles, 77 como moderadas y solo 2 como fuertes; además, las dos afirmaciones fuertes no correspondieron a confiabilidad de EPS, sino a efectos de costo o cronograma en un caso de diseño concurrente. Las limitaciones encontradas incluyeron cobertura incompleta del ciclo de vida, vínculo débil entre afirmación y evidencia, evidencia de caso único, ausencia de validación independiente y madurez limitada de prototipo y resultados planteados como trabajo futuro. 39 trabajos no presentaron evidencia física o de vuelo, 38 carecieron de línea base o comparador, 35 no realizaron evaluación cuantitativa del resultado MBSE y 34 no pusieron a disposición activos de modelo. Por ello, el alcance del proyecto no presupone que MBSE haya demostrado de forma general una mejora directa en la confiabilidad de vuelo del EPS. En su lugar, plantea una contribución más acotada y verifiable: estructurar y evaluar evidencia sobre trazabilidad, reproducibilidad, capacidad de integración y verificación temprana dentro de los casos seleccionados.

La brecha es especialmente relevante en la integración de verificación y validación dentro del modelo. En términos cuantitativos, 25 estudios presentaron verificación previa a pruebas físicas específica de EPS/potencia, 23 incluyeron comprobaciones paramétricas, de presupuesto o de restricciones, 22 simulaciones ejecutables o análisis de escenarios, 21 paquetes de prueba o actividades de verificación y validación (V&V), 19 trazabilidad requisito–modelo o matrices de verificación y 11 acoplamientos con herramientas o flujos de datos externos. Como antecedente externo a MBSE, Acero et al. (con el Dr. González Llorente como coautor) proponen un método genérico para validar EPS de CubeSat mediante presupuesto de potencia, modos de operación, profundidad de descarga y ciclos de carga/descarga en la misión LEOPAR; sus conclusiones señalan como trabajo futuro extender el método hacia modelado del EPS y software de gestión de energía [3]. Este antecedente refuerza la pertinencia de conectar análisis eléctrico, requisitos, modos de operación y software de gestión de energía. No obstante, las capacidades reportadas aparecen fragmentadas, pues el nivel máximo de integración de V&V se

<!-- PDF_PAGE: 7 -->

concentró en simulación en lazo, comprobaciones ejecutables o artefactos enlazados por trazabilidad, mientras que software-in-the-loop o hardware-in-the-loop apareció solamente en un estudio.

El impacto técnico de esta fragmentación se relaciona con la calidad del diseño, la trazabilidad de decisiones, la eficiencia de revisión, la reproducibilidad de análisis y la detección temprana de inconsistencias de integración. En un EPS de nanosatélite, estas dimensiones son críticas porque el subsistema alimenta cargas, protege elementos eléctricos, administra modos de operación y se acopla con restricciones de misión.

El alcance del anteproyecto está condicionado por restricciones operativas: las decisiones se estudiarán antes de construir hardware de vuelo; los casos dependerán de datos disponibles de literatura, casos publicados o información técnica facilitada durante la pasantía; las herramientas dependerán de licencias, disponibilidad institucional y tiempo de aprendizaje; y la validación se limitará a matrices de trazabilidad, análisis de potencia/energía, simulaciones, prototipado virtual y revisión técnico-académica. Estas restricciones condicionan las decisiones de diseño y evitan convertir el problema en una promesa de validación física o de confiabilidad de vuelo.

Para la ÉTS y su Departamento de Ingeniería Aeroespacial, el proyecto es pertinente porque se alinea con líneas de investigación en sistemas espaciales, sistemas autónomos, calificación espacial, sistemas de alimentación eléctrica, modelado y control, y sistemas ciberfísicos. Para el TEC, el trabajo conserva una orientación mecatrónica al integrar electrónica de potencia, software, modelado de sistemas, simulación, interfaces y verificación. El resultado esperado no es solamente un documento descriptivo, sino un marco reproducible que pueda apoyar futuros proyectos académicos e industriales de nanosatélites y facilitar la comunicación entre disciplinas. Asimismo, la revisión del estado del arte que sustenta este anteproyecto fue realizada bajo la dirección del Dr. González Llorente

<!-- PDF_PAGE: 8 -->

con la intención de ser sometida a una conferencia antes del inicio formal del proyecto. A partir de los frutos consolidados del proyecto se pretende preparar posteriormente una publicación de revista.

## Diagrama Causa-Efecto (Ishikawa)

La Figura 1 sintetiza causas preliminares asociadas con la problemática identificada. El efecto corresponde a la situación descrita en la síntesis: fragmentación de evidencia que dificulta justificar la arquitectura del EPS y detectar inconsistencias de integración antes de pruebas físicas. Las ramas agrupan variables técnicas y metodológicas que contribuyen a esa dificultad, evitando presentarlas como acciones correctivas. Las etiquetas [E] señalan causas respaldadas por la revisión sistemática y las etiquetas [H] señalan hipótesis de trabajo que deberán contrastarse durante la caracterización, el modelado y la revisión técnico-académica.


![figure_001.png](Anteproyecto_Arguedas_Rodríguez_Anthony_José_images/figure_001.png)



<div align="center">

Figura 1. Diagrama causa-efecto para la fragmentación de evidencia que dificulta justificar la arquitectura del EPS y detectar inconsistencias de integración antes de pruebas físicas

</div>

<!-- PDF_PAGE: 9 -->

## Síntesis del problema

Durante el diseño temprano de sistemas de potencia eléctrica para nanosatélites, la evidencia que sustenta decisiones de arquitectura, operación e interfaces suele quedar dispersa entre requisitos, presupuestos de potencia, modelos parciales y simulaciones no conectadas. Esta fragmentación reduce la trazabilidad y reproducibilidad del diseño, y dificulta justificar la arquitectura del EPS y detectar inconsistencias de integración antes de pruebas físicas.

## Procedimientos para la ejecución del proyecto

El proyecto se realizará como una investigación aplicada de diseño de ingeniería durante la pasantía en la ÉTS, comprendida entre el 4 de agosto y el 1 de diciembre de 2026, con actividades previas de preparación y formalización del anteproyecto. La ruta técnica se organizará con una sola metodología base: OOSEM (Object-Oriented Systems Engineering Method). Esta metodología resulta pertinente porque permite partir de actores, necesidades, escenarios, requisitos, arquitectura funcional y lógica, restricciones e información de verificación, que son precisamente los artefactos que el problema identifica como fragmentados en el diseño temprano de EPS de nanosatélites [4]. No se declara una adaptación formal adicional de OOSEM ni se emplean otras metodologías como fundamento del procedimiento. Las matrices, listas de verificación, cálculos, registros de decisión y minutas se utilizarán únicamente como instrumentos de documentación, análisis y control de evidencia dentro de esa ruta.

Las principales fuentes documentales serán la revisión sistemática de literatura sobre MBSE, nanosatélites, EPS y V&V temprana, junto con sus registros de búsqueda, matriz de extracción, códigos controlados, conteos de evidencia, indicadores de limitación y registros de trazabilidad; publicaciones técnicas de casos CubeSat/nanosatélite; documentación de OOSEM, Systems Modeling Language (SysML) y herramientas candidatas; y documentación pública o institucional disponible en la ÉTS y el TEC. También se considerará el linaje de publicaciones

<!-- PDF_PAGE: 10 -->

del Space Systems Working Group CubeSat System Reference Model (SSWG CSRM), que aborda la definición de una arquitectura o modelo de referencia para el nanosatélite completo. Este linaje no se centra solo en el EPS ni detalla en particular el subsistema de potencia eléctrica; sin embargo, al estar compuesto por varias publicaciones y cubrir múltiples vistas del sistema, brinda una referencia de madurez, completitud e integración útil para contrastar el marco propuesto. Los sujetos de información serán el director académico en la ÉTS, revisores del TEC y, cuando sea necesario, especialistas consultados en sistemas espaciales, potencia eléctrica, MBSE, simulación o mecatrónica.

## Ruta de ejecución basada en OOSEM

Las etapas siguientes describen la secuencia técnica del proyecto, sin dimensión cronológica. Cada etapa conserva la lógica de OOSEM y produce evidencia revisable asociada con los objetivos específicos, indicadores y entregables definidos en el listado de objetivos.

<!-- PDF_PAGE: 11 -->

<div align="center">

Tabla 1. Ruta de ejecución basada en OOSEM.

</div>

<table border="1"><tr><td>Etapa</td><td>Qué se hará</td><td>Por qué se hará</td><td>Cómo se hará</td><td>Evidencia que producirá</td><td>Objetivos asociados</td></tr><tr><td>1</td><td>Caracterizar el contexto del EPS dentro del nanosatélite, los actores técnicos, necesidades, restricciones, interfaces, funciones esperadas y fuentes disponibles.</td><td>Para delimitar la frontera del problema y evitar que el marco MBSE dependa de una herramienta o solución física preseleccionada.</td><td>Se revisarán la literatura sistematizada, fuentes documentales e institucionales disponibles, comentarios técnicos de especialistas y antecedentes institucionales; cada elemento se registrará con fuente, justificación o supuesto explícito.</td><td>Matriz de necesidades, restricciones, interfaces y criterios técnicos con trazabilidad de fuente.</td><td>Obj.1</td></tr><tr><td>2</td><td>Formular requisitos seleccionados, escenarios o modos de operación relevantes del EPS y criterios técnicos para el flujo de modelado, análisis y gestión de evidencia.</td><td>Para transformar las necesidades de misión y de revisión técnica en elementos verificables, conectados con arquitectura y evidencia temprana.</td><td>Se asignarán identificadores a necesidades, requisitos, criterios, interfaces y supuestos; se documentará la relación entre cada requisito y su origen, condición de evaluación o restricción.</td><td>Conjunto inicial de requisitos seleccionados, criterios técnicos y supuestos documentados.</td><td>Obj.1 y Obj.2</td></tr><tr><td>3</td><td>Seleccionar el flujo operativo de modelado, análisis y gestión de evidencia.</td><td>Para asegurar que las herramientas y formatos apoyen la trazabilidad, reproducibilidad y capacidad de integración sin definir por sí mismos el alcance de la solución.</td><td>Se compararán alternativas por categoría mediante la matriz ponderada indicada en los indicadores del proyecto, considerando disponibilidad, licenciamiento, interoperabilidad, curva de aprendizaje, capacidad de trazabilidad y factibilidad temporal; la decisión se revisará con el director académico.</td><td>Registro de decisión del flujo operativo, con puntuaciones, restricciones, decisión y justificación.</td><td>Obj.2</td></tr><tr><td>4</td><td>Modelar la arquitectura genérica del EPS según OOSEM.</td><td>Para representar de forma trazable las funciones, componentes lógicos, interfaces, modos de operación y restricciones que permiten justificar tempranamente el diseño del EPS.</td><td>Se construirán vistas de necesidades, requisitos, funciones, arquitectura funcional/lógica, interfaces y restricciones; cada requisito seleccionado deberá vincularse al menos con un elemento arquitectónico.</td><td>Modelo MBSE genérico de la arquitectura del EPS y figura de arquitectura funcional.</td><td>Obj.3</td></tr><tr><td>5</td><td>Estructurar la verificación temprana de requisitos del EPS.</td><td>Para reducir la fragmentación entre requisitos, arquitectura,</td><td>Se elaborará un catálogo de métodos de verificación por requisito, matrices de trazabilidad y</td><td>Paquete de verificación temprana con catálogo, matriz de trazabilidad, evidencias generadas o justificación de</td><td>Obj.4</td></tr></table>

<!-- PDF_PAGE: 12 -->

<table border="1"><tr><td>Etapa</td><td>Qué se hará</td><td>Por qué se hará</td><td>Cómo se hará</td><td>Evidencia que producirá</td><td>Objetivos asociados</td></tr><tr><td></td><td></td><td>análisis de potencia/energía y evidencia de revisión antes de disponer de hardware de vuelo.</td><td>listas de consistencia; también se realizarán análisis de potencia/energía, simulaciones y prototipado virtual ajustados a los datos disponibles.</td><td>brechas.</td><td></td></tr><tr><td>6</td><td>Aplicar y evaluar el marco en dos casos de estudio contrastantes, siempre que cuenten con datos suficientes.</td><td>Para comprobar si el marco puede producir evidencia trazable y comparable en más de un perfil de EPS sin afirmar validación física ni confiabilidad de vuelo.</td><td>Se instanciarán los artefactos del marco para cada caso, se documentarán parámetros y supuestos utilizados, se aplicarán los mismos criterios de trazabilidad y se comparará la evidencia obtenida.</td><td>Modelos especializados por caso e informe técnico de evaluación comparativa.</td><td>Obj.5</td></tr><tr><td>7</td><td>Revisar técnicamente y consolidar los resultados.</td><td>Para verificar claridad, utilidad académica, factibilidad y límites de la propuesta antes de la entrega final.</td><td>Se presentarán los artefactos al director académico o revisores académicos, se registrarán observaciones, se actualizarán decisiones, limitaciones, brechas y anexos reproducibles.</td><td>Informe técnico final, matrices, modelos, scripts o archivos de soporte, minutas de revisión y registro de decisiones.</td><td>Obj.1-5</td></tr></table>

<!-- PDF_PAGE: 13 -->

## Control de alcance y evidencias

Para mantener la factibilidad del proyecto, quedan fuera del alcance la construcción de hardware de vuelo, la validación ambiental y el diseño completo de la misión del nanosatélite. La simulación y el prototipado virtual serán actividades requeridas para generar evidencia trazable de la propuesta, con un nivel de detalle ajustado a los datos disponibles. El uso de hardware-in-the-loop, el desarrollo de un gemelo digital de alta fidelidad y el desarrollo de nuevos algoritmos autónomos para EPS (para el caso de estudio de alta autonomía) no forman parte del compromiso mínimo del proyecto, y por ello se evaluarán durante la ejecución si existe disponibilidad confirmada de datos, laboratorio, equipo y tiempo, y si aportan evidencia verificable frente a los indicadores. Para efectos de alcance, una alta fidelidad en el gemelo digital se entendería como una integración explícita de capas mecánica, térmica, electrónica del EPS y software de control, con representación funcional de elementos como seguimiento del punto máximo de potencia (Maximum Power Point Tracking, MPPT) y protección de sobrecorriente y sobrevoltaje (overcurrent and overvoltage protection, OCVP). Por tanto, cualquier prototipado virtual que no cubra esas capas se tratará como un modelo de menor fidelidad.

## Objetivo General

Desarrollar un marco de ingeniería de sistemas basada en modelos orientado al fortalecimiento de la justificación temprana del diseño de sistemas de potencia eléctrica de nanosatélites mediante evidencia trazable y reproducible.

## Objetivos Específicos

<!-- PDF_PAGE: 14 -->

<div align="center">

Tabla 2. Objetivos específicos, indicadores verificables y entregables técnicos.

</div>

<table border="1"><tr><td>Objetivo específico</td><td>Indicador verificable</td><td>Entregable técnico</td></tr><tr><td>Caracterizar las necesidades, restricciones, interfaces y criterios técnicos del EPS de nanosatélites.</td><td>Variable: cobertura de caracterización; condición de evaluación: revisión de la matriz frente a las fuentes documentales y comentarios técnicos recibidos; umbral: 100 % de necesidades, restricciones, interfaces y criterios registrados con fuente o justificación.</td><td>Matriz de necesidades, restricciones, interfaces y criterios técnicos del EPS.</td></tr><tr><td>Seleccionar el flujo operativo de modelado, análisis y gestión de evidencia del marco MBSE.</td><td>Variable: cobertura de categorías de decisión; condición de evaluación: revisión de la matriz ponderada de alternativas; umbral: 100 % de categorías candidatas documentadas con puntuación, restricción y decisión.</td><td>Registro de decisión del flujo operativo del marco MBSE.</td></tr><tr><td>Modelar la arquitectura genérica del EPS con funciones, componentes lógicos, interfaces, modos de operación y restricciones.</td><td>Variable: cobertura arquitectónica; condición de evaluación: inspección del modelo MBSE genético; umbral: 100 % de requisitos seleccionados vinculados con al menos un elemento arquitectónico.</td><td>Modelo MBSE genético de la arquitectura del EPS.</td></tr><tr><td>Estructurar la verificación temprana de requisitos del EPS dentro del marco MBSE.</td><td>Variable: cobertura de verificación temprana; condición de evaluación: revisión del catálogo de verificación y la matriz de trazabilidad; umbral: 100 % de requisitos seleccionados vinculados con un método de verificación.</td><td>Paquete de verificación temprana del EPS.</td></tr><tr><td>Evaluar el marco MBSE en dos casos de estudio contrastantes de EPS.</td><td>Variable: cobertura de aplicación del marco; condición de evaluación: revisión del informe de aplicación comparativa; umbral: 2 casos de estudio documentados con evidencia trazable, uno tradicional y otro de alta autonomía.</td><td>Informe técnico de evaluación comparativa del marco MBSE.</td></tr></table>

<!-- PDF_PAGE: 15 -->

## Enfoque de la solución

Dirección técnica y tipo de solución

El enfoque de la solución consiste en desarrollar un marco MBSE para la justificación temprana del diseño de EPS de nanosatélites, no un prototipo físico de vuelo ni el diseño completo de una misión espacial. El tipo de solución será un conjunto articulado de artefactos técnicos: matriz de necesidades, restricciones, interfaces y criterios; registro de decisión del flujo operativo; modelo MBSE genérico de arquitectura del EPS; paquete de verificación temprana; modelos, scripts o archivos de soporte cuando sean necesarios; y evaluación comparativa en dos casos de estudio.

El principio general de operación del marco será transformar entradas de contexto de misión y actores técnicos en requisitos verificables, vincular esos requisitos con una arquitectura funcional/lógica genérica del EPS, especializar la arquitectura para casos de estudio, ejecutar o justificar análisis tempranos de potencia/energía y consolidar evidencia trazable para revisión. Desde la perspectiva del EPS, la solución representa de forma genérica el flujo de energía eléctrica entre funciones de generación, almacenamiento, acondicionamiento, protección y distribución, junto con el flujo de información necesario para monitoreo, control, modos de operación, interfaces y verificación. No se fijan marcas, modelos, componentes comerciales ni topologías finales mientras no exista justificación derivada de los requisitos, datos de caso y matriz de decisión.

Dentro del flujo operativo, NVIDIA Omniverse [5] se considerará explícitamente como herramienta candidata para el prototipado virtual requerido de escenarios, interfaces y evidencias, siempre subordinada a la matriz de decisión. Su inclusión no implica selección definitiva ni compromiso de implementar hardware-in-the-loop o un gemelo digital de alta fidelidad.

<!-- PDF_PAGE: 16 -->

Como opciones iniciales de casos de estudio, se considerarán el EPS híbrido para CubeSats reportado por Torres et al. [6], el EPS autónomo validated experimentalmente por Ali et al. [7] y la fuente de alimentación CubeSat de código abierto presentada por Damkjar et al. [8]. Estas opciones se usarán como candidatas para contrastar perfiles de EPS tradicional, autónomo o abierto, pero la selección final permanece pendiente y deberá confirmarse con el director académico según disponibilidad de datos suficientes, pertinencia técnica y factibilidad temporal.

<!-- PDF_PAGE: 17 -->

<div align="center">

Tabla 3. Módulos de la solución y relación con el problema y los objetivos.

</div>

<table border="1"><tr><td>Módulo de la solución</td><td>Función dentro del marco</td><td>Relación con el problema y los objetivos</td></tr><tr><td>Caracterización del EPS</td><td>Organizar necesidades, restricciones, interfaces, criterios técnicos, fuentes y supuestos.</td><td>Atiende la fragmentación inicial de entradas técnicas y produce el entregable del Obj.1.</td></tr><tr><td>Selección del flujo operativo</td><td>Definir cómo se modelará, analizará y gestionará la evidencia, con herramientas subordinadas a criterios técnicos.</td><td>Evita decisiones guiadas por disponibilidad o preferencia de herramienta y produce el registro del Obj.2.</td></tr><tr><td>Modelo MBSE y arquitectura genérica</td><td>Representar funciones, componentes lógicos, interfaces, modos y restricciones del EPS.</td><td>Conecta requisitos con arquitectura para reducir pérdida de trazabilidad y produce el modelo del Obj.3.</td></tr><tr><td>Verificación temprana</td><td>Relacionar requisitos con métodos de verificación, análisis de potencia/energía, revisiones de consistencia y evidencias factibles.</td><td>Responde a la brecha de V&amp;V previa a pruebas físicas y produce el paquete del Obj.4.</td></tr><tr><td>Evaluación en casos de estudio</td><td>Aplicar el marco en dos casos contrastantes con datos suficientes y comparar la evidencia generada.</td><td>Permite valorar la utilidad del marco sin afirmar validación física ni confiabilidad de vuelo y produce el informe del Obj.5.</td></tr><tr><td>Gestión de evidencia y revisión</td><td>Mantener trazabilidad, decisiones, limitaciones, supuestos y comentarios técnicos recibidos.</td><td>Apoya la reproducibilidad, la revisión académica y la claridad de supuestos en todos los objetivos.</td></tr></table>

<!-- PDF_PAGE: 18 -->

## Arquitectura Funcional

La arquitectura funcional del marco se presenta en la Figura 2 y organiza los módulos principales que conectan el contexto de misión, los requisitos, el modelo MBSE, la arquitectura del EPS, la verificación temprana y la evidencia técnica. Dado que el alcance se centra en el diseño temprano del EPS, el flujo físico relevante es la energía eléctrica y el flujo técnico principal es la información. No se propone un flujo material de fabricación o ensamblaje.

<!-- PDF_PAGE: 19 -->

<div align="center">

Tabla 4. Módulos funcionales y flujos principales de la arquitectura funcional.

</div>

<table border="1"><tr><td>Módulo funcional</td><td>Función</td><td>Flujo principal</td></tr><tr><td>Entradas de contexto y actores</td><td>Recoger necesidades de misión, restricciones, interfaces, fuentes documentales e institucionales disponibles y comentarios técnicos de especialistas.</td><td>Información desde fuentes y actores hacia la gestión de requisitos.</td></tr><tr><td>Gestión de requisitos y criterios</td><td>Convertir entradas de contexto en requisitos seleccionados, criterios técnicos, supuestos y condiciones de evaluación.</td><td>Información estructurada hacia el repositorio MBSE, la arquitectura y la verificación.</td></tr><tr><td>Modelo/repositorio MBSE y trazabilidad</td><td>Mantener relaciones entre necesidades, requisitos, funciones, componentes lógicos, interfaces, análisis y evidencias.</td><td>Información bidireccional entre artefactos del marco y registros de decisión.</td></tr><tr><td>Gestión funcional de energía del EPS</td><td>Representar, en nivel funcional, generación, almacenamiento, acondicionamiento, protección, distribución y entrega de energía a cargas del nanosatélite.</td><td>Energía eléctrica desde funciones de generación/almacenamiento hacia acondicionamiento, protección, distribución y cargas; información de estado hacia supervisión.</td></tr><tr><td>Supervisión y modos de operación</td><td>Representar monitoreo, comandos, estados, modos de operación y respuestas ante restricciones o inconsistencias.</td><td>Información de telemetría, estado y control entre arquitectura EPS, requisitos, escenarios y verificación.</td></tr><tr><td>Especialización por caso de estudio</td><td>Instanciar requisitos, parámetros, interfaces, modos y supuestos según datos disponibles de cada caso.</td><td>Información del modelo genérico hacia modelos especializados; registro de limitaciones y ajustes del marco.</td></tr><tr><td>Verificación temprana y análisis</td><td>Relacionar requisitos con métodos de inspección, análisis, demostración, simulación o prueba limitada, según datos disponibles.</td><td>Información desde requisitos, arquitectura y parámetros hacia resultados de análisis de potencia/energía y matrices de trazabilidad.</td></tr><tr><td>Evidencia, revisión y salida del marco</td><td>Consolidar resultados, brechas, decisiones, limitaciones y valoración técnico-académica.</td><td>Información de resultados hacia informe comparativo, paquete de evidencias y refinamiento del modelo.</td></tr></table>

<!-- PDF_PAGE: 20 -->


![figure_002.png](Anteproyecto_Arguedas_Rodríguez_Anthony_José_images/figure_002.png)



<div align="center">

Figura 2. Arquitectura Funcional. Módulos y flujos del marco MBSE para EPS de nanosatélites.

</div>

## Validación esperada

La validación esperada comprobará el cumplimiento de los indicadores definidos para cada objetivo. No se plantea como validación de hardware de vuelo ni como demostración de confiabilidad orbital, sino que se limitará a revisar cobertura,

<!-- PDF_PAGE: 21 -->

trazabilidad, reproducibilidad y evidencia técnica temprana dentro de los datos disponibles.

<!-- PDF_PAGE: 22 -->

<div align="center">

Tabla 5. Validación esperada por objetivo.

</div>

<table border="1"><tr><td>Objetivo asociado</td><td>Variable y condición de evaluación</td><td>Método o instrumento</td><td>Criterio de aceptación</td><td>Evidencia esperada</td></tr><tr><td>Obj.1: caracterización</td><td>Cobertura de necesidades, restricciones, interfaces y criterios frente a fuentes documentales y comentarios técnicos recibidos.</td><td>Matriz de caracterización, referencias, identificadores de fuente, revisión con director académico o revisores académicos.</td><td>100% de necesidades, restricciones, interfaces y criterios registrados con fuente, justificación o supuesto explícito.</td><td>Matriz revisada y lista de observaciones o ajustes.</td></tr><tr><td>Obj.2: flujo operativo</td><td>Cobertura de categorías candidatas de modelado, análisis y gestión de evidencia.</td><td>Matriz ponderada de alternativas y registro de decisión.</td><td>100% de categorías candidatas documentadas con puntuación, restricción y decisión.</td><td>Registro de decisión aprobado o revisado, con restricciones de disponibilidad y licenciamiento.</td></tr><tr><td>Obj.3: arquitectura genérica</td><td>Cobertura arquitectónica de los requisitos seleccionados.</td><td>Inspección del modelo MBSE genérico, matriz requisito-función-elemento lógico-interfaz.</td><td>100% de requisitos seleccionados vinculados con al menos un elemento arquitectónico.</td><td>Modelo MBSE genérico y matriz de trazabilidad arquitectónica.</td></tr><tr><td>Obj.4: verificación temprana</td><td>Cobertura de verificación de los requisitos seleccionados.</td><td>Catálogo de métodos de verificación, matriz de trazabilidad, análisis de potencia/energía, simulaciones y prototipado virtual.</td><td>100% de requisitos seleccionados vinculados con un método de verificación; cuando exista una restricción numérica por caso, el resultado deberá compararse con esa restricción o documentar la brecha.</td><td>Paquete de verificación temprana con resultados, brechas, supuestos y evidencias enlazadas.</td></tr><tr><td>Obj.5: evaluación en casos</td><td>Cobertura de aplicación del marco en dos casos de estudio contrastantes.</td><td>Protocolo de aplicación, modelos especializados, matrices por caso, informe comparativo y revisión técnico-académica.</td><td>2 casos de estudio documentados con evidencia trazable utilizando el modelo genérico y el flujo operativo ya aprobados. Un caso será tradicional y el otro de alta autonomía.</td><td>Informe técnico de evaluación comparativa, comentarios de revisión y registro de limitaciones.</td></tr></table>

<!-- PDF_PAGE: 23 -->

Además de los criterios anteriores, se documentarán las decisiones que permanezcan abiertas durante la ejecución: selección final de los dos casos de estudio, conjunto de requisitos trazables, pesos y categorías de la matriz de decisión, herramientas concretas, criterios de aceptación por caso y formato de publicación o anexado de modelos, scripts y parámetros. La simulación y el prototipado virtual forman parte del alcance previsto porque aportan evidencia trazable para la justificación temprana del EPS. En cambio, el uso de hardware-in-the-loop y el desarrollo de un gemelo digital de alta fidelidad quedarán abiertos a consideración, conditionados a disponibilidad técnica, datos suficientes y aporte verificable a los indicadores. La revisión técnico-académica mínima será realizada por el Dr. Jesús David González Llorente, y podrán incorporarse consultas puntuales a otros especialistas si el alcance técnico lo requiere.

## Cronograma

El cronograma se plantea para una pasantía de investigación en la ÉTS con alta carga de modelado, análisis, revisión bibliográfica y validación técnico-académica. Las fechas son orientativas, y están inspiradas en el calendario oficial del curso de Proyecto Final de Graduación y a las revisiones acordadas con el director académico. El periodo formal de pasantía en la ÉTS comprende del 4 de agosto de 2026 al 1 de diciembre de 2026. Las actividades de junio y julio corresponden a preparación previa y formalización del anteproyecto ante la universidad de origen, y cualquier consolidación posterior al 1 de diciembre se entiende como cierre documental o académico del proyecto final de graduación (PFG) de cara a la defensa final, no como actividad adicional de pasantía.

## Lista de actividades

Para cada objetivo específico se proponen actividades numeradas que permiten construir el cronograma y verificar el avance mediante productos concretos. Además, se incorpora una actividad transversal de redacción del informe desde la

<!-- PDF_PAGE: 24 -->

primera semana del cronograma hasta el cierre documental, para evidenciar el seguimiento continuo solicitado por la rúbrica.

<div align="center">

Tabla 6. Lista de actividades del cronograma.

</div>

<table border="1"><tr><td>Objetivo específico</td><td>Actividad</td></tr><tr><td>1. Caracterizar las necesidades, restricciones, interfaces y criterios técnicos del EPS de nanosatélites.</td><td>1.1 Consolidar fuentes documentales y antecedentes técnicos sobre EPS, MBSE, nanosatélites y V&amp;V temprana.</td></tr><tr><td>1. Caracterizar las necesidades, restricciones, interfaces y criterios técnicos del EPS de nanosatélites.</td><td>1.2 Identificar actores técnicos, frontera del EPS, necesidades de misión, funciones del EPS, interfaces, restricciones de potencia/energía, supuestos y requisitos iniciales.</td></tr><tr><td>1. Caracterizar las necesidades, restricciones, interfaces y criterios técnicos del EPS de nanosatélites.</td><td>1.3 Definir criterios técnicos, con pesos relativos o prioridad justificada según impacto y factibilidad.</td></tr><tr><td>1. Caracterizar las necesidades, restricciones, interfaces y criterios técnicos del EPS de nanosatélites.</td><td>1.4 Elaborar la matriz de necesidades, restricciones, interfaces y criterios técnicos, con fuente, justificación o supuesto explícito.</td></tr><tr><td>2. Seleccionar el flujo operativo de modelado, análisis y gestión de evidencia del marco MBSE.</td><td>2.1 Identificar alternativas por categoría: lenguaje de modelado, herramienta MBSE, análisis/programación, visualización y gestión de evidencia.</td></tr><tr><td>2. Seleccionar el flujo operativo de modelado, análisis y gestión de evidencia del marco MBSE.</td><td>2.2 Evaluar alternativas mediante matriz ponderada, considerando disponibilidad, licenciamiento, interoperabilidad, trazabilidad y tiempo de aprendizaje.</td></tr><tr><td>2. Seleccionar el flujo operativo de modelado, análisis y gestión de evidencia del marco MBSE.</td><td>2.3 Seleccionar el flujo operativo preliminar y documentar restricciones, supuestos y justificación de la decisión.</td></tr><tr><td>2. Seleccionar el flujo operativo de modelado, análisis y gestión de evidencia del marco MBSE.</td><td>2.4 Revisar la decisión con el director académico y ajustar el alcance técnico si alguna herramienta no resulta factible.</td></tr><tr><td>3. Modelar la arquitectura genérica del EPS con funciones, componentes lógicos, interfaces, modos de operación y restricciones.</td><td>3.1 Definir la descomposición funcional del EPS y sus modos principales de operación.</td></tr><tr><td>3. Modelar la arquitectura genérica del EPS con funciones, componentes lógicos, interfaces, modos de operación y restricciones.</td><td>3.2 Modelar componentes lógicos, interfaces, restricciones y relaciones con requisitos seleccionados.</td></tr><tr><td>3. Modelar la arquitectura genérica del EPS con funciones, componentes lógicos, interfaces, modos de operación y restricciones.</td><td>3.3 Revisar consistencia, modularidad, independencia tecnológica y trazabilidad inicial del modelo genérico.</td></tr><tr><td>4. Estructurar la verificación temprana de requisitos del EPS dentro del</td><td>4.1 Definir el catálogo de métodos de verificación temprana por inspección, análisis, demostración, simulación o prueba limitada,</td></tr></table>

<!-- PDF_PAGE: 25 -->

<table border="1"><tr><td>Objetivo específico</td><td>Actividad</td></tr><tr><td>marco MBSE.</td><td>según los datos y medios disponibles.</td></tr><tr><td>4. Estructurar la verificación temprana de requisitos del EPS dentro del marco MBSE.</td><td>4.2 Construir matrices de trazabilidad entre necesidades, requisitos, arquitectura, análisis y evidencias.</td></tr><tr><td>4. Estructurar la verificación temprana de requisitos del EPS dentro del marco MBSE.</td><td>4.3 Ejecutar análisis de potencia/energía, simulaciones, prototipado virtual o revisiones de consistencia, y justificar brechas según datos disponibles.</td></tr><tr><td>4. Estructurar la verificación temprana de requisitos del EPS dentro del marco MBSE.</td><td>4.4 Revisar la cobertura de verificación, brechas de evidencia y criterios de aceptación.</td></tr><tr><td>5. Evaluar el marco MBSE en dos casos de estudio contrastantes de EPS.</td><td>5.1 Definir el protocolo de aplicación del marco en casos de estudio.</td></tr><tr><td>5. Evaluar el marco MBSE en dos casos de estudio contrastantes de EPS.</td><td>5.2 Confirmar dos casos de estudio con datos disponibles suficientes, uno tradicional y otro de alta autonomía.</td></tr><tr><td>5. Evaluar el marco MBSE en dos casos de estudio contrastantes de EPS.</td><td>5.3 Aplicar el marco a cada caso y documentar requisitos, parámetros, interfaces y supuestos especializados.</td></tr><tr><td>5. Evaluar el marco MBSE en dos casos de estudio contrastantes de EPS.</td><td>5.4 Comparar la aplicación del marco en los dos casos de estudio mediante métricas de trazabilidad, reproducibilidad, integración y evidencia generada.</td></tr><tr><td>5. Evaluar el marco MBSE en dos casos de estudio contrastantes de EPS.</td><td>5.5 Recopilar revisión técnico-académica del director académico y, si corresponde, de expertos consultados sobre utilidad, claridad y factibilidad del marco.</td></tr><tr><td>5. Evaluar el marco MBSE en dos casos de estudio contrastantes de EPS.</td><td>5.6 Documentar limitaciones, riesgos residuales, lecciones aprendidas y oportunidades de mejora.</td></tr><tr><td>5. Evaluar el marco MBSE en dos casos de estudio contrastantes de EPS.</td><td>5.7 Consolidar informe técnico, modelos, matrices, scripts y anexos para entrega final.</td></tr><tr><td>Actividad transversal de seguimiento documental.</td><td>T.1 Redactar y actualizar continuamente el informe, los anexos y la bitácora de cambios del PFG desde la semana 1 hasta el cierre documental.</td></tr></table>

## Diagrama de Gantt

Tomando como referencia las actividades anteriores, el diagrama de Gantt utiliza los códigos de actividad como unidad principal de seguimiento e incluye la actividad transversal T.1 para la redacción continua del informe.

<!-- PDF_PAGE: 26 -->

<div align="center">

Tabla 7. Diagrama de Gantt del proyecto.

</div>

<table border="1"><tr><td>Código</td><td>Actividad resumida</td><td>Jun.2026</td><td>Jul.2026</td><td>Ago.2026</td><td>Sep.2026</td><td>Oct.2026</td><td>Nov.2026</td><td>Dic.2026</td><td>Producto de control</td></tr><tr><td>T.1</td><td>Redacción continua del informe, anexos y seguimiento documental.</td><td>10-30</td><td>01-31</td><td>04-31</td><td>01-30</td><td>01-31</td><td>01-30</td><td>01-04</td><td>Versiones semanales del informe, bitácora de cambios y anexos actualizados.</td></tr><tr><td>1.1</td><td>Consolidación de fuentes documentales y antecedentes técnicos.</td><td>10-30</td><td>01-31</td><td></td><td></td><td></td><td></td><td></td><td>Base documental y referencias priorizadas.</td></tr><tr><td>1.2</td><td>Identificación de actores, frontera, necesidades, interfaces, restricciones y requisitos iniciales.</td><td></td><td></td><td>10-21</td><td></td><td></td><td></td><td></td><td>Borrador de necesidades, supuestos y requisitos.</td></tr><tr><td>1.3</td><td>Definición y priorización de criterios técnicos.</td><td></td><td></td><td>17-28</td><td></td><td></td><td></td><td></td><td>Criterios priorizados y pesos preliminares.</td></tr><tr><td>1.4</td><td>Matriz de necesidades, restricciones, interfaces y criterios técnicos con trazabilidad de fuente.</td><td></td><td></td><td>24-31</td><td></td><td></td><td></td><td></td><td>Matriz revisable del objetivo 1 con fuente, justificación o supuesto.</td></tr><tr><td>2.1</td><td>Identificación de alternativas por categoría de herramienta.</td><td></td><td></td><td>17-21</td><td></td><td></td><td></td><td></td><td>Lista de alternativas candidatas.</td></tr><tr><td>2.2</td><td>Evaluación ponderada de alternativas.</td><td></td><td></td><td>24-31</td><td></td><td></td><td></td><td></td><td>Matriz de decisión.</td></tr><tr><td>2.3</td><td>Selección del flujo operativo preliminar.</td><td></td><td></td><td>28-31</td><td></td><td></td><td></td><td></td><td>Registro de decisión técnica.</td></tr><tr><td>2.4</td><td>Revisión y ajuste de la selección con el director académico.</td><td></td><td></td><td>29-31</td><td></td><td></td><td></td><td></td><td>Decisión revisada o plan alternativo.</td></tr><tr><td>3.1</td><td>Descomposición funcional del EPS y modos de operación.</td><td></td><td></td><td>24-31</td><td>01-04</td><td></td><td></td><td></td><td>Funciones y modos definidos.</td></tr><tr><td>3.2</td><td>Modelado de componentes lógicos, interfaces y restricciones.</td><td></td><td></td><td></td><td>01-18</td><td></td><td></td><td></td><td>Modelo genérico preliminar.</td></tr><tr><td>3.3</td><td>Revisión de consistencia, modularidad y trazabilidad inicial.</td><td></td><td></td><td></td><td>14-25</td><td></td><td></td><td></td><td>Modelo genérico revisado.</td></tr><tr><td>4.1</td><td>Catálogo de métodos de verificación temprana.</td><td></td><td></td><td></td><td>28-30</td><td>01-09</td><td></td><td></td><td>Catálogo de V&amp;V temprana.</td></tr><tr><td>4.2</td><td>Matrices de trazabilidad entre requisitos, arquitectura y evidencias.</td><td></td><td></td><td></td><td></td><td>05-16</td><td></td><td></td><td>Matrices de trazabilidad.</td></tr></table>

<!-- PDF_PAGE: 27 -->

<table border="1"><tr><td>Código</td><td>Actividad resumida</td><td>Jun.2026</td><td>Jul.2026</td><td>Ago.2026</td><td>Sep.2026</td><td>Oct.2026</td><td>Nov.2026</td><td>Dic.2026</td><td>Producto de control</td></tr><tr><td>4.3</td><td>Análisis, simulaciones, prototipado virtual o revisiones de consistencia.</td><td></td><td></td><td></td><td></td><td>12-31</td><td>01-06</td><td></td><td>Resultados de análisis o brechas justificadas.</td></tr><tr><td>4.4</td><td>Revisión de cobertura y brechas de verificación.</td><td></td><td></td><td></td><td></td><td></td><td>02-13</td><td></td><td>Cobertura y brechas documentadas.</td></tr><tr><td>5.1</td><td>Protocolo de aplicación del marco en casos de estudio.</td><td></td><td></td><td></td><td>21-30</td><td>01-02</td><td></td><td></td><td>Protocolo de aplicación.</td></tr><tr><td>5.2</td><td>Confirmación de dos casos de estudio.</td><td></td><td></td><td></td><td>28-30</td><td>01-09</td><td></td><td></td><td>Casos seleccionados y datos mínimos disponibles.</td></tr><tr><td>5.3</td><td>Aplicación del marco a cada caso.</td><td></td><td></td><td></td><td></td><td>05-16</td><td></td><td></td><td>Modelos especializados por caso.</td></tr><tr><td>5.4</td><td>Comparación de resultados en los dos casos de estudio.</td><td></td><td></td><td></td><td></td><td>19-31</td><td>01-13</td><td></td><td>Informe comparativo preliminar.</td></tr><tr><td>5.5</td><td>Revisión técnico-académica del marco y resultados.</td><td></td><td></td><td></td><td></td><td></td><td>09-20</td><td></td><td>Comentarios o rúbrica de revisión.</td></tr><tr><td>5.6</td><td>Documentación de limitaciones y mejoras.</td><td></td><td></td><td></td><td></td><td></td><td>16-27</td><td></td><td>Limitaciones y trabajo futuro.</td></tr><tr><td>5.7</td><td>Consolidación de informe, modelos, matrices, scripts y anexos.</td><td></td><td></td><td></td><td></td><td></td><td>23-30</td><td>01-04</td><td>Entregables finales.</td></tr></table>

<!-- PDF_PAGE: 28 -->

Como criterio de control, cada actividad debe cerrar con un producto verificable y no solamente con avance de lectura o exploración. La actividad transversal T.1 deberá mantenerse activa desde la primera semana del cronograma hasta el cierre, con versiones acumulativas del informe y anexos como evidencia de seguimiento documental continuo. Las actividades administrativas de movilidad y trámites institucionales se gestionarán fuera del alcance técnico del cronograma. Las actividades de simulación y prototipado virtual deberán mantenerse subordinadas al objetivo principal y producir evidencia trazable dentro del calendario. El uso de hardware-in-the-loop, un gemelo digital de alta fidelidad o la exploración de nuevos algoritmos autónomos para EPS se mantendrán como posibilidad condicionada y se registrarán como limitación o trabajo futuro si no resulta factible.

## Uso de recursos

Para la ejecución del proyecto se utilizarán recursos humanos, técnicos, de información y de validación disponibles en la ÉTS y el TEC, así como recursos aportados por el estudiante.

En cuanto al recurso humano, el estudiante investigador será responsable de la revisión bibliográfica, modelo MBSE, análisis, programación de apoyo, documentación y preparación de entregables. El director académico en la ÉTS, Dr. Jesús David González Llorente, brindará orientación técnica, revisión técnico-académica del alcance, validación de decisiones y retroalimentación sobre sistemas espaciales, EPS y MBSE. Los revisores del TEC, el asesor y el jurado, verificarán el cumplimiento académico del anteproyecto y del reporte final del PFG. Cuando sea necesario, se realizarán consultas puntuales a especialistas en sistemas espaciales, potencia eléctrica, simulación o mecatrónica.

Sobre el recurso técnico y físico, se utilizará una computadora personal y, según disponibilidad y aprobación institucional, infraestructura de la ÉTS para trabajo académico, acceso a bibliotecas, repositorios, software institucional, estaciones de trabajo o laboratorios disponibles. Las herramientas de modelado, análisis,

<!-- PDF_PAGE: 29 -->

programación, visualización y gestión de evidencia se seleccionarán mediante matriz de decisión, priorizando alternativas libres, educativas o institucionales. No se contempla compra de hardware de vuelo ni fabricación de un prototipo físico del EPS.

Como recurso de información se utilizarán la revisión sistemática de literatura, publicaciones académicas sobre EPS de nanosatélites y diseños abiertos o validados [3], [6]–[8], documentación pública de casos CubeSat, referencias de OOSEM [4], guías de ingeniería de sistemas [9], documentación de SysML [10] y documentación de herramientas candidatas, incluidas las de visualización o prototipado virtual [5], además de normas, manuales o catálogos de verificación disponibles mediante la ÉTS, el TEC o fuentes abiertas.

Asimismo, como recurso de validación se contará con la validación temprana apoyada en matrices de trazabilidad, listas de verificación, revisión técnico-académica a cargo del Dr. Jesús David González Llorente, análisis de potencia/energía, simulaciones, prototipado virtual y documentación de evidencias. El uso de hardware-in-the-loop o de un gemelo digital de alta fidelidad se considerará únicamente si existe disponibilidad confirmada y si aporta evidencia trazable dentro del calendario.

## Presupuesto

Los montos se expresan en dólares canadienses (CAD) y corresponden al presupuesto técnico directo del proyecto. La estimación supone que se priorizarán herramientas libres, educativas o institucionales, y que no se fabricará hardware de vuelo ni se comprarán componentes espaciales.

<!-- PDF_PAGE: 30 -->

<div align="center">

Tabla 8. Presupuesto técnico directo del proyecto.

</div>

<table border="1"><tr><td>Descripción</td><td>Cantidad</td><td>Valor estimado por unidad</td><td>Subtotal</td><td>Disponible en ÉTS/TEC o por el estudiante actualmente</td></tr><tr><td>Software de MBSE, modelado y documentación técnica bajo modalidad libre, educativa o institucional.</td><td>1 conjunto</td><td>CAD 0</td><td>CAD 0</td><td>Sí; sujeto a selección mediante matriz de decisión.</td></tr><tr><td>Herramientas de programación, análisis y automatización para cálculos, matrices y generación de evidencias.</td><td>1 conjunto</td><td>CAD 0</td><td>CAD 0</td><td>Sí; se priorizará software abierto o institucional.</td></tr><tr><td>Equipo de cómputo personal y/o estaciones institucionales para modelado, análisis y redacción.</td><td>1 conjunto</td><td>CAD 0</td><td>CAD 0</td><td>Sí; computadora personal y recursos institucionales sujetos a disponibilidad y aprobación institucional.</td></tr><tr><td>Recursos computacionales adicionales, almacenamiento o accesorios menores, si se requieren.</td><td>1</td><td>CAD 200</td><td>CAD 200</td><td>Parcial; solo se adquirirán si se justifica técnicamente.</td></tr><tr><td>Recursos de laboratorio, emulación o consumibles menores no espaciales, si el director confirma su pertinencia.</td><td>1</td><td>CAD 150</td><td>CAD 150</td><td>Parcial; sujeto a disponibilidad de la ÉTS y aprobación del alcance.</td></tr><tr><td>Acceso a literatura, guías, normas y bases de datos institucionales.</td><td>1 conjunto</td><td>CAD 0</td><td>CAD 0</td><td>Sí; mediante la ÉTS, el TEC o fuentes abiertas.</td></tr><tr><td>Contingencia técnica menor para ajustes improvistos de documentación, almacenamiento o accesorios.</td><td>1</td><td>CAD 100</td><td>CAD 100</td><td>No; se utilizará solo si aparece una necesidad técnica justificada.</td></tr><tr><td>Total del presupuesto técnico directo</td><td></td><td></td><td>CAD 450</td><td></td></tr></table>

<!-- PDF_PAGE: 31 -->

El costo técnico directo del proyecto es viable porque la ejecución depende principalmente de tiempo de investigación, acceso institucional, modelado, análisis y revisión experta. Los costos personales de movilidad, alojamiento, alimentación, transporte local, seguros o trámites migratorios se manejarán en un presupuesto separado de manutención de la pasantía y no como parte principal del presupuesto técnico del PFG.

## Referencias

[1] École de technologie supérieure, "Département de génie aérospatial," Accedido:

12 may. 2026. [En línea]. Disponible en:

https://www.etsmtl.ca/etudier-a-lets/departements/departement-de-genie-aerospatial

[2] École de technologie supérieure, "Jesús David González Llorente," Accedido: 27 abr. 2026. [En línea]. Disponible en: https://www.etsmtl.ca/etudier-a-lets/corpsenseignant/jgonzalez-llorente

[3] I. F. Acero et al., "A Method for Validating CubeSat Satellite EPS Through Power Budget Analysis Aligned With Mission Requirements," IEEE Access, vol. 11, pp. 43316-43332, 2023, doi: 10.1109/ACCESS.2023.3271596.

[4] Lockheed Martin Corporation and INCOSE OOSEM Working Group, Object-Oriented Systems Engineering Method (OOSEM) Tutorial, 2006.

[5] NVIDIA, "NVIDIA Omniverse Documentation," Accedido: 22 may. 2026. [En línea]. Disponible en: https://docs.omniverse.nvidia.com/

[6] M. R. Torres, D. A. Coutinho, and E. C. V. Boas, "A Hybrid Electrical Power Subsystem for CubeSats: Design and Experimental Validation," IEEE Journal on

<!-- PDF_PAGE: 32 -->

Miniaturization for Air and Space Systems, vol. 6, no. 4, pp. 392-403, Dec. 2025 doi: 10.1109/JMASS.2025.3613723.

[7] H. Ali, A. Iqbal, A. M. Alatwi, et al., "Design and experimental validation of an autonomous electrical power system (EPS) for CubeSats," Scientific Reports, 2026, doi: 10.1038/s41598-026-51416-y.

[8] S. Damkjar, J. Zhu, B. F. Cockburn, and D. G. Elliott, "An Open-Source CubeSat Electrical Power Supply," IEEE Aerospace and Electronic Systems Magazine, vol. 41, no. 4, pp. 4-16, Apr. 2026, doi: 10.1109/MAES.2025.3638725.

[9] NASA, NASA Systems Engineering Handbook. National Aeronautics and Space Administration, 2016. [En línea]. Disponible en: https://www.nasa.gov/wp-content/uploads/2018/09/nasa systems engineering handbook 0.pdf

[10] Object Management Group, "Systems Modeling Language, Version 2.0," Accedido: 22 may. 2026. [En línea]. Disponible en: https://www.omg.org/spec/SysML/

<!-- PDF_PAGE: 33 -->

<div align="center">

# Carta de Aceptación por parte de la Empresa

</div>

23 de julio del 2026

Dr. -Ing. Carlos Adrián Salazar García

Coordinador de Proyectos de Graduación

Licenciatura en Ingeniería Mecatrónica

Instituto Tecnológico de Costa Rica

## Estimado Ingeniero:

Por este medio, me permito comunicarle que hemos aceptado al estudiante Anthony José Arguedas Rodríguez, cédula 208510418, carnet ITCR 2022218504, en nuestra empresa para realice el proyecto titulado Marco de Ingeniería de Sistemas Basada en Modelos para la Justificación Temprana del Diseño de Sistemas de Potencia Eléctrica en Nanosatélites, a realizarse en un lapso de 16 semanas calendario, a partir del inicio del II semestre lectivo 2026.

Hago de su conocimiento que hemos leído y aprobado la propuesta que nos ha presentado el Sr. Arguedas Rodríguez. Dicho documento cumple con los requerimientos de nuestra empresa y haremos todos los esfuerzos posibles por aportar los recursos necesarios para su exitosa conclusión.

Además, le informo que hemos recibido una copia del documento "Normas de Proyecto de Graduación para empresas" del programa de Licenciatura de Ingeniería Mecatrónica del Instituto Tecnológico de Costa Rica, en el cual se detallan todos los aspectos a considerar durante este proceso.

Atentamente,

<!-- PDF_PAGE: 34 -->

## Anexo B.

<div align="center">

# Hoja de Información del Proyecto

</div>

Datos del estudiante:

Nombre: Anthony José Arguedas Rodríguez

Cédula: 208510418 Carné ITCR: 2022218504

Dirección de su residencia: Calle Lapas, Ciudad Quesada, San Carlos, Alajuela,

Costa Rica

Teléfono de residencia: ninguno

Teléfono celular: +506 8378 9714

Correo electrónico personal: anthony_arguedas@outlook.com

Correo electrónico estudiante: antarguedas@estudiantec.cr

## Información del proyecto:

Informacion del proyecto:

Nombre del Proyecto: Marco de Ingeniería de Sistemas Basada en Modelos para la Justificacion Temprana del Diseño de Sistemas de Potencia Eléctrica en Nanosatélites

Informacion de la empresa:

Nombre: École de technologie supérieure

Actividad Principal: Educación superior

Zona: Le Sud-Ouest, Ville de Montréal, Québec, Canada

Dirección: 1100 Rue Notre Dame Ouest, Montréal, QC H3C 1K3, Canada

Teléfono: ninguno

## Información del encargado/asesor en la empresa:

Nombre: Jesús David González Llorente

Puesto que ocupa: Profesor

Departamento: Département de génie aérospatial

Profesión: Profesor, investigador en ingeniería aeroespacial

Grado académico: Ph.D.

Teléfono: ninguno

Correo electrónico: Jesus.Gonzalez@etsmtl.ca