from datetime import datetime

# ========== FUNCIONES PRINCIPALES ==========


def verificar_disponibilidad_fecha(
    fecha_inicio, fecha_fin, recursos_necesarios, eventos_planificados, recursos
):
    # 1. Encontrar eventos que se solapan
    eventos_solapados = encontrar_eventos_solapados(
        fecha_inicio, fecha_fin, eventos_planificados
    )

    # 2. Si no hay eventos solapados, verificar solo combustible
    if not eventos_solapados:
        disponible, mensaje = verificar_disponibilidad_sin_solapamientos(
            recursos_necesarios, recursos
        )
        return disponible, mensaje

    # 3. Si hay eventos solapados, calcular recursos ocupados
    recursos_ocupados = calcular_recursos_ocupados(eventos_solapados)

    # 4. Verificar disponibilidad con solapamientos
    disponible, mensaje = verificar_disponibilidad_con_solapamientos(
        recursos_necesarios, recursos_ocupados, recursos
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
        # Sumar recursos usados por este evento
        for recurso_usado, cantidad in evento.get("recursos_usados", {}).items():
            clave = obtener_clave_recurso_por_nombre(evento, recurso_usado)

            if clave:
                if clave not in recursos_ocupados:
                    recursos_ocupados[clave] = 0
                recursos_ocupados[clave] += cantidad

    return recursos_ocupados


# Obtiene la clave (categoria|tipo) a partir del nombre del recurso
def obtener_clave_recurso_por_nombre(evento, nombre_recurso):

    for r_detalle in evento.get("recursos_detalle", []):
        if r_detalle["nombre_mostrar"] == nombre_recurso:
            return f"{r_detalle['categoria']}|{r_detalle['tipo']}"
    return None


def verificar_disponibilidad_sin_solapamientos(recursos_necesarios, recursos):
    for _, req in recursos_necesarios.items():
        if req["es_combustible"]:
            stock_disponible = obtener_stock_combustible(req, recursos)

            if stock_disponible < req["cantidad"]:
                return (
                    False,
                    f"Combustible insuficiente: {req['categoria']} {req['tipo']}",
                )

    return True, "Sin problemas de combustible"


def verificar_disponibilidad_con_solapamientos(
    recursos_necesarios, recursos_ocupados, recursos
):

    for clave, req in recursos_necesarios.items():
        cantidad_necesaria = req["cantidad"]

        # Para combustible
        if req["es_combustible"]:
            stock_disponible = obtener_stock_combustible(req, recursos)

            if stock_disponible < cantidad_necesaria:
                return (
                    False,
                    f"Combustible insuficiente con solapamientos: {req['categoria']} {req['tipo']}",
                )

        # Para equipos
        else:
            capacidad_total = obtener_capacidad_equipos(req, recursos)
            cantidad_ocupada = recursos_ocupados.get(clave, 0)
            disponible = capacidad_total - cantidad_ocupada

            if disponible < cantidad_necesaria:
                return (
                    False,
                    f"Equipos no disponibles con solapamientos: {req['categoria']} {req['tipo']}",
                )

    return True, "Disponible"


def obtener_stock_combustible(req, recursos):
    stock_total = 0
    for r in recursos:
        if r["categoria"] == req["categoria"] and r["tipo"] == req["tipo"]:
            stock_total += r["cantidad_disponible"]
    return stock_total


# Calcula la capacidad total de equipos
def obtener_capacidad_equipos(req, recursos):
    capacidad_total = 0
    for r in recursos:
        if r["categoria"] == req["categoria"] and r["tipo"] == req["tipo"]:
            capacidad_total += r["cantidad_total"]
    return capacidad_total
