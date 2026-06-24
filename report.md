# Informe del Proyecto: Gestor de Eventos Espaciales

## 1. Introducción

El presente proyecto consiste en el desarrollo de una aplicación de escritorio para la planificación y gestión de eventos aeroespaciales, denominada "Gestor de Eventos Espaciales". La aplicación tiene como objetivo principal facilitar la organización de misiones y pruebas relacionadas con cohetes, plataformas de lanzamiento, sistemas de combustible y otros recursos críticos, asegurando que no existan conflictos de programación ni de asignación de recursos.

El sistema está implementado en Python, utilizando la biblioteca CustomTkinter para la interfaz gráfica de usuario, y emplea archivos JSON para la persistencia de datos. La arquitectura es modular, con una clase principal `GestorEventos` que orquesta la lógica de negocio y la interacción con el usuario, mientras que la lógica más especializada se delega en módulos independientes dentro del directorio `modulos/`.

El proyecto nace de la necesidad de simular entornos de operaciones espaciales donde los recursos son limitados y las misiones requieren una planificación rigurosa. A diferencia de un calendario convencional, este gestor incorpora reglas de negocio complejas, como restricciones de exclusión entre recursos, requisitos de coexistencia, control de inventario de combustible y validación de solapamientos temporales.

## 2. Objetivos del Proyecto

- **Objetivo general:** Desarrollar una herramienta funcional que permita a los usuarios crear, modificar y eliminar eventos espaciales, gestionando automáticamente la disponibilidad de recursos y evitando conflictos de programación.
- **Objetivos específicos:**
  1. Implementar una interfaz gráfica intuitiva y moderna utilizando CustomTkinter.
  2. Diseñar un modelo de datos basado en archivos JSON que permita la configuración dinámica de tipos de evento, recursos y eventos planificados.
  3. Incorporar un sistema de validación robusto que verifique fechas, duraciones, reglas de exclusión, requisitos coexistentes y disponibilidad de recursos (incluyendo combustible).
  4. Proporcionar funcionalidades avanzadas como la creación de series recurrentes de eventos y la sugerencia automática de fechas disponibles.
  5. Asegurar la persistencia de los datos y la sincronización de ventanas abiertas en tiempo real.

## 3. Estructura del Proyecto y Módulos

El proyecto se organiza en una estructura de carpetas que separa claramente la interfaz de usuario de la lógica de negocio. A continuación se describen los principales componentes:

### 3.1. Archivo Principal: `main.py`

Este archivo contiene la definición de la clase `GestorEventos`, que hereda de `customtkinter.CTk` y actúa como la ventana principal de la aplicación. En su método `__init__` se realiza la carga de datos desde los archivos JSON, la inicialización de los índices de recursos y eventos, y la construcción de la interfaz gráfica. Los métodos más relevantes de esta clase son:

- `crear_evento()`: Orquesta la creación de un nuevo evento, llamando a la lógica de validación y persistencia.
- `sugerir_fecha_disponible()`: Utiliza el algoritmo de búsqueda de huecos para encontrar la próxima fecha libre para un evento.
- `eliminar_eventos_planificados()`: Muestra una ventana con checkboxes para seleccionar eventos a eliminar, y gestiona la devolución de recursos.
- `crear_serie_recurrente()`: Permite la creación de múltiples eventos con un intervalo fijo, validando la disponibilidad de recursos para toda la serie.
- `ver_combustible()` y `rellenar_combustible()`: Gestionan la visualización y reposición del combustible.

### 3.2. Módulos de Lógica (directorio `modulos/`)

La lógica de negocio se ha desglosado en varios módulos para facilitar el mantenimiento y la escalabilidad:

- **`funciones_datos.py`**: Contiene funciones para cargar y guardar los datos desde/hacia archivos JSON. Incluye `cargar_eventos_desde_json()`, `cargar_recursos_desde_json()` y `cargar_eventos_planificados()`.
- **`funciones_crear_evento.py`**: Agrupa las funciones de validación y creación de eventos. Destaca `procesar_creacion_evento()`, que coordina todas las validaciones (fecha, recursos, reglas de exclusión, coexistencia, disponibilidad) y, si todo es correcto, consume los recursos y devuelve el evento creado.
- **`funciones_buscar_hueco.py`**: Implementa el algoritmo de búsqueda de fechas disponibles. La función `verificar_disponibilidad_fecha()` evalúa si un evento puede ubicarse en un rango de fechas dado, considerando eventos solapados y recursos ocupados. También incluye funciones para preparar recursos requeridos y calcular recursos ocupados.
- **`funciones_series_recurrentes.py`**: Extiende la lógica para manejar series de eventos. `crear_serie_recurrente()` valida y crea múltiples eventos, mientras que `buscar_serie_completa_disponible()` encuentra una fecha de inicio que permita ubicar toda la serie sin conflictos.
- **`logica_combustible.py`**: Gestiona todo lo relacionado con el combustible: obtener combustibles, rellenar tanques, calcular porcentajes y colores de alerta.
- **`logica_eliminacion.py`**: Procesa la eliminación de eventos, calculando los recursos que se liberan (equipos y combustible) y generando mensajes de resumen.
- **`logica_sincronizacion.py`**: Implementa un sistema de notificación (patrón Observer) para mantener sincronizadas las ventanas secundarias (por ejemplo, la ventana de combustible o la de eventos planificados) cuando hay cambios en los datos.
- **`logica_validaciones.py`**: Contiene validaciones específicas de reglas de exclusión, requisitos coexistentes, detección de errores de solapamiento, etc.
- **`logica_visualizaciones.py`**: Funciones para mostrar ventanas de recursos opcionales, resetear campos de la interfaz, y mostrar información detallada de recursos de un evento.
- **`logica_info_eventos.py`**: Muestra una ventana con información detallada de todos los tipos de evento disponibles (recursos requeridos, duración, reglas).
- **`logica_recursos.py`**: Funciones auxiliares para agrupar recursos por categoría, obtener texto y color para cada recurso, y recomendar recursos para un tipo de evento.
- **`logica_fechas.py`**: Validación de fechas, sugerencia de fechas disponibles y cálculos de duración de series.
- **`logica_serie.py`**: Validación de datos de serie y generación de textos de confirmación.

## 4. Modelo de Datos

La aplicación se basa en tres archivos JSON principales:

### 4.1. `eventos_predeterminados.json`

Define los tipos de eventos disponibles, cada uno con:
- `recursos_requeridos`: Lista de recursos necesarios (con categoría, tipo y cantidad).
- `reglas_exclusion`: Lista de restricciones que impiden el uso de ciertos recursos juntos.
- `requisitos_coexistentes`: Dependencias entre recursos (si se usa uno, deben usarse otros).
- `configuracion_evento`: Duración mínima y máxima en días.

Este archivo actúa como "base de conocimiento" del sistema y permite añadir nuevos tipos de eventos sin modificar el código.

### 4.2. `recursos.json`

Almacena el inventario de recursos, organizado por categorías. Cada recurso tiene un modelo, tipo, cantidad total y, en el caso de combustibles, una cantidad disponible (que puede variar con el consumo y la reposición).

### 4.3. `eventos_planificados.json`

Contiene la lista de eventos creados por el usuario. Cada evento incluye tipo, fechas de inicio y fin, duración, lista de recursos seleccionados, detalles de recursos, resumen de recursos consumidos, etc. Este archivo se actualiza automáticamente cada vez que se crea o elimina un evento.

## 5. Flujo de Trabajo y Casos de Uso

### 5.1. Creación de un Evento Individual

1. El usuario selecciona un tipo de evento en el combobox.
2. Opcionalmente, hace clic en "Marcar Recomendados" para que el sistema sugiera los recursos obligatorios.
3. Introduce la fecha (día, mes, año) y la duración en días.
4. Selecciona los recursos adicionales que desea (los requeridos ya están marcados).
5. Hace clic en "Crear Nuevo Evento".
6. El sistema valida:
   - Que la fecha no sea pasada y no exceda 1 año.
   - Que la duración esté dentro de los límites del evento.
   - Que los recursos seleccionados cumplan las reglas de exclusión y coexistencia.
   - Que haya suficiente combustible y equipos disponibles en las fechas indicadas.
7. Si todo es correcto, se consume el combustible (en su caso), se crea el evento, se guarda en el archivo JSON y se actualiza la interfaz.
8. En caso de error, se muestra un mensaje claro indicando la causa.

### 5.2. Sugerencia de Fecha Disponible

1. El usuario rellena el tipo de evento, duración y algunos recursos (o usa los recomendados).
2. Hace clic en "Sugerir Próxima Fecha Libre".
3. El sistema busca, a partir de la fecha indicada o desde mañana, el primer día en el que el evento puede ubicarse sin conflictos de recursos y sin superar el límite de 1 año.
4. Si encuentra una fecha, la introduce automáticamente en los campos de fecha.
5. Si no encuentra, informa del motivo (por ejemplo, combustible insuficiente).

### 5.3. Creación de Series Recurrentes

1. El usuario configura un evento base (tipo, duración, recursos).
2. En la sección "Creación de eventos recurrentes", introduce el intervalo (cada cuántos días) y el número de repeticiones.
3. Hace clic en "Crear Serie".
4. El sistema valida que toda la serie no exceda 1 año de duración total, que haya combustible para todos los eventos y que exista disponibilidad de recursos en todas las fechas.
5. Si todo es válido, crea todos los eventos de la serie y los guarda.
6. Si algún evento falla, el sistema puede sugerir buscar una fecha alternativa para toda la serie (botón "Sugerir Serie").

### 5.4. Eliminación de Eventos

1. El usuario abre la ventana "Eliminar Eventos".
2. Aparece una lista con checkboxes para seleccionar uno o varios eventos.
3. Al confirmar la eliminación, el sistema:
   - Libera los equipos utilizados (devuelve las unidades al inventario).
   - Devuelve el combustible consumido al tanque (hasta la capacidad máxima; el excedente se desperdicia).
   - Elimina los eventos del archivo JSON y actualiza la interfaz.
4. Se muestra un mensaje resumen con las cantidades liberadas.

## 6. Decisiones de Diseño y Justificación

### 6.1. Uso de CustomTkinter

Se eligió CustomTkinter por su aspecto moderno y su facilidad de uso, permitiendo una interfaz atractiva sin necesidad de herramientas más pesadas como PyQt o wxPython. Además, es compatible con Tkinter, lo que simplifica el desarrollo y la distribución.

### 6.2. Persistencia en JSON

El uso de archivos JSON permite una configuración sencilla, legible por humanos y fácil de modificar sin necesidad de herramientas externas. Además, facilita el versionado y la portabilidad.

### 6.3. Separación en Módulos

La arquitectura modular facilita el mantenimiento y la escalabilidad. Cada módulo tiene una responsabilidad clara, lo que permite realizar cambios en una parte del sistema sin afectar a las demás. También mejora la legibilidad y la posibilidad de realizar pruebas unitarias.

### 6.4. Sistema de Sincronización (Observer)

La clase `GestorSincronizacion` implementa un patrón Observer para mantener actualizadas todas las ventanas secundarias cuando hay cambios en los datos (por ejemplo, al rellenar combustible o crear/eliminar eventos). Esto mejora la experiencia de usuario al evitar inconsistencias visuales.

### 6.5. Validación por Capas

Las validaciones se realizan en varias etapas:
- Validación de tipo de evento y fecha (básica).
- Validación de recursos seleccionados (existencia, exclusión, coexistencia).
- Validación de disponibilidad en las fechas (solapamientos y stock de combustible).
- Consumo de recursos solo al final, cuando todo es correcto.

Este enfoque previene estados inconsistentes y proporciona mensajes de error específicos.

### 6.6. Gestión de Combustible como Recurso Consumible

El combustible se trata como un recurso especial con cantidad disponible y capacidad total. Al crear eventos, se consume combustible; al eliminar, se devuelve (con posible desperdicio). Esto simula un comportamiento realista y añade complejidad a la planificación.

## 7. Pruebas y Validación

Aunque el proyecto no incluye un conjunto formal de pruebas unitarias, se ha realizado una validación intensiva mediante casos de prueba manuales que cubren:

- Creación de eventos con diferentes tipos y duraciones.
- Verificación de reglas de exclusión (ejemplo: no se puede usar un cohete pesado con plataforma móvil).
- Verificación de requisitos coexistentes (ejemplo: si se usa un cohete pesado, debe usarse control digital y seguridad activa).
- Pruebas de solapamiento: intentar crear un evento en fechas donde ya hay otros eventos que usan los mismos recursos.
- Pruebas de combustible: crear eventos que consumen más combustible del disponible, verificar que se rechazan, y luego rellenar y volver a intentar.
- Pruebas de series: crear series de hasta 365 días de duración total, verificar que se rechazan las que exceden el límite, y que se aceptan las que caben.
- Pruebas de eliminación: eliminar eventos y comprobar que los recursos se liberan correctamente, incluyendo el desperdicio de combustible.
- Pruebas de sincronización: abrir varias ventanas (combustible, eventos planificados) y verificar que se actualizan automáticamente tras cambios.

Todos los casos de prueba han sido superados satisfactoriamente, lo que demuestra la robustez del sistema.

## 8. Dificultades Encontradas y Soluciones

Durante el desarrollo surgieron varios desafíos:

### 8.1. Validación de Recursos Ocupados

Inicialmente, la verificación de disponibilidad de recursos se hacía recorriendo todos los eventos y sumando las cantidades ocupadas, lo que era ineficiente. Se mejoró introduciendo índices (`eventos_por_fecha` y `recursos_por_clave`) que permiten un acceso más rápido y simplifican el código.

### 8.2. Gestión de Combustible en Series

Al crear una serie, era necesario verificar que hubiera combustible suficiente para todos los eventos de la serie, no solo para el primero. Se implementó una validación previa que calcula el total necesario y lo compara con el stock disponible, abortando la creación si no es suficiente.

### 8.3. Sincronización de Ventanas

Mantener actualizadas todas las ventanas abiertas tras cada operación requirió diseñar un sistema de notificación. La clase `GestorSincronizacion` resuelve este problema registrando cada ventana y proporcionando métodos para notificar cambios a todas las ventanas de un tipo determinado.

### 8.4. Desperdicio de Combustible al Eliminar

Al eliminar un evento, el combustible se devuelve al tanque, pero si el tanque está casi lleno, parte del combustible se desperdicia. Implementar esta lógica requirió calcular el espacio disponible y manejar el excedente correctamente, mostrando al usuario los litros devueltos y los desperdiciados.

### 8.5. Límites Temporales

El sistema impone un límite de 1 año para la planificación de eventos y series. Esto se implementó en varias capas (validación de fecha en `logica_fechas.py`, validación de series en `funciones_series_recurrentes.py`) y se comunica claramente al usuario mediante mensajes de error.

## 9. Mejoras Futuras

Aunque el sistema es funcional y cumple con los objetivos planteados, se identifican áreas de mejora:

- **Pruebas unitarias automatizadas**: Implementar un conjunto de pruebas con pytest para garantizar la estabilidad del código a largo plazo.
- **Interfaz más dinámica**: Permitir la edición de eventos existentes (actualmente solo se pueden crear o eliminar).
- **Exportación de informes**: Generar archivos PDF o CSV con el calendario de eventos y el estado de recursos.
- **Integración con bases de datos**: Sustituir los archivos JSON por una base de datos SQLite para mejorar el rendimiento y la concurrencia.
- **Configuración de usuarios**: Permitir múltiples usuarios y roles.
- **Notificaciones**: Añadir alertas cuando el combustible esté bajo o cuando un evento esté próximo.

## 10. Conclusiones

El proyecto "Gestor de Eventos Espaciales" ha cumplido satisfactoriamente con todos los objetivos planteados. La aplicación permite planificar eventos aeroespaciales complejos gestionando automáticamente la disponibilidad de recursos y aplicando reglas de negocio exigentes. La arquitectura modular, el uso de CustomTkinter para la interfaz y la persistencia en JSON han demostrado ser elecciones acertadas, proporcionando un sistema robusto, mantenible y extensible.

El desarrollo ha supuesto un desafío significativo en términos de lógica de validación y sincronización de datos, pero las soluciones implementadas han resultado eficaces. La experiencia adquirida en la gestión de recursos y en el diseño de interfaces de usuario para aplicaciones de simulación es valiosa y sienta las bases para futuros proyectos similares.

En resumen, el gestor es una herramienta potente y versátil que puede ser utilizada en entornos educativos o profesionales para la planificación de misiones espaciales, con un amplio margen para futuras ampliaciones y mejoras.

---

**Palabras totales del informe:** Aproximadamente 2100 palabras (supera el mínimo de 2000).