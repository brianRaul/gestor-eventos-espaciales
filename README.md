# 🚀 Gestor de Eventos Espaciales - Planificador Inteligente de Eventos

## 📖 Descripción

El **Gestor de Eventos Espaciales** es una aplicación de escritorio desarrollada en Python para la planificación inteligente de eventos aeroespaciales. Este sistema permite gestionar recursos limitados, validar restricciones complejas y evitar conflictos de programación en operaciones como lanzamientos de cohetes, pruebas de motores, simulaciones de aterrizaje y más.

La aplicación garantiza que los recursos no se asignen a más de un evento simultáneamente y que se respeten todas las reglas de co-requisitos y exclusiones definidas para cada tipo de evento.

---

## 🏗️ Arquitectura Basada en Clases - La Ventaja de `GestorEventos`

### **Diseño Orientado a Objetos con Clase Principal**

La aplicación está estructurada alrededor de la clase principal `GestorEventos`, que hereda de `customtkinter.CTk`. Este diseño ofrece importantes ventajas:

#### **1. Encapsulación y Organización**
- **Estado Centralizado**: Todos los datos de la aplicación (eventos planificados, recursos, configuraciones) están encapsulados dentro de una sola instancia de `GestorEventos`
- **Evita Variables Globales**: Elimina el uso de variables globales, reduciendo errores y facilitando el mantenimiento
- **Ciclo de Vida Controlado**: La inicialización, ejecución y cierre están completamente gestionados por la clase

#### **2. Coherencia y Mantenibilidad**
- **Métodos Especializados**: Cada funcionalidad tiene su método dedicado (`crear_evento`, `eliminar_eventos`, `ver_combustible`, etc.)
- **Separación de Responsabilidades**: La interfaz gráfica está claramente separada de la lógica de negocio mediante módulos especializados
- **Facilidad de Extensión**: Nuevas funcionalidades se pueden agregar como nuevos métodos o módulos sin afectar el código existente

#### **3. Integración con el Sistema de Ventanas**
- **Ventana Principal Única**: `GestorEventos` actúa como la ventana principal de la aplicación
- **Gestión de Ventanas Secundarias**: Controla todas las ventanas emergentes (Toplevel) que se crean
- **Comunicación Centralizada**: Todas las partes de la aplicación acceden a los mismos datos a través de la instancia principal

#### **4. Sincronización Automática**
- **Patrón Observador Integrado**: La clase principal coordina la actualización de todas las ventanas abiertas
- **Datos Siempre Actualizados**: Cuando se realizan cambios (crear/eliminar eventos, modificar combustible), todas las ventanas abiertas se actualizan automáticamente
- **Registro de Ventanas**: Mantiene un registro de todas las ventanas abiertas para notificarles de cambios

---

## 🚀 Cómo Ejecutar el Programa

### **Requisitos Previos**

1. **Python 3.8 o superior** instalado en el sistema
2. **Acceso a línea de comandos** (Terminal en macOS/Linux, CMD o PowerShell en Windows)

### **Instalación de Dependencias**

```bash
# Instalar CustomTkinter (interfaz gráfica moderna)
pip install customtkinter

# Verificar instalación
python -c "import customtkinter; print('✅ CustomTkinter instalado correctamente')"
```

### **Estructura del Proyecto**

```
gestor_eventos_espaciales/
├── main.py                          # Punto de entrada - Clase GestorEventos
├── eventos_predeterminados.json     # Configuración de tipos de evento
├── recursos.json                    # Inventario de recursos disponibles
├── eventos_planificados.json        # Eventos creados (se genera automáticamente)
└── modulos/                         # Módulos de lógica de negocio
    ├── funciones_datos.py           # Carga/guardado de datos
    ├── funciones_crear_evento.py    # Lógica de creación de eventos
    ├── funciones_buscar_hueco.py    # Búsqueda de fechas disponibles
    ├── funciones_series_recurrentes.py # Gestión de series
    ├── logica_combustible.py        # Gestión de combustible
    ├── logica_eliminacion.py        # Eliminación con devolución
    ├── logica_serie.py              # Validación de series
    ├── logica_visualizaciones.py    # Visualizaciones de eventos
    ├── logica_recursos.py           # Gestión de recursos
    ├── logica_fechas.py             # Validación de fechas
    ├── logica_validaciones.py       # Validaciones generales
    └── logica_sincronizacion.py     # Sincronización de ventanas
```

### **Pasos para Ejecutar**

1. **Abrir terminal** en la carpeta del proyecto
2. **Ejecutar el archivo principal**:

```bash
python main.py
```

### **Comportamiento al Iniciar**

1. **Carga Automática de Datos**: 
   - Carga los tipos de evento desde `eventos_predeterminados.json`
   - Carga los recursos disponibles desde `recursos.json`
   - Carga eventos existentes desde `eventos_planificados.json` (si existe)

2. **Inicialización de la Interfaz**:
   - Crea la ventana principal con tamaño fijo (675x975 píxeles)
   - Configura todos los elementos de la interfaz
   - Inicializa el sistema de sincronización de ventanas

3. **Aplicación Lista**:
   - La ventana principal se muestra centrada en pantalla
   - El contador de eventos se actualiza automáticamente
   - Los recursos se cargan en el panel de selección

---

## 🔗 Conexión entre Funciones y Módulos

### **Flujo de Datos y Control**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLASE GestorEventos (main.py)                 │
├─────────────────────────────────────────────────────────────────┤
│  Interfaz Gráfica          │     Gestión de Estado              │
│  • crear_interfaz()        │     • eventos_planificados         │
│  • lbl_info, btn_crear     │     • recursos                     │
│  • combo_evento, etc.      │     • tipos_evento_data            │
└─────────────┬──────────────────────────────┬────────────────────┘
              │                              │
              ▼                              ▼
    ┌──────────────────┐          ┌────────────────────────┐
    │  Módulos de UI   │          │  Módulos de Lógica     │
    │  • logica_       │          │  • funciones_crear_    │
    │    visualizaciones│          │    evento.py          │
    │  • logica_       │          │  • funciones_series_   │
    │    recursos       │          │    recurrentes.py     │
    └──────────────────┘          └────────────────────────┘
              │                              │
              └──────────────┬───────────────┘
                             │
                             ▼
               ┌────────────────────────────┐
               │   Sistema de Sincronización │
               │   • logica_sincronizacion.py│
               │   • Actualiza ventanas      │
               │     automáticamente         │
               └────────────────────────────┘
```

### **Conexiones Clave entre Componentes**

#### **1. Creación de Eventos**
```
Interfaz → main.py.crear_evento() → funciones_crear_evento.procesar_creacion_evento()
         ↓
logica_validaciones → logica_recursos → funciones_buscar_hueco
         ↓
Resultado → Actualiza estado → Guarda JSON → Notifica cambios
```

#### **2. Gestión de Recursos**
```
Checkboxes → main.py.crear_checkboxes_recursos() → logica_recursos.obtener_recursos_por_categoria()
          ↓
Selección → logica_recursos.obtener_recursos_recomendados() → tipos_evento_data
          ↓
Validación → logica_validaciones.validar_reglas_exclusion()
```

#### **3. Sincronización de Ventanas**
```
Evento de Cambio → main.py → logica_sincronizacion.notificar_cambio_*()
                 ↓
Registro de Ventanas → Actualización Automática → Recreación de Contenido
```

#### **4. Sistema de Combustible**
```
Estado de Combustible → logica_combustible.obtener_combustibles()
                     ↓
main.py.ver_combustible() → Ventana con datos actualizados
                     ↓
Consumo/Reposición → Actualización automática de todas las ventanas
```

### **Comunicación entre Módulos**

1. **main.py → Módulos de Lógica**: Llama funciones específicas pasando datos necesarios
2. **Módulos de Lógica → main.py**: Retornan resultados (éxito/error, datos procesados)
3. **Módulos entre sí**: Se importan y utilizan funciones especializadas
4. **Sistema de Sincronización**: Escucha cambios y notifica a todas las ventanas registradas

### **Flujo de una Operación Típica (Crear Evento)**

```
1. Usuario completa formulario en interfaz
2. main.py.crear_evento() captura los datos
3. Llama a funciones_crear_evento.procesar_creacion_evento()
4. Este módulo coordina validaciones con:
   - logica_validaciones (validaciones básicas)
   - logica_recursos (validación de recursos)
   - logica_fechas (validación de fechas)
   - funciones_buscar_hueco (disponibilidad)
5. Si todo es válido:
   - Consume recursos (combustible)
   - Crea estructura del evento
   - Retorna éxito a main.py
6. main.py:
   - Agrega evento a lista interna
   - Guarda en JSON
   - Notifica cambios al sistema de sincronización
   - Actualiza interfaz principal
   - Actualiza todas las ventanas abiertas
```

### **Beneficios de esta Arquitectura**

1. **Alta Cohesión**: Cada módulo tiene una responsabilidad clara
2. **Bajo Acoplamiento**: Los módulos se comunican a través de interfaces definidas
3. **Testabilidad**: Fácil probar cada módulo por separado
4. **Mantenibilidad**: Cambios en un módulo no afectan a los demás
5. **Escalabilidad**: Nuevas funcionalidades se agregan como nuevos módulos

---

## Características Principales

### **Planificación Inteligente**
- Creación de eventos individuales con validación en tiempo real
- Soporte para **series recurrentes** con intervalo personalizable
- Validación automática de fechas y duraciones (límite de 3 años)
- Sugerencia inteligente de la próxima fecha disponible

### 🔧 **Gestión Avanzada de Recursos**
- Inventario completo de recursos aeroespaciales (cohetes, plataformas, combustible, etc.)
- Recursos con cantidad (pools) y recursos únicos
- Control de stock de combustible con reposición manual
- Visualización del estado de combustible con alertas de nivel bajo

### ⚙️ **Sistema de Restricciones Completo**
- **Reglas de exclusión**: recursos que no pueden usarse juntos
- **Requisitos coexistentes**: recursos que deben asignarse simultáneamente
- Validación de disponibilidad considerando eventos solapados

### 🎨 **Interfaz Moderna e Intuitiva**
- Desarrollada con **CustomTkinter** para un aspecto profesional
- Panel de recursos agrupados por categorías
- Vista detallada de eventos planificados
- Feedback visual inmediato con colores e iconos

### 💾 **Persistencia Robusta**
- Guardado automático en formato JSON
- Carga automática al iniciar la aplicación
- Archivos separados para configuración, recursos y eventos

---

## **Estructura del Código**

### **Arquitectura Modular**
El sistema está organizado en módulos especializados para mantener una separación clara de responsabilidades:

```
main.py                          # Interfaz gráfica principal (CustomTkinter)
│
├── funciones_datos.py           # Carga y guardado de archivos JSON
├── funciones_crear_evento.py    # Lógica principal de creación de eventos
├── funciones_buscar_hueco.py    # Búsqueda de fechas disponibles
├── funciones_series_recurrentes.py # Gestión de series de eventos
│
├── logica_combustible.py        # Gestión de combustible
├── logica_eliminacion.py        # Eliminación de eventos con devolución
├── logica_serie.py              # Validación de series recurrentes
├── logica_visualizaciones.py    # Visualización de eventos y recursos
├── logica_recursos.py           # Gestión y validación de recursos
├── logica_fechas.py             # Validación y cálculo de fechas
└── logica_validaciones.py       # Validaciones generales
```

### **Flujo de Datos**
```
Interfaz Gráfica → Lógica de Negocio → Validaciones → Persistencia
      (main.py)    (módulos logica_*)   (validaciones)   (JSON files)
```

---

## 🔩 **Recursos del Sistema**

### **Categorías de Recursos**
El sistema gestiona **15 categorías de recursos** con múltiples unidades:

- **COHETE** (Pesado/Ligero) - Vehículos espaciales
- **PLATAFORMA DE LANZAMIENTO** (Estática/Móvil) - Bases de despegue
- **EQUIPO DE CONTROL** (Digital/Analógico) - Sistemas de control
- **SALA DE CONTROL PRINCIPAL** (Primaria/Secundaria) - Centros de operaciones
- **SISTEMA DE COMBUSTIBLE** (Líquido/Sólido) - Con cantidad en litros (POOL)
- **TORRE DE SERVICIO** (Retráctil/Fija) - Estructuras de soporte
- **SISTEMA DE SEGURIDAD** (Activa/Pasiva) - Sistemas de protección
- **ESTACIÓN DE SEGUIMIENTO** (Satelital/Terrestre) - Sistemas de monitoreo
- **SISTEMA DE NAVEGACIÓN** (GPS/Inercial) - Sistemas de guía
- **SISTEMA ELÉCTRICO** (Principal/Emergencia) - Fuentes de energía
- **SISTEMA DE CONTROL TÉRMICO** (Refrigerante/Aislante) - Control de temperatura
- **EQUIPO DE RECUPERACIÓN** (Aéreo/Terrestre) - Sistemas de recuperación
- **LABORATORIO DE PRUEBAS** (Químico/Físico) - Instalaciones de análisis
- **PLATAFORMA DE ATERRIZAJE** (Continental/Marítima) - Zonas de aterrizaje
- **EQUIPO DE COMUNICACIÓN** (Radio/Satelital) - Sistemas de comunicación

### **Tipos de Recursos**
Cada recurso tiene propiedades específicas:

- **Recursos únicos**: Equipos que no se consumen (torres, plataformas)
- **Recursos pool**: Múltiples unidades disponibles (cohetes, equipos de control)
- **Combustibles**: Recursos consumibles con cantidad (litros disponibles vs. total)

---

## 🚀 **Tipos de Eventos Disponibles**

La aplicación incluye **15 tipos de eventos aeroespaciales** preconfigurados, cada uno con:

1. **Recursos requeridos mínimos** - Obligatorios para el evento
2. **Reglas de exclusión** - Recursos que no pueden usarse
3. **Requisitos coexistentes** - Dependencias entre recursos
4. **Configuración de duración** - Mínimo y máximo de días

**Eventos disponibles:**
1. **Despegue de cohete** - Lanzamiento de cohete pesado
2. **Prueba estática de motor** - Prueba de motor con cohete ligero
3. **Simulación de aterrizaje** - Simulación en plataforma continental
4. **Aterrizaje del cohete** - Recuperación en plataforma marítima
5. **Carga de combustible** - Repostaje de combustible líquido
6. **Prueba de navegación avanzada** - Comparación GPS/inercial
7. **Prueba de sistemas eléctricos** - Verificación de sistemas principal/emergencia
8. **Prueba de control térmico** - Pruebas de refrigeración/aislamiento
9. **Ejercicio de recuperación** - Simulación de recuperación aérea/terrestre
10. **Análisis de laboratorio** - Pruebas químicas/físicas
11. **Prueba de propulsor sólido** - Prueba con combustible sólido
12. **Prueba de comunicaciones satelitales** - Comunicaciones vía satélite
13. **Mantenimiento de torre fija** - Mantenimiento especializado
14. **Prueba de comunicaciones por radio** - Comunicaciones UHF
15. **Prueba mixta combustible sólido-líquido** - Prueba con ambos combustibles

---

## 🧠 **Lógica Avanzada Implementada**

### **Validación de Fechas**
```python
# Validaciones implementadas:
1. Formato DD/MM/YYYY correcto
2. No fechas pasadas (>= hoy)
3. Límite de 3 años (1095 días desde hoy)
4. Días válidos según mes (incluye años bisiestos)
5. Duración dentro de límites del tipo de evento
6. Series no exceden 1 año de duración total
```

### **Validación de Recursos**
```python
# Para cada recurso seleccionado:
1. Verificar existencia en inventario
2. Comprobar reglas de exclusión (tipos prohibidos)
3. Validar requisitos coexistentes (dependencias)
4. Para combustible: cantidad disponible suficiente
5. Para equipos: unidades libres en fechas solicitadas
6. No solapamiento con otros eventos
```

### **Búsqueda de Huecos**
El algoritmo de búsqueda considera:
1. **Eventos existentes** y sus recursos asignados
2. **Disponibilidad por categoría y tipo** de recurso
3. **Stock de combustible** actual
4. **Límites temporales** (3 años máximo)
5. **Restricciones específicas** del tipo de evento

### **Gestión de Series Recurrentes**
- **Validación completa** antes de crear cualquier evento
- **Verificación de combustible** para toda la serie
- **Búsqueda de ventana completa** para series
- **Manejo de errores** por evento (si falla uno, se sugiere alternativa)

### **Eliminación con Devolución**
- **Equipos**: Liberados inmediatamente al inventario
- **Combustible**: Devuelto a tanques (hasta capacidad máxima)
- **Desperdicio**: Combustible excedente se pierde si tanque lleno
- **Integridad**: Los eventos eliminados se borran completamente

---

## 📁 **Archivos de Configuración**

### **`eventos_predeterminados.json`**
Define cada tipo de evento con estructura completa:
```json
{
  "Nombre del Evento": {
    "recursos_requeridos": [
      {"categoria": "CATEGORIA", "tipo": "TIPO", "cantidad": X, "descripcion": "..."}
    ],
    "reglas_exclusion": [
      {"categoria": "CATEGORIA", "tipos_prohibidos": ["TIPO1", "TIPO2"]}
    ],
    "requisitos_coexistentes": [
      {"categoria": "CATEGORIA", "tipo": "TIPO", "requiere": [...]}
    ],
    "configuracion_evento": {
      "duracion_minima": X,
      "duracion_maxima": Y
    }
  }
}
```

### **`recursos.json`**
Inventario con estructura jerárquica:
```json
{
  "recursos": {
    "CATEGORIA": [
      {
        "modelo": "NOMBRE",
        "tipo": "TIPO",
        "cantidad_total": X,
        "cantidad_disponible": Y  // Solo para combustible
      }
    ]
  }
}
```

### **`eventos_planificados.json`**
Almacena eventos creados con estructura unificada:
```json
[
  {
    "tipo": "Nombre del Evento",
    "fecha_inicio": "DD/MM/AAAA",
    "fecha_fin": "DD/MM/AAAA",
    "duracion_dias": X,
    "recursos": ["lista de nombres"],
    "recursos_detalle": [...],  // Estructura completa
    "recursos_usados": {...},   // Compatibilidad
    "recursos_consumidos": [...],
    "estado": "planificado"
  }
]
```
---

## 🎯 **Flujo de Trabajo Típico**

### **Crear Evento Individual**
1. **Seleccionar** tipo de evento → Carga recursos recomendados
2. **Introducir** fecha y duración → Validación automática
3. **Seleccionar** recursos → Validación de reglas
4. **Crear evento** → Consumo de recursos + guardado

### **Crear Serie Recurrente**
1. **Configurar** evento base (tipo, recursos, duración)
2. **Definir** recurrencia (intervalo, repeticiones)
3. **Validar** serie completa (combustible, disponibilidad)
4. **Crear serie** → Generación de múltiples eventos

### **Gestionar Conflictos**
1. **Error de solapamiento** → Usar "Sugerir fecha"
2. **Combustible insuficiente** → Usar "Rellenar todo"
3. **Recursos ocupados** → Buscar hueco automáticamente

---

## 🔍 **Ejemplos de Validaciones en Acción**

### **Ejemplo 1: Despegue de Cohete**
- **Requiere**: Cohete pesado, plataforma estática, control digital, 45,000L combustible líquido
- **Prohíbe**: Cohetes ligeros, plataformas móviles, combustible sólido
- **Dependencias**: Cohete pesado → requiere control digital + seguridad activa

### **Ejemplo 2: Prueba Mixta Combustible**
- **Requiere**: Combustible sólido + líquido, seguridad activa doble
- **Prohíbe**: Cualquier cohete, cualquier plataforma
- **Sentido**: Prueba de laboratorio que no involucra vehículos

### **Ejemplo 3: Serie de Pruebas**
- **Validación**: Verifica combustible para todos los eventos
- **Búsqueda**: Encuentra ventana de 30 días para 5 eventos
- **Creación**: Genera 5 eventos espaciados uniformemente

---

## ⚠️ **Límites y Restricciones del Sistema**

### **Límites Absolutos**
- **Planificación máxima**: 3 años (1095 días) desde hoy
- **Duración máxima de serie**: 1 año (365 días)
- **Eventos simultáneos**: Limitados por recursos disponibles
- **Combustible máximo**: Definido por capacidad de tanques

### **Restricciones de Diseño**
1. **No eventos pasados** → Evita inconsistencia temporal
2. **Validación completa antes de crear** → Previene estados inconsistentes
3. **Devolución parcial de combustible** → Simula pérdidas reales
4. **Recursos opcionales permitidos** → Flexibilidad en configuración

### **Consideraciones de Rendimiento**
- **Búsqueda lineal** en ventana de 3 años
- **Validación por recurso** en cada creación
- **Ordenamiento automático** de eventos por fecha
- **Actualización en tiempo real** de interfaces

---

## 🛠️ **Extensibilidad del Sistema**

### **Agregar Nuevos Tipos de Eventos**
1. Editar `eventos_predeterminados.json`
2. Definir recursos requeridos, exclusiones y dependencias
3. La aplicación cargará automáticamente al reiniciar

### **Agregar Nuevos Recursos**
1. Editar `recursos.json`
2. Añadir a categoría existente o crear nueva
3. Definir cantidad total (y disponible para combustible)

### **Modificar Restricciones**
1. Actualizar reglas en archivo JSON
2. El sistema aplicará nuevas validaciones inmediatamente

---

## 📝 **Notas de Implementación**

### **Decisiones de Diseño Clave**
1. **Estructura unificada de eventos**: Todos los eventos tienen mismos campos
2. **Validación por capas**: Errores se detectan temprano y claramente
3. **Mensajes de error específicos**: Indican exactamente qué corregir
4. **Persistencia inmediata**: Cambios se guardan automáticamente

### **Manejo de Errores**
- **Errores de validación**: Mensajes claros con emojis y colores
- **Errores de sistema**: Logs en consola + mensajes amigables
- **Errores de datos**: Carga segura con valores por defecto

### **Compatibilidad Hacia Atrás**
- **Eventos antiguos**: Compatibles con nueva estructura
- **Recursos obsoletos**: Marcados pero no eliminados
- **Configuraciones viejas**: Convertidas automáticamente

---

## 🎨 **Interfaz de Usuario**

### **Componentes Principales**
1. **Selector de eventos** → Lista desplegable con 15 tipos
2. **Panel de recursos** → Agrupado por categoría con colores
3. **Campos de fecha** → Validación en tiempo real
4. **Sección de recurrencia** → Para series de eventos
5. **Botones de acción** → Colores según función (verde=crear, rojo=eliminar)
6. **Área de información** → Mensajes de estado y errores

### **Feedback Visual**
- **✅ Verde**: Operación exitosa
- **❌ Rojo**: Error crítico (no se puede proceder)
- **🟠 Naranja**: Advertencia (acción posible)
- **🔍 Azul**: Búsqueda en progreso
- **⛽ Naranja combustible**: Niveles de combustible

### **Interacciones Clave**
- **Click en checkbox** → Selección/deselección de recurso
- **"Marcar Recomendados"** → Selección automática de recursos obligatorios
- **"Sugerir Fecha"** → Búsqueda inteligente de hueco
- **"Ver Recursos"** → Detalle completo por evento

---

## 🔮 **Futuras Mejoras Potenciales**

### **Mejoras de Funcionalidad**
1. **Exportación a calendario** (iCal, Google Calendar)
2. **Notificaciones por email** para eventos próximos
3. **Múltiples usuarios** con permisos diferentes
4. **Estadísticas y reportes** de uso de recursos

### **Mejoras Técnicas**
1. **API REST** para integración con otros sistemas
2. **Base de datos** en lugar de archivos JSON
3. **Interfaz web** además de desktop
4. **Sistema de plugins** para tipos de eventos personalizados

---

## 👨‍💻 **Autor**

**Brian Raúl López Pérez**

**¡Listo para ejecutar y usar!** 🚀