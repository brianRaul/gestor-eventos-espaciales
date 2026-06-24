from datetime import datetime, timedelta
from . import logica_recursos as lr
from . import logica_fechas as lf
from . import logica_validaciones as lval

# ========== FUNCIONES DE VALIDACIÓN ==========


# Valida la fecha y duración del evento
def validar_fecha_duracion(
    day, month, year, duracion_str, tipo_evento, tipos_evento_data
):
    # Usar la función del módulo
    valido, mensaje, fecha_inicio, fecha_fin, duracion = lf.validar_fecha_basica(
        day, month, year, duracion_str, tipo_evento, tipos_evento_data
    )

    return valido, mensaje, fecha_inicio, fecha_fin, duracion


# Valida que se cumplan los recursos requeridos
def validar_recursos_requeridos(
    evento_data,
    recursos_seleccionados,
    recursos,
    eventos_planificados,
    fecha_inicio,
    fecha_fin,
    recursos_por_clave=None,
):
    recursos_requeridos = evento_data.get("recursos_requeridos", [])

    # Agrupar recursos seleccionados por categoría y tipo
    recursos_seleccionados_dict = {}
    for recurso in recursos_seleccionados:
        clave = f"{recurso['categoria']}-{recurso['tipo']}"
        if clave not in recursos_seleccionados_dict:
            recursos_seleccionados_dict[clave] = []
        recursos_seleccionados_dict[clave].append(recurso)

    # Verificar cada recurso requerido
    for recurso_req in recursos_requeridos:
        categoria_req = recurso_req.get("categoria", "")
        tipo_req = recurso_req.get("tipo", "")
        cantidad_req = recurso_req.get("cantidad", 1)

        clave_req = f"{categoria_req}-{tipo_req}"
        if clave_req not in recursos_seleccionados_dict:
            return (
                False,
                f"❌ El recurso requerido '{categoria_req} {tipo_req}' no está seleccionado",
            )

        recursos_del_tipo = recursos_seleccionados_dict[clave_req]

        if "COMBUSTIBLE" in categoria_req.upper():
            # Usar índice si está disponible
            if recursos_por_clave is not None:
                clave_idx = f"{categoria_req}|{tipo_req}"
                recurso_idx = recursos_por_clave.get(clave_idx)
                total_disponible = (
                    recurso_idx["cantidad_disponible"] if recurso_idx else 0
                )
            else:
                total_disponible = sum(
                    r["cantidad_disponible"] for r in recursos_del_tipo
                )
            if total_disponible < cantidad_req:
                faltante = cantidad_req - total_disponible
                return (
                    False,
                    f"❌ Combustible insuficiente: {categoria_req} {tipo_req} (faltan {faltante}L)",
                )
        else:
            # Para equipos: capacidad total
            if recursos_por_clave is not None:
                clave_idx = f"{categoria_req}|{tipo_req}"
                recurso_idx = recursos_por_clave.get(clave_idx)
                capacidad_total = recurso_idx["cantidad_total"] if recurso_idx else 0
            else:
                capacidad_total = sum(r["cantidad_total"] for r in recursos_del_tipo)

            # Buscar eventos que se solapen
            cantidad_ocupada = 0
            for evento in eventos_planificados:
                try:
                    ev_inicio = datetime.strptime(
                        evento["fecha_inicio"], "%d/%m/%Y"
                    ).date()
                    ev_fin = datetime.strptime(evento["fecha_fin"], "%d/%m/%Y").date()
                except:
                    continue
                se_solapan = (fecha_inicio.date() <= ev_fin) and (
                    fecha_fin.date() >= ev_inicio
                )
                if se_solapan:
                    for rd in evento.get("recursos_detalle", []):
                        if rd["categoria"] == categoria_req and rd["tipo"] == tipo_req:
                            cantidad_ocupada += rd.get("cantidad", 1)
            disponible = capacidad_total - cantidad_ocupada
            if disponible < cantidad_req:
                return (
                    False,
                    f"❌ Ocupado en esas fechas: {categoria_req} {tipo_req}. (Total: {capacidad_total}, Ocupados: {cantidad_ocupada}, Necesarios: {cantidad_req})",
                )
    return True, ""

# Consume los recursos necesarios para el evento
def consumir_recursos(
    evento_data, recursos_seleccionados, recursos, recursos_por_clave=None
):
    recursos_requeridos = evento_data.get("recursos_requeridos", [])
    recursos_consumidos = []

    for recurso in recursos_seleccionados:
        if recurso["es_combustible"]:
            if recursos_por_clave is not None:
                clave = f"{recurso['categoria']}|{recurso['tipo']}"
                r = recursos_por_clave.get(clave)
                if r:
                    cantidad_necesaria = 0
                    for recurso_req in recursos_requeridos:
                        if (
                            recurso_req["categoria"] == r["categoria"]
                            and recurso_req["tipo"] == r["tipo"]
                        ):
                            cantidad_necesaria = recurso_req["cantidad"]
                            break
                    r["cantidad_disponible"] -= cantidad_necesaria
                    recursos_consumidos.append(
                        {
                            "recurso": r["nombre_mostrar"],
                            "cantidad": cantidad_necesaria,
                            "es_consumible": True,
                        }
                    )
            else:
                # Fallback: búsqueda lineal
                for r in recursos:
                    if r["nombre_mostrar"] == recurso["nombre_mostrar"]:
                        cantidad_necesaria = 0
                        for recurso_req in recursos_requeridos:
                            if (
                                recurso_req["categoria"] == r["categoria"]
                                and recurso_req["tipo"] == r["tipo"]
                            ):
                                cantidad_necesaria = recurso_req["cantidad"]
                                break
                        r["cantidad_disponible"] -= cantidad_necesaria
                        recursos_consumidos.append(
                            {
                                "recurso": r["nombre_mostrar"],
                                "cantidad": cantidad_necesaria,
                                "es_consumible": True,
                            }
                        )
                        break
        else:
            recursos_consumidos.append(
                {
                    "recurso": recurso["nombre_mostrar"],
                    "cantidad": 1,
                    "es_consumible": False,
                }
            )
    return recursos_consumidos

# Crea el diccionario del evento
def crear_evento_dict(
    tipo_evento,
    fecha_inicio,
    fecha_fin,
    duracion,
    recursos_seleccionados_nombres,
    recursos_seleccionados,
    recursos_requeridos,
    recursos_consumidos,
):
    # 1. Crear recursos_detalle completo CON CANTIDAD CORRECTA
    recursos_detalle = []
    for recurso in recursos_seleccionados:
        # Buscar la cantidad requerida en recursos_requeridos (para TODOS los recursos)
        cantidad = 1  # valor por defecto (solo si no se encuentra en requeridos)
        for req in recursos_requeridos:
            if (
                req["categoria"] == recurso["categoria"]
                and req["tipo"] == recurso["tipo"]
            ):
                cantidad = req.get("cantidad", 1)
                break

        recursos_detalle.append(
            {
                "nombre_mostrar": recurso["nombre_mostrar"],
                "categoria": recurso["categoria"],
                "modelo": recurso["modelo"],
                "tipo": recurso["tipo"],
                "es_combustible": recurso["es_combustible"],
                "es_consumible": recurso["es_combustible"],
                "cantidad": cantidad,  # ← AHORA USA LA CANTIDAD REQUERIDA PARA EQUIPOS TAMBIÉN
            }
        )

    # 2. Crear diccionario con recursos usados (para compatibilidad)
    uso_recursos_evento = {}
    for recurso in recursos_seleccionados:
        # Buscar cantidad requerida
        cantidad = 1
        for req in recursos_requeridos:
            if (
                req["categoria"] == recurso["categoria"]
                and req["tipo"] == recurso["tipo"]
            ):
                cantidad = req.get("cantidad", 1)
                break
        uso_recursos_evento[recurso["nombre_mostrar"]] = cantidad

    # --- Generar resumen de recursos ---
    resumen_recursos = {}
    for rd in recursos_detalle:
        clave = f"{rd['categoria']}|{rd['tipo']}"
        resumen_recursos[clave] = resumen_recursos.get(clave, 0) + rd["cantidad"]

    nuevo_evento = {
        "tipo": tipo_evento,
        "fecha_inicio": fecha_inicio.strftime("%d/%m/%Y"),
        "fecha_fin": fecha_fin.strftime("%d/%m/%Y"),
        "duracion_dias": duracion,
        "recursos": recursos_seleccionados_nombres,
        "recursos_detalle": recursos_detalle,
        "recursos_usados": uso_recursos_evento,
        "recursos_consumidos": recursos_consumidos,
        "resumen_recursos": resumen_recursos,
        "estado": "planificado",
    }

    return nuevo_evento

# ========== FUNCIÓN PRINCIPAL ==========

def procesar_creacion_evento(
    tipo_evento,
    day,
    month,
    year,
    duracion_str,
    recursos_seleccionados_nombres,
    recursos,
    eventos_planificados,
    tipos_evento_data,
    modo_validacion=False,
    recursos_por_clave=None,
):

    # 1. Validar tipo de evento
    valido, mensaje = lval.validar_tipo_evento(tipo_evento, tipos_evento_data)
    if not valido:
        return False, mensaje, None, []

    # 2. Validar fecha y duración
    valido, mensaje, fecha_inicio, fecha_fin, duracion = validar_fecha_duracion(
        day, month, year, duracion_str, tipo_evento, tipos_evento_data
    )
    if not valido:
        return False, mensaje, None, []

    # 3. Obtener datos del evento
    evento_data = tipos_evento_data[tipo_evento]

    # 4. Convertir nombres a información completa de recursos
    valido, mensaje, recursos_seleccionados = lval.validar_recursos_seleccionados(
        recursos_seleccionados_nombres, recursos
    )

    if not valido:
        return False, mensaje, None, []

    # 5. Validar reglas de exclusión
    valido, mensaje = lval.validar_reglas_exclusion(evento_data, recursos_seleccionados)
    if not valido:
        return False, mensaje, None, []

    # 6. Validar requisitos coexistentes
    valido, mensaje = lval.validar_requisitos_coexistentes(
        evento_data, recursos_seleccionados
    )
    if not valido:
        return False, mensaje, None, []

    # 7. Validar recursos requeridos
    valido, mensaje = validar_recursos_requeridos(
        evento_data,
        recursos_seleccionados,
        recursos,
        eventos_planificados,
        fecha_inicio,
        fecha_fin,
        recursos_por_clave=recursos_por_clave,
    )
    if not valido:
        return False, mensaje, None, []

    # 8. Validar recursos opcionales
    recursos_opcionales = lval.validar_recursos_opcionales(
        evento_data, recursos_seleccionados
    )

    # Si estamos en modo validación, devolver advertencia
    if modo_validacion and recursos_opcionales:
        nombres_opcionales = [r["nombre_mostrar"] for r in recursos_opcionales]
        mensaje_advertencia = f"ℹ️ {len(nombres_opcionales)} recursos opcionales"
        return True, mensaje_advertencia, None, recursos_opcionales

    # Si estamos en modo validación sin recursos opcionales
    if modo_validacion:
        return True, "✅ Validación exitosa", None, recursos_opcionales

    # Si estamos creando el evento, añadir advertencia al mensaje final
    mensaje_opcional = ""
    if recursos_opcionales:
        nombres_opcionales = [r["nombre_mostrar"] for r in recursos_opcionales]
        # Crear lista con viñetas para mejor visualización
        lista_recursos = "\n".join([f"• {nombre}" for nombre in nombres_opcionales])
        mensaje_opcional = (
            f"\n\nℹ️ NOTA: Se incluyeron recursos opcionales (no necesarios):\n"
            f"{lista_recursos}"
        )

    # 8.1. Consumir recursos
    recursos_consumidos = consumir_recursos(
        evento_data,
        recursos_seleccionados,
        recursos,
        recursos_por_clave=recursos_por_clave,
    )

    # 9. Crear diccionario del evento
    nuevo_evento = crear_evento_dict(
        tipo_evento,
        fecha_inicio,
        fecha_fin,
        duracion,
        recursos_seleccionados_nombres,
        recursos_seleccionados,
        evento_data.get("recursos_requeridos", []),
        recursos_consumidos,
    )

    mensaje_exito = f"🚀 Evento '{tipo_evento}' creado exitosamente"

    return True, mensaje_exito, nuevo_evento, recursos_opcionales
