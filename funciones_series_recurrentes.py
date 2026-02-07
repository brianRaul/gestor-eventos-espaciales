from datetime import datetime, date, timedelta
from funciones_crear_evento import *
from funciones_buscar_hueco import *

def crear_serie_recurrente(
    tipo_evento,
    recursos_seleccionados_nombres,
    fecha_inicio_str,
    duracion_dias,
    intervalo_dias,
    num_eventos,
    recursos,
    eventos_planificados,
    tipos_evento_data,
    app=None,
):
    # 1. Validar que no sean números demasiado largos
    if (
        len(str(duracion_dias)) > 4
        or len(str(intervalo_dias)) > 4
        or len(str(num_eventos)) > 4
    ):
        return False, "❌ Número inválido", [], None

    # 2. Convertir fecha
    try:
        fecha_inicial = datetime.strptime(fecha_inicio_str, "%d/%m/%Y").date()
    except:
        return False, "❌ Fecha inválida", [], None

    # 3. Verificar que el intervalo no sea menor que la duración
    if num_eventos > 1 and intervalo_dias < duracion_dias:
        return (
            False,
            "❌ Intervalo menor que duración",
            [],
            None,
        )

    # 4. LÍMITES DE TIEMPO
    HOY = datetime.now().date()
    LIMITE_FUTURO_DIAS = 1095  # 3 años
    LIMITE_SERIE_DIAS = 365  # 1 año para la serie

    # Verificar que el primer evento no esté en el pasado
    if fecha_inicial < HOY:
        return False, "❌ No puedes planificar en el pasado", [], None

    # Verificar que el primer evento esté dentro de 3 años
    if fecha_inicial > HOY + timedelta(days=LIMITE_FUTURO_DIAS):
        return (
            False,
            f"❌ Fecha fuera de rango (máximo 3 años)",
            [],
            None,
        )

    # 5. Calcular fechas de la serie completa
    fecha_inicio_ultimo = fecha_inicial + timedelta(
        days=(num_eventos - 1) * intervalo_dias
    )
    fecha_fin_ultimo = fecha_inicio_ultimo + timedelta(days=duracion_dias - 1)
    duracion_total_serie = (fecha_fin_ultimo - fecha_inicial).days + 1

    # Verificar que la serie completa no exceda 1 año
    if duracion_total_serie > LIMITE_SERIE_DIAS:
        eventos_posibles = (LIMITE_SERIE_DIAS - duracion_dias) // intervalo_dias + 1
        eventos_posibles = max(1, eventos_posibles)

        return (
            False,
            f"❌ Serie demasiado larga (máximo {eventos_posibles} eventos)",
            [],
            None,
        )

    # 6. Verificar que toda la serie esté dentro de 3 años
    if fecha_fin_ultimo > HOY + timedelta(days=LIMITE_FUTURO_DIAS):
        # Calcular cuántos eventos caben en los 3 años
        dias_disponibles = (
            HOY + timedelta(days=LIMITE_FUTURO_DIAS) - fecha_inicial
        ).days
        eventos_posibles = 1
        if intervalo_dias > 0:
            eventos_posibles = min(
                num_eventos, (dias_disponibles // intervalo_dias) + 1
            )

        eventos_posibles = max(1, eventos_posibles)

        return (
            False,
            f"❌ Serie fuera de rango (máximo {eventos_posibles} eventos)",
            [],
            None,
        )

    # 7. Obtener datos del tipo de evento
    if tipo_evento not in tipos_evento_data:
        return False, "❌ Tipo de evento no encontrado", [], None

    evento_data = tipos_evento_data[tipo_evento]
    recursos_requeridos = evento_data.get("recursos_requeridos", [])

    # 8. VERIFICACIÓN DE CAPACIDAD MÁXIMA
    for req in recursos_requeridos:
        if "COMBUSTIBLE" in req["categoria"].upper():
            capacidad_total = 0
            cantidad_por_evento = req["cantidad"]

            # Calcular capacidad total
            for recurso in recursos:
                if (
                    recurso["categoria"] == req["categoria"]
                    and recurso["tipo"] == req["tipo"]
                    and recurso.get("es_combustible", False)
                ):
                    capacidad_total += recurso["cantidad_total"]

            # Verificar si toda la serie es posible
            total_necesario = req["cantidad"] * num_eventos
            if total_necesario > capacidad_total:
                eventos_posibles = capacidad_total // req["cantidad"]
                eventos_posibles = int(eventos_posibles)
                return (
                    False,
                    f"❌ Capacidad insuficiente (máximo {eventos_posibles} eventos)",
                    [],
                    None,
                )

    # 9. Verificar combustible disponible actual
    total_combustible_necesario = {}
    for req in recursos_requeridos:
        if "COMBUSTIBLE" in req["categoria"].upper():
            categoria_tipo = f"{req['categoria']}|{req['tipo']}"
            total_combustible_necesario[categoria_tipo] = req["cantidad"] * num_eventos

    for categoria_tipo, cantidad_necesaria in total_combustible_necesario.items():
        categoria, tipo = categoria_tipo.split("|")
        stock_disponible = 0

        for recurso in recursos:
            if (
                recurso["es_combustible"]
                and recurso["categoria"] == categoria
                and recurso["tipo"] == tipo
            ):
                stock_disponible += recurso["cantidad_disponible"]

        if stock_disponible < cantidad_necesaria:
            faltante = cantidad_necesaria - stock_disponible
            return (
                False,
                f"❌ Combustible insuficiente (faltan {faltante}L de {categoria} {tipo})",
                [],
                None,
            )

    # 10. VALIDAR TODOS LOS EVENTOS (sin crear)
    eventos_validados = []

    fecha_temp = fecha_inicial
    for i in range(num_eventos):
        # Validar este evento específico
        exito, mensaje, _, _ = procesar_creacion_evento(
            tipo_evento=tipo_evento,
            day=str(fecha_temp.day),
            month=str(fecha_temp.month),
            year=str(fecha_temp.year),
            duracion_str=str(duracion_dias),
            recursos_seleccionados_nombres=recursos_seleccionados_nombres,
            recursos=recursos,
            eventos_planificados=eventos_planificados + eventos_validados,
            tipos_evento_data=tipos_evento_data,
            modo_validacion=True,
        )

        if not exito:
            # Determinar si es error de solapamiento
            if es_error_solapamiento(mensaje):
                return False, mensaje, [], fecha_temp
            else:
                return False, mensaje, [], None

        # Crear evento simulado con estructura completa
        evento_simulado = {
            "fecha_inicio": fecha_temp.strftime("%d/%m/%Y"),
            "fecha_fin": (fecha_temp + timedelta(days=duracion_dias - 1)).strftime(
                "%d/%m/%Y"
            ),
            "recursos_detalle": [],  # Tendrá estructura completa
            "recursos_usados": {},
        }

        # Llenar recursos_detalle (igual que en crear_evento_dict)
        for nombre_recurso in recursos_seleccionados_nombres:
            for recurso in recursos:
                if recurso["nombre_mostrar"] == nombre_recurso:
                    cantidad = 1
                    if recurso["es_combustible"]:
                        for req in recursos_requeridos:
                            if (
                                req["categoria"] == recurso["categoria"]
                                and req["tipo"] == recurso["tipo"]
                            ):
                                cantidad = req.get("cantidad", 1)
                                break

                    evento_simulado["recursos_detalle"].append(
                        {
                            "nombre_mostrar": recurso["nombre_mostrar"],
                            "categoria": recurso["categoria"],
                            "tipo": recurso["tipo"],
                            "es_combustible": recurso["es_combustible"],
                            "cantidad": cantidad,
                        }
                    )

                    evento_simulado["recursos_usados"][nombre_recurso] = cantidad
                    break

        eventos_validados.append(evento_simulado)
        fecha_temp += timedelta(days=intervalo_dias)

    # 11. CREAR LOS EVENTOS REALES (CON ESTRUCTURA UNIFICADA) - CORREGIDO
    fecha_temp = fecha_inicial
    eventos_creados = []
    recursos_opcionales_serie = set()  # ← conjunto para recursos opcionales únicos

    for i in range(num_eventos):
        # Crear el evento real
        exito, mensaje, nuevo_evento, recursos_opcionales = procesar_creacion_evento(
            tipo_evento=tipo_evento,
            day=str(fecha_temp.day),
            month=str(fecha_temp.month),
            year=str(fecha_temp.year),
            duracion_str=str(duracion_dias),
            recursos_seleccionados_nombres=recursos_seleccionados_nombres,
            recursos=recursos,
            eventos_planificados=eventos_planificados,
            tipos_evento_data=tipos_evento_data,
            modo_validacion=False,
        )

        # VERIFICACIÓN CLAVE: Si hay error, retornar inmediatamente
        if not exito:
            return (
                False,
                f"❌ Error en evento {i+1}: {mensaje}",
                eventos_creados,
                fecha_temp,
            )

        # VERIFICACIÓN CLAVE: Si no hay nuevo_evento, retornar error
        if nuevo_evento is None:
            return (
                False,
                f"❌ Error en evento {i+1}: No se pudo crear",
                eventos_creados,
                fecha_temp,
            )

        # Si llegamos aquí, el evento se creó exitosamente
        eventos_creados.append(nuevo_evento)
        eventos_planificados.append(nuevo_evento)

        # Extraer recursos opcionales de la lista devuelta
        if recursos_opcionales and isinstance(recursos_opcionales, list):
            for recurso in recursos_opcionales:
                if isinstance(recurso, dict) and "nombre_mostrar" in recurso:
                    recursos_opcionales_serie.add(recurso["nombre_mostrar"])
                elif isinstance(recurso, str):
                    recursos_opcionales_serie.add(recurso)

        fecha_temp += timedelta(days=intervalo_dias)

    # 12. Mensaje final de la serie
    mensaje_final = f"✅ Serie creada: {len(eventos_creados)} eventos"

    # Añadir información sobre recursos opcionales si los hay
    if recursos_opcionales_serie:
        mensaje_final += f"\n\nℹ️ Recursos opcionales incluidos"
    
    return True, mensaje_final, eventos_creados, None

def buscar_serie_completa_disponible(
    tipo_evento,
    recursos_seleccionados_nombres,
    duracion_dias,
    intervalo_dias,
    num_eventos,
    recursos,
    eventos_planificados,
    tipos_evento_data,
    app=None,
):
    LIMITE_DIAS_SERIE = 365  # Límite de duración de serie
    LIMITE_FUTURO_DIAS = 1095  # Límite de 3 años para planificación

    # --- 1. VERIFICACIONES PREVIAS ---

    # Verificar duración vs intervalo
    if num_eventos > 1 and intervalo_dias < duracion_dias:
        return (
            False,
            None,
            "❌ El intervalo debe ser mayor que la duración",
        )

    # Calcular duración total de la serie
    fecha_inicio_simulada = date.today()
    fecha_inicio_ultimo = fecha_inicio_simulada + timedelta(
        days=(num_eventos - 1) * intervalo_dias
    )
    fecha_fin_ultimo = fecha_inicio_ultimo + timedelta(days=duracion_dias - 1)
    duracion_total_serie = (fecha_fin_ultimo - fecha_inicio_simulada).days + 1

    # Verificar que la serie no exceda 365 días
    if duracion_total_serie > LIMITE_DIAS_SERIE:
        eventos_posibles = (LIMITE_DIAS_SERIE - duracion_dias) // intervalo_dias + 1
        eventos_posibles = max(1, eventos_posibles)

        return (
            False,
            None,
            f"❌ Serie demasiado larga (máximo {eventos_posibles} eventos)",
        )

    # Verificar que toda la serie quepa dentro de 3 años desde hoy
    HOY = date.today()
    FECHA_MAXIMA = HOY + timedelta(days=LIMITE_FUTURO_DIAS)

    if fecha_fin_ultimo > FECHA_MAXIMA:
        # Calcular cuántos eventos caben en los 3 años
        dias_disponibles = (FECHA_MAXIMA - HOY).days
        eventos_posibles = 1
        if intervalo_dias > 0:
            eventos_posibles = min(
                num_eventos, (dias_disponibles // intervalo_dias) + 1
            )

        # Asegurar que al menos quepa un evento
        eventos_posibles = max(1, eventos_posibles)

        return (
            False,
            None,
            f"❌ La serie excede 3 años (máximo {eventos_posibles} eventos)",
        )

    if tipo_evento not in tipos_evento_data:
        return False, None, "❌ Tipo de evento no válido"

    evento_data = tipos_evento_data.get(tipo_evento)
    recursos_req = evento_data.get("recursos_requeridos", [])

    # Verificar capacidad máxima vs necesidad
    for req in recursos_req:
        if "COMBUSTIBLE" in req["categoria"].upper():
            capacidad_total = 0
            for r in recursos:
                if (
                    r["categoria"] == req["categoria"]
                    and r["tipo"] == req["tipo"]
                    and r.get("es_combustible", False)
                ):
                    capacidad_total += r["cantidad_total"]

            # Verificar si un solo evento es posible
            if req["cantidad"] > capacidad_total:
                return (
                    False,
                    None,
                    f"❌ Capacidad insuficiente (se necesitan {req['cantidad']}L, capacidad: {capacidad_total}L)",
                )

            # Verificar si toda la serie es posible
            total_necesario = req["cantidad"] * num_eventos
            if total_necesario > capacidad_total:
                eventos_posibles = capacidad_total // req["cantidad"]
                eventos_posibles = int(eventos_posibles)
                return (
                    False,
                    None,
                    f"❌ Capacidad insuficiente (máximo {eventos_posibles} eventos)",
                )

    # Verificar combustible disponible actual
    total_combustible_necesario = {}
    for req in recursos_req:
        if "COMBUSTIBLE" in req["categoria"].upper():
            clave = f"{req['categoria']}|{req['tipo']}"
            if clave not in total_combustible_necesario:
                total_combustible_necesario[clave] = 0
            total_combustible_necesario[clave] += req["cantidad"] * num_eventos

    # Verificar si hay suficiente combustible disponible
    for clave, cantidad_necesaria in total_combustible_necesario.items():
        categoria, tipo = clave.split("|")
        stock_disponible = 0

        for r in recursos:
            if (
                r["categoria"] == categoria
                and r["tipo"] == tipo
                and r.get("es_combustible", False)
            ):
                stock_disponible += r["cantidad_disponible"]

        if stock_disponible < cantidad_necesaria:
            faltante = cantidad_necesaria - stock_disponible
            return (
                False,
                None,
                f"❌ Combustible insuficiente (faltan {faltante}L de {categoria} {tipo})",
            )
    
    # --- 2. BÚSQUEDA DE FECHAS DISPONIBLES ---
    LIMITE_BUSQUEDA = LIMITE_FUTURO_DIAS  # Buscar en los próximos 3 años

    fecha_inicio_busqueda = date.today()
    fecha_maxima = fecha_inicio_busqueda + timedelta(days=LIMITE_FUTURO_DIAS)

    for dias_offset in range(LIMITE_BUSQUEDA):

        if app and dias_offset % 5 == 0:
            app.update()

        fecha_candidata = fecha_inicio_busqueda + timedelta(days=dias_offset)

        # Verificar que toda la serie quepa dentro de 3 años para esta fecha candidata
        fecha_inicio_ultimo_candidato = fecha_candidata + timedelta(
            days=(num_eventos - 1) * intervalo_dias
        )
        fecha_fin_ultimo_candidato = fecha_inicio_ultimo_candidato + timedelta(
            days=duracion_dias - 1
        )

        if fecha_fin_ultimo_candidato > fecha_maxima:
            # Esta fecha no sirve, pasar a la siguiente
            continue

        puede_toda_la_serie = True
        eventos_simulados = []

        for i in range(num_eventos):
            f_actual = fecha_candidata + timedelta(days=i * intervalo_dias)

            # Validamos cada evento de la serie
            exito, msg, _, _ = procesar_creacion_evento(
                tipo_evento,
                str(f_actual.day),
                str(f_actual.month),
                str(f_actual.year),
                str(duracion_dias),
                recursos_seleccionados_nombres,
                recursos,
                eventos_planificados + eventos_simulados,
                tipos_evento_data,
                modo_validacion=True,
            )

            if not exito:
                puede_toda_la_serie = False
                # Si el error NO es de solapamiento, terminar la búsqueda
                if not es_error_solapamiento(msg):
                    return False, None, msg
                break

            # Añadir a la simulación
            eventos_simulados.append(
                {
                    "fecha_inicio": f_actual.strftime("%d/%m/%Y"),
                    "fecha_fin": (
                        f_actual + timedelta(days=duracion_dias - 1)
                    ).strftime("%d/%m/%Y"),
                    "recursos_usados": {n: 1 for n in recursos_seleccionados_nombres},
                }
            )

        if puede_toda_la_serie:
            return (
                True,
                fecha_candidata,
                f"✅ Serie disponible desde {fecha_candidata.strftime('%d/%m/%Y')}",
            )

    return (
        False,
        None,
        f"❌ No hay fechas disponibles en {LIMITE_BUSQUEDA} días",
    )

def es_error_solapamiento(mensaje_error):
    """Determina si un error es de solapamiento (recursos ocupados en fechas)"""
    mensaje_lower = mensaje_error.lower()

    # Errores que SON de solapamiento
    palabras_solapamiento = [
        "ocupad",
        "ocupado",
        "ocupada",
        "ocupados",
        "ocupadas",
        "solap",
        "solapa",
        "solapamiento",
        "solapan",
        "calendario",
        "disponible",
        "disponibilidad",
        "hueco",
        "libre",
        "conflicto",
        "choque",
        "superpone",
    ]

    # Errores que NO SON de solapamiento
    palabras_no_solapamiento = [
        "duración",
        "duracion",
        "duraci",
        "días",
        "dias",
        "menor",
        "mayor",
        "mínima",
        "minima",
        "máxima",
        "maxima",
        "fecha inválida",
        "fecha invalida",
        "selecciona",
        "selección",
        "recurso prohibido",
        "requiere",
        "combustible",
        "litro",
        "litros",
        "3 años",
        "3 año",
        "1095",
        "pasado",
    ]

    # Si contiene palabras de NO solapamiento, no es solapamiento
    for palabra in palabras_no_solapamiento:
        if palabra in mensaje_lower:
            return False

    # Si contiene palabras de solapamiento, es solapamiento
    return any(palabra in mensaje_lower for palabra in palabras_solapamiento)
