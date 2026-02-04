# 🚀 Gestor de Eventos Espaciales - Planificador Inteligente de Eventos

## 📖 Descripción

El **Gestor de Eventos Espaciales** es una aplicación de escritorio desarrollada en Python para la planificación inteligente de eventos aeroespaciales. Este sistema permite gestionar recursos limitados, validar restricciones complejas y evitar conflictos de programación en operaciones como lanzamientos de cohetes, pruebas de motores, simulaciones de aterrizaje y más.

La aplicación garantiza que los recursos no se asignen a más de un evento simultáneamente y que se respeten todas las reglas de co-requisitos y exclusiones definidas para cada tipo de evento.

---

## ✨ Características Principales

### ✅ **Planificación Inteligente**
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

## 🚀 **Instalación y Ejecución**

### **Requisitos Previos**
- **Python 3.8 o superior** ([Descargar Python](https://www.python.org/downloads/))
- **Sistema operativo**: Windows, macOS o Linux

### **Paso 1: Clonar o descargar el proyecto**
```bash
# Opción 1: Clonar con Git
git clone <tu-repositorio>
cd gestor-eventos-espaciales

# Opción 2: Descargar ZIP
# 1. Descarga el proyecto como ZIP desde GitHub
# 2. Descomprímelo en una carpeta de tu elección
# 3. Abre una terminal en esa carpeta
```

### **Paso 2: Instalar dependencias**
```bash
pip install customtkinter
```

### **Paso 3: Ejecutar la aplicación**
```bash
python main.py
```
**¡Importante!** Solo necesitas ejecutar `main.py`. La aplicación cargará automáticamente todos los datos necesarios.

### **Estructura mínima de archivos:**
```
gestor-eventos-espaciales/
├── main.py                    ← ¡EJECUTA ESTE ARCHIVO!
├── funciones_crear_evento.py
├── funciones_series_recurrentes.py
├── funciones_buscar_hueco.py
├── funciones_datos.py
├── eventos_predeterminados.json
├── recursos.json
├── eventos_planificados.json  ← Se crea automáticamente
└── README.md
```

### **Paso 4: Usar la aplicación**
1. La interfaz se abrirá automáticamente
2. Sigue las instrucciones en pantalla
3. ¡Comienza a planificar eventos espaciales!

---

## 📋 **Tipos de Eventos Disponibles**

La aplicación incluye **15 tipos de eventos aeroespaciales** preconfigurados:

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

## 🔩 **Recursos del Sistema**

El sistema gestiona **15 categorías de recursos** con múltiples unidades:

- **COHETE** (Pesado/Ligero)
- **PLATAFORMA DE LANZAMIENTO** (Estática/Móvil)
- **EQUIPO DE CONTROL** (Digital/Analógico)
- **SALA DE CONTROL PRINCIPAL** (Primaria/Secundaria)
- **SISTEMA DE COMBUSTIBLE** (Líquido/Sólido) ← Con cantidad en litros
- **TORRE DE SERVICIO** (Retráctil/Fija)
- **SISTEMA DE SEGURIDAD** (Activa/Pasiva)
- **ESTACIÓN DE SEGUIMIENTO** (Satelital/Terrestre)
- **SISTEMA DE NAVEGACIÓN** (GPS/Inercial)
- **SISTEMA ELÉCTRICO** (Principal/Emergencia)
- **SISTEMA DE CONTROL TÉRMICO** (Refrigerante/Aislante)
- **EQUIPO DE RECUPERACIÓN** (Aéreo/Terrestre)
- **LABORATORIO DE PRUEBAS** (Químico/Físico)
- **PLATAFORMA DE ATERRIZAJE** (Continental/Marítima)
- **EQUIPO DE COMUNICACIÓN** (Radio/Satelital)

---

## 🎮 **Guía Rápida de Uso**

### **Planificar un Evento Individual**
1. **Selecciona** un tipo de evento del menú desplegable
2. **Introduce** la fecha (día, mes, año) y duración en días
3. **Marca** los recursos necesarios (usa "✓ Marcar Recomendados" para selección automática)
4. **Haz clic** en "🚀 Crear Nuevo Evento"

### **Crear una Serie Recurrente**
1. Rellena fecha y duración
2. Especifica intervalo (en días) y número de repeticiones
3. Usa "🔍 Sugerir Serie" para encontrar fechas disponibles
4. Confirma con "🔄 Crear Serie"

### **Gestionar Eventos Existentes**
- **📋 Ver Eventos Planificados**: Muestra todos los eventos agendados
- **🗑️ Eliminar Eventos**: Elimina eventos seleccionados, liberando recursos
- **📦 Ver Recursos**: Detalla los recursos utilizados en cada evento

### **Gestionar Combustible**
- **📊 Ver Combustible**: Muestra niveles actuales de todos los tanques
- **⛽ Rellenar Todo**: Repone todos los tanques de combustible al máximo

### **Búsqueda Inteligente**
- **🔍 Sugerir Próxima Fecha Libre**: Encuentra automáticamente la próxima ventana disponible

---

## ⚙️ **Especificaciones Técnicas**

### **Límites del Sistema**
- **Planificación máxima**: 3 años (1095 días) hacia el futuro
- **Duración máxima de serie**: 1 año (365 días)
- **No se permiten** eventos en fechas pasadas
- **Validación completa** de fechas (días/meses válidos, años bisiestos)

### **Validaciones Implementadas**
```python
# Ejemplo de validaciones automáticas
1. Fechas válidas (formato DD/MM/AAAA)
2. No solapamiento de recursos
3. Combustible suficiente disponible
4. Cumplimiento de reglas de exclusión
5. Cumplimiento de co-requisitos
6. Límites de duración por tipo de evento
```

### **Arquitectura del Sistema**
```
Capa de Presentación (GUI) → main.py
         ↓
Capa de Lógica → funciones_*.py
         ↓
Capa de Datos → *.json
```

---

## 🛠️ **Solución de Problemas**

### **Problemas Comunes y Soluciones**

| Problema | Solución |
|----------|----------|
| **"Módulo customtkinter no encontrado"** | Ejecuta: `pip install customtkinter` |
| **"Archivo JSON no encontrado"** | Asegúrate de que todos los archivos .json están en la misma carpeta que main.py |
| **"Fecha inválida"** | Usa formato DD/MM/AAAA (ej: 15/04/2024) |
| **"Combustible insuficiente"** | Usa el botón **"⛽ Rellenar Todo"** para reponer tanques |
| **"Ocupado en esas fechas"** | Usa **"🔍 Sugerir Próxima Fecha Libre"** |
| **"La serie excede 1 año"** | Reduce el número de repeticiones o el intervalo |

### **Códigos de Error**
- **❌ Rojo**: Error crítico (no se puede crear el evento)
- **🟠 Naranja**: Advertencia (problema recuperable)
- **✅ Verde**: Operación exitosa
- **🔍 Azul**: Búsqueda en progreso

---

## 📁 **Archivos de Configuración**

### **`eventos_predeterminados.json`**
Define cada tipo de evento con:
- **recursos_requeridos**: Cantidades mínimas obligatorias
- **reglas_exclusion**: Recursos que no pueden usarse juntos
- **requisitos_coexistentes**: Recursos que deben usarse simultáneamente
- **configuracion_evento**: Duración mínima y máxima

### **`recursos.json`**
Contiene el inventario completo con:
- Cantidad total de cada recurso
- Para combustible: cantidad disponible actual
- Categorías y tipos organizados

### **`eventos_planificados.json`**
Almacena automáticamente todos los eventos creados con:
- Fechas de inicio y fin
- Recursos asignados con cantidades
- Estado de planificación

---

## 🔍 **Ejemplos de Restricciones**

### **Regla de Exclusión**
```json
{
  "categoria": "COHETE",
  "tipos_prohibidos": ["Ligero"]
}
```
→ Para un "Despegue de cohete", no se permite usar cohetes ligeros.

### **Requisito Coexistente**
```json
{
  "categoria": "COHETE",
  "tipo": "Pesado",
  "requiere": [
    {"categoria": "EQUIPO DE CONTROL", "tipo": "Digital"},
    {"categoria": "SISTEMA DE SEGURIDAD", "tipo": "Activa"}
  ]
}
```
→ Un cohete pesado siempre requiere control digital y seguridad activa.

---

## 🧠 **Lógica Avanzada Implementada**

### **Validación de Fechas**
- No se permiten eventos en el pasado
- Límite de planificación: 3 años (1095 días) hacia el futuro
- Límite de series: 1 año (365 días) de duración total
- Validación de días/meses válidos automática

### **Validación de Recursos**
- Combustible: Verifica cantidad disponible vs. requerida
- Equipos: Verifica disponibilidad en el rango de fechas
- Reglas de exclusión: Bloquea combinaciones prohibidas
- Co-requisitos: Exige recursos complementarios

### **Búsqueda de Huecos**
- Analiza eventos solapados
- Considera la disponibilidad de cada recurso
- Sugiere la próxima fecha disponible

---

## 🎨 **Detalles de la Interfaz**

La aplicación utiliza **CustomTkinter** con:
- **Tema oscuro** por defecto (configurable)
- **Widgets personalizados**: combobox, checkboxes con scroll, botones con iconos
- **Feedback visual**: colores según estado (verde=éxito, rojo=error, naranja=advertencia)
- **Actualización en tiempo real**: contador de eventos, estado de recursos

---

## 🏆 **Funcionalidades Avanzadas**

### ✅ **Recursos con Cantidad (Pools)**
- Los combustibles tienen cantidad disponible y cantidad total
- Los equipos tienen múltiples unidades disponibles
- El sistema verifica unidades libres, no solo presencia/ausencia

### ✅ **Planificación de Eventos Recurrentes**
- Series con intervalo personalizable
- Validación de toda la serie antes de crear
- Búsqueda de fechas disponibles para series completas

### ✅ **Gestión Completa de Combustible**
- Consumo automático al crear eventos
- Devolución al eliminar eventos
- Reposición manual con "Rellenar Todo"
- Alertas visuales cuando el nivel es crítico

### ✅ **Eliminación con Devolución**
- Al eliminar eventos, los recursos se devuelven al inventario
- Combustible regresa a los tanques (hasta capacidad máxima)
- Equipos quedan disponibles para otros eventos

---

## 📝 **Notas de Desarrollo**

### **Patrones de Diseño Implementados**
- **Modelo-Vista-Controlador (MVC)** implícito
- **Funciones puras** para validación y cálculo
- **Persistencia independiente** de la interfaz

### **Extensiones Futuras Posibles**
1. **Exportación a calendario** (iCal, Google Calendar)
2. **Notificaciones por email** para eventos próximos
3. **Múltiples usuarios** con permisos diferentes
4. **Estadísticas y reportes** de uso de recursos
5. **API REST** para integración con otros sistemas

---

## ❓ **Preguntas Frecuentes**

### **¿Puedo modificar los tipos de eventos?**
Sí, editando `eventos_predeterminados.json`. La aplicación cargará los cambios al reiniciar.

### **¿Cómo restauro el combustible?**
Usa el botón **"⛽ Rellenar Todo"** en la interfaz principal.

### **¿Puedo planificar más de 3 años?**
No, por diseño. El sistema limita la planificación a 3 años para mantener la precisión.

### **¿Qué pasa si cierro la aplicación?**
Todos los datos se guardan automáticamente. Al reabrirla, verás tus eventos planificados.

---

## 👨‍💻 **Autor**

**Brian Raúl López Pérez**

---

## 📄 **Licencia**

Este proyecto fue desarrollado como parte de un trabajo académico. Para uso educativo y demostración.

---

## 🎯 **Resumen Final**

Este **Gestor de Eventos Espaciales** es un sistema completo que demuestra:
- ✅ Planificación inteligente con restricciones complejas
- ✅ Interfaz gráfica profesional y usable
- ✅ Gestión avanzada de recursos con cantidades
- ✅ Persistencia robusta de datos
- ✅ Validaciones exhaustivas y manejo de errores

**¡Listo para ejecutar y usar!** 🚀