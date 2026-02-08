# logica_fechas.py
from datetime import datetime, date, timedelta


def sugerir_fecha_disponible_logica(
    tipo_evento,
    tipos_evento_data,
    day,
    month,
    year,
    duracion_str,
    eventos_planificados,
    recursos,
    preparar_recursos_requeridos_func,
    verificar_disponibilidad_fecha_func,
):

    # Lógica para sugerir una fecha disponible para un evento
    if tipo_evento not in tipos_evento_data:
        return None, "❌ Selecciona un evento primero", False

    try:
        duracion = int(duracion_str)
    except:
        duracion = 1

    # Obtener recursos requeridos para este evento
    evento_data = tipos_evento_data[tipo_evento]
    recursos_requeridos = evento_data.get("recursos_requeridos", [])

    # Usar función preparada para convertir recursos requeridos
    recursos_necesarios = preparar_recursos_requeridos_func(recursos_requeridos)

    # Empezar la búsqueda desde la fecha que el usuario puso, o desde mañana
    try:
        fecha_busqueda = date(int(year), int(month), int(day))

        # Si la fecha es en el pasado, empezar desde mañana
        if fecha_busqueda < date.today():
            fecha_busqueda = date.today() + timedelta(days=1)
    except:
        # Si no hay fecha válida, empezar desde mañana
        fecha_busqueda = date.today() + timedelta(days=1)

    # Límite de búsqueda: 3 años (1095 días)
    LIMITE_BUSQUEDA = 1095
    fecha_maxima = date.today() + timedelta(days=1095)

    # Variable para detectar si el error es de combustible
    error_combustible_detectado = False
    mensaje_combustible = ""

    for _ in range(LIMITE_BUSQUEDA):
        # Verificar que no excedamos el límite de 3 años
        if fecha_busqueda > fecha_maxima:
            break

        fecha_fin = fecha_busqueda + timedelta(days=duracion - 1)

        # Usar la función de disponibilidad externa
        disponible, mensaje_disponibilidad = verificar_disponibilidad_fecha_func(
            fecha_busqueda,
            fecha_fin,
            recursos_necesarios,
            eventos_planificados,
            recursos,
        )

        if disponible:
            return (
                fecha_busqueda,
                f"✅ Fecha disponible: {fecha_busqueda.strftime('%d/%m/%Y')} (dentro de los próximos 3 años)",
                False,
            )
        else:
            # VERIFICACIÓN CLAVE: Si el mensaje indica problema de combustible, guardar el error
            mensaje_lower = mensaje_disponibilidad.lower()
            if any(
                palabra in mensaje_lower
                for palabra in ["combustible", "fuel", "litro", "litros"]
            ):
                error_combustible_detectado = True
                mensaje_combustible = mensaje_disponibilidad
                # No rompemos el bucle, continuamos buscando

        # Pasar al siguiente día
        fecha_busqueda += timedelta(days=1)

    # Después de buscar en todas las fechas
    if error_combustible_detectado:
        return None, mensaje_combustible, True
    else:
        return None, "❌ No se encontró fecha disponible en los próximos 3 años", False


def validar_fecha_basica(
    day, month, year, duracion_str, tipo_evento=None, tipos_evento_data=None
):
    # Validación básica de fecha y duración sin dependencias de eventos planificados

    try:
        # PRIMERO: Verificar si algún número es demasiado grande
        if len(day) > 2 or len(month) > 2 or len(year) > 4 or len(duracion_str) > 4:
            return False, "❌ Fecha o duración inválida", None, None, None

        # Convertir duración
        duracion = int(duracion_str)

        # Validaciones normales que ya tenías
        if duracion <= 0:
            return False, "❌ La duración debe ser mayor a 0", None, None, None

        fecha_inicio = datetime(int(year), int(month), int(day))
        if fecha_inicio.date() < datetime.now().date():
            return False, "❌ No puedes planificar en el pasado", None, None, None

        LIMITE_FUTURO_DIAS = 1095
        fecha_maxima = datetime.now().date() + timedelta(days=LIMITE_FUTURO_DIAS)

        if fecha_inicio.date() > fecha_maxima:
            return (
                False,
                f"❌ No puedes planificar eventos a más de 3 años en el futuro",
                None,
                None,
                None,
            )

        fecha_fin = fecha_inicio + timedelta(days=duracion - 1)

        # Validar que el evento completo no exceda los 3 años
        if fecha_fin.date() > fecha_maxima:
            return (
                False,
                f"❌ El evento no puede terminar después de 3 años a partir de hoy",
                None,
                None,
                None,
            )

        # Si se proporciona tipo de evento, validar duración min/max
        if tipo_evento and tipos_evento_data and tipo_evento in tipos_evento_data:
            evento_data = tipos_evento_data[tipo_evento]
            config_evento = evento_data.get("configuracion_evento", {})
            d_min = config_evento.get("duracion_minima", 1)
            d_max = config_evento.get("duracion_maxima", 30)

            if not (d_min <= duracion <= d_max):
                return (
                    False,
                    f"❌ Duración permitida: {d_min}-{d_max} días",
                    None,
                    None,
                    None,
                )

        return True, "", fecha_inicio, fecha_fin, duracion

    except ValueError:
        return False, "❌ Fecha o duración inválida", None, None, None
    except OverflowError:
        return False, "❌ Fecha o duración inválida", None, None, None


def obtener_fechas_serie(fecha_inicio_str, duracion_dias, intervalo_dias, num_eventos):
    """
    Calcula las fechas para una serie de eventos recurrentes

    Retorna:
    - fechas_inicio: lista de fechas de inicio
    - fechas_fin: lista de fechas de fin
    - valido: True/False
    - mensaje: mensaje de error
    """
    try:
        fecha_inicial = datetime.strptime(fecha_inicio_str, "%d/%m/%Y").date()

        fechas_inicio = []
        fechas_fin = []

        fecha_temp = fecha_inicial
        for _ in range(num_eventos):
            fechas_inicio.append(fecha_temp)
            fecha_fin = fecha_temp + timedelta(days=duracion_dias - 1)
            fechas_fin.append(fecha_fin)
            fecha_temp += timedelta(days=intervalo_dias)

        return fechas_inicio, fechas_fin, True, ""
    except Exception as e:
        return [], [], False, f"❌ Error calculando fechas: {str(e)}"


def calcular_duracion_total_serie(duracion_dias, intervalo_dias, num_eventos):
    """
    Calcula la duración total de una serie de eventos
    """
    if num_eventos <= 0:
        return 0
    return (num_eventos - 1) * intervalo_dias + duracion_dias


def validar_limites_serie(
    duracion_dias,
    intervalo_dias,
    num_eventos,
    max_duracion_serie=365,
    max_planificacion=1095,
):
    """
    Valida que una serie de eventos cumpla con los límites establecidos
    """
    duracion_total = calcular_duracion_total_serie(
        duracion_dias, intervalo_dias, num_eventos
    )

    if duracion_total > max_duracion_serie:
        eventos_posibles = (max_duracion_serie - duracion_dias) // intervalo_dias + 1
        eventos_posibles = max(1, eventos_posibles)
        return False, f"❌ Serie demasiado larga (máximo {eventos_posibles} eventos)"

    # Verificar que toda la serie quepa dentro del límite de planificación
    hoy = date.today()
    fecha_inicio_simulada = hoy
    fecha_inicio_ultimo = fecha_inicio_simulada + timedelta(
        days=(num_eventos - 1) * intervalo_dias
    )
    fecha_fin_ultimo = fecha_inicio_ultimo + timedelta(days=duracion_dias - 1)

    if fecha_fin_ultimo > hoy + timedelta(days=max_planificacion):
        dias_disponibles = (hoy + timedelta(days=max_planificacion) - hoy).days
        eventos_posibles = 1
        if intervalo_dias > 0:
            eventos_posibles = min(
                num_eventos, (dias_disponibles // intervalo_dias) + 1
            )

        eventos_posibles = max(1, eventos_posibles)
        return False, f"❌ La serie excede 3 años (máximo {eventos_posibles} eventos)"

    return True, ""
