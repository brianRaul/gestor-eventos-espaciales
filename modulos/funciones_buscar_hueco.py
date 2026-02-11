from datetime import datetime

# ========== FUNCIONES PRINCIPALES ==========
def verificar_disponibilidad_fecha(
    fecha_inicio, fecha_fin, recursos_necesarios, eventos_planificados, recursos,
    eventos_por_fecha=None, recursos_por_clave=None
):
    # 1. Encontrar eventos que se solapan (usar índice si está disponible)
    if eventos_por_fecha is not None:
        eventos_solapados = encontrar_eventos_solapados_rapido(fecha_inicio, fecha_fin, eventos_por_fecha)
    else:
        eventos_solapados = encontrar_eventos_solapados(fecha_inicio, fecha_fin, eventos_planificados)

    # 2. Si no hay eventos solapados, verificar solo combustible
    if not eventos_solapados:
        disponible, mensaje = verificar_disponibilidad_sin_solapamientos(
            recursos_necesarios, recursos, recursos_por_clave
        )
        return disponible, mensaje

    # 3. Si hay eventos solapados, calcular recursos ocupados
    recursos_ocupados = calcular_recursos_ocupados(eventos_solapados)

    # 4. Verificar disponibilidad con solapamientos
    disponible, mensaje = verificar_disponibilidad_con_solapamientos(
        recursos_necesarios, recursos_ocupados, recursos, recursos_por_clave
    )
    return disponible, mensaje

# Prepara los recursos requeridos en formato para verificación
# Convierte la lista de recursos requeridos a diccionario
def preparar_recursos_requeridos(recursos_requeridos):

    recursos_necesarios = {}

    for req in recursos_requeridos:
        clave = f"{req['categoria']}|{req['tipo']}"
        recursos_necesarios[clave] = {
            "categoria": req["categoria"],
            "tipo": req["tipo"],
            "cantidad": req.get("cantidad", 1),
            "es_combustible": "COMBUSTIBLE" in req["categoria"].upper(),
        }

    return recursos_necesarios

# ========== FUNCIONES AUXILIARES ==========

# Encuentra eventos que se solapan con un rango de fechas
def encontrar_eventos_solapados(fecha_inicio, fecha_fin, eventos_planificados):

    eventos_solapados = []

    # Obtener fechas del evento
    for evento in eventos_planificados:
        ev_inicio, ev_fin = obtener_fechas_evento(evento)

        if ev_inicio and ev_fin:
            # Verificar solapamiento
            se_solapan = (fecha_inicio <= ev_fin) and (fecha_fin >= ev_inicio)

            if se_solapan:
                eventos_solapados.append(evento)

    return eventos_solapados

def encontrar_eventos_solapados_rapido(fecha_inicio, fecha_fin, eventos_por_fecha):
    """
    Versión optimizada que usa el índice de fechas (eventos_por_fecha).
    """
    from datetime import timedelta
    eventos_solapados = set()
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        fecha_str = fecha_actual.strftime("%d/%m/%Y")
        eventos_dia = eventos_por_fecha.get(fecha_str, [])
        eventos_solapados.update(eventos_dia)
        fecha_actual += timedelta(days=1)
    return list(eventos_solapados)

# Extrae las fechas de inicio y fin de un evento
def obtener_fechas_evento(evento):

    try:
        ev_inicio = datetime.strptime(evento["fecha_inicio"], "%d/%m/%Y").date()
        ev_fin = datetime.strptime(evento["fecha_fin"], "%d/%m/%Y").date()
        return ev_inicio, ev_fin
    except:
        return None, None

# Calcula cuántos recursos están ocupados por eventos solapados
def calcular_recursos_ocupados(eventos_solapados):
    recursos_ocupados = {}
    for evento in eventos_solapados:
        # Usar resumen precalculado (más rápido)
        resumen = evento.get("resumen_recursos", {})
        for clave, cantidad in resumen.items():
            recursos_ocupados[clave] = recursos_ocupados.get(clave, 0) + cantidad
    return recursos_ocupados

# Obtiene la clave (categoria|tipo) a partir del nombre del recurso
def obtener_clave_recurso_por_nombre(evento, nombre_recurso):

    for r_detalle in evento.get("recursos_detalle", []):
        if r_detalle["nombre_mostrar"] == nombre_recurso:
            return f"{r_detalle['categoria']}|{r_detalle['tipo']}"
    return None

def verificar_disponibilidad_sin_solapamientos(recursos_necesarios, recursos, recursos_por_clave=None):
    for _, req in recursos_necesarios.items():
        if req["es_combustible"]:
            stock_disponible = obtener_stock_combustible(req, recursos, recursos_por_clave)
            if stock_disponible < req["cantidad"]:
                faltante = req["cantidad"] - stock_disponible
                return False, f"❌ Combustible insuficiente: {req['categoria']} {req['tipo']} (faltan {faltante}L)"
    return True, "Sin problemas de combustible"

def verificar_disponibilidad_con_solapamientos(
    recursos_necesarios, recursos_ocupados, recursos, recursos_por_clave=None
):
    for clave, req in recursos_necesarios.items():
        cantidad_necesaria = req["cantidad"]
        if req["es_combustible"]:
            stock_disponible = obtener_stock_combustible(req, recursos, recursos_por_clave)
            if stock_disponible < cantidad_necesaria:
                faltante = cantidad_necesaria - stock_disponible
                return False, f"❌ Combustible insuficiente: {req['categoria']} {req['tipo']} (faltan {faltante}L)"
        else:
            capacidad_total = obtener_capacidad_equipos(req, recursos, recursos_por_clave)
            cantidad_ocupada = recursos_ocupados.get(clave, 0)
            disponible = capacidad_total - cantidad_ocupada
            if disponible < cantidad_necesaria:
                return False, f"❌ {req['categoria']} {req['tipo']} no disponible (faltan {cantidad_necesaria - disponible} unidades)"
    return True, "Disponible"

def obtener_stock_combustible(req, recursos, recursos_por_clave=None):
    if recursos_por_clave is not None:
        clave = f"{req['categoria']}|{req['tipo']}"
        recurso = recursos_por_clave.get(clave)
        return recurso["cantidad_disponible"] if recurso else 0
    else:
        # Fallback a búsqueda lineal
        stock_total = 0
        for r in recursos:
            if r["categoria"] == req["categoria"] and r["tipo"] == req["tipo"]:
                stock_total += r["cantidad_disponible"]
        return stock_total

# Calcula la capacidad total de equipos
def obtener_capacidad_equipos(req, recursos, recursos_por_clave=None):
    if recursos_por_clave is not None:
        clave = f"{req['categoria']}|{req['tipo']}"
        recurso = recursos_por_clave.get(clave)
        return recurso["cantidad_total"] if recurso else 0
    else:
        capacidad_total = 0
        for r in recursos:
            if r["categoria"] == req["categoria"] and r["tipo"] == req["tipo"]:
                capacidad_total += r["cantidad_total"]
        return capacidad_total