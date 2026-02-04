from datetime import datetime, timedelta

# ========== FUNCIONES DE VALIDACIÓN ==========

# Valida que el tipo de evento sea válido
def validar_tipo_evento(tipo_evento, tipos_evento_data):
    if not tipo_evento or tipo_evento == "Elige un tipo de evento":
        return False, "❌ Selecciona un tipo de evento"
    
    if tipo_evento not in tipos_evento_data:
        return False, "❌ Tipo de evento no encontrado"
    
    return True, ""


# Valida la fecha y duración del evento
def validar_fecha_duracion(day, month, year, duracion_str, tipo_evento, tipos_evento_data):
    try:
        # PRIMERO: Verificar si algún número es demasiado grande
        if len(day) > 2 or len(month) > 2 or len(year) > 4 or len(duracion_str) > 4:
            return False,"❌ Fecha o duración inválida", None, None, None
            
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
            return False, f"❌ No puedes planificar eventos a más de 3 años en el futuro", None, None, None
        
        fecha_fin = fecha_inicio + timedelta(days=duracion - 1)
        
        # Validar que el evento completo no exceda los 3 años
        if fecha_fin.date() > fecha_maxima:
            return False, f"❌ El evento no puede terminar después de 3 años a partir de hoy", None, None, None
        
        # Validar duración min/max del evento
        evento_data = tipos_evento_data[tipo_evento]
        config_evento = evento_data.get("configuracion_evento", {})
        d_min = config_evento.get("duracion_minima", 1)
        d_max = config_evento.get("duracion_maxima", 30)
        
        if not (d_min <= duracion <= d_max):
            return False, f"❌ Duración permitida: {d_min}-{d_max} días", None, None, None
        
        return True, "", fecha_inicio, fecha_fin, duracion
        
    except ValueError:
        return False, "❌ Fecha o duración inválida", None, None, None
    except OverflowError:
        return False, "❌ Fecha o duración inválida", None, None, None
    
# Convierte nombres de recursos a objetos completos y valida
def validar_recursos_seleccionados(recursos_seleccionados_nombres, recursos):
    recursos_seleccionados = []
    for nombre_mostrar in recursos_seleccionados_nombres:
        for recurso in recursos:
            if recurso["nombre_mostrar"] == nombre_mostrar:
                recursos_seleccionados.append(recurso)
                break
    
    if not recursos_seleccionados:
        return False, "❌ Selecciona al menos un recurso", None
    
    return True, "", recursos_seleccionados


# Valida reglas de exclusión de recursos
def validar_reglas_exclusion(evento_data, recursos_seleccionados):
    reglas_exclusion = evento_data.get("reglas_exclusion", [])
    
    for regla in reglas_exclusion:
        categoria_prohibida = regla.get("categoria", "")
        tipos_prohibidos = regla.get("tipos_prohibidos", [])
        
        for recurso in recursos_seleccionados:
            if (recurso["categoria"] == categoria_prohibida and 
                recurso["tipo"] in tipos_prohibidos):
                return False, f"⛔ RECURSO PROHIBIDO: '{recurso['nombre_mostrar']}' no está permitido para este evento."
    
    return True, ""


# Valida requisitos de recursos coexistentes
def validar_requisitos_coexistentes(evento_data, recursos_seleccionados):
    requisitos_coexistentes = evento_data.get("requisitos_coexistentes", [])
    
    for requisito in requisitos_coexistentes:
        categoria_principal = requisito.get("categoria", "")
        tipo_principal = requisito.get("tipo", "")
        requiere_lista = requisito.get("requiere", [])
        
        # Verificar si el recurso principal está seleccionado
        principal_seleccionado = False
        for recurso in recursos_seleccionados:
            if (recurso["categoria"] == categoria_principal and 
                recurso["tipo"] == tipo_principal):
                principal_seleccionado = True
                break
        
        if principal_seleccionado:
            # Verificar que todos los recursos requeridos estén seleccionados
            for requerido in requiere_lista:
                cat_req = requerido.get("categoria", "")
                tipo_req = requerido.get("tipo", "")
                encontrado = False
                
                for recurso in recursos_seleccionados:
                    if (recurso["categoria"] == cat_req and 
                        recurso["tipo"] == tipo_req):
                        encontrado = True
                        break
                
                if not encontrado:
                    return False, f"❌ '{categoria_principal} {tipo_principal}' requiere también '{cat_req} {tipo_req}'"
    
    return True, ""


# Valida que se cumplan los recursos requeridos
def validar_recursos_requeridos(evento_data, recursos_seleccionados, recursos, eventos_planificados, fecha_inicio, fecha_fin):
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
            return False, f"❌ El recurso requerido '{categoria_req} {tipo_req}' no está seleccionado"
        
        recursos_del_tipo = recursos_seleccionados_dict[clave_req]
        
        # Para combustible, verificar cantidad disponible
        if "COMBUSTIBLE" in categoria_req.upper():
            total_disponible = sum(r["cantidad_disponible"] for r in recursos_del_tipo)
            if total_disponible < cantidad_req:
              faltante = cantidad_req - total_disponible
              return False, f"❌ COMBUSTIBLE INSUFICIENTE: {categoria_req} {tipo_req}\nSe necesitan: {cantidad_req}L\nDisponible: {total_disponible}L\nFaltan: {faltante}L\n\n💡 Usa 'Rellenar Todo' para reponer combustible."
        else:
            # Para equipos: verificar ocupación en esas fechas
            capacidad_total = sum(r["cantidad_total"] for r in recursos_del_tipo)
            
            # Buscar eventos que se solapen
            cantidad_ocupada = 0
            for evento in eventos_planificados:
                try:
                    ev_inicio = datetime.strptime(evento["fecha_inicio"], "%d/%m/%Y").date()
                    ev_fin = datetime.strptime(evento["fecha_fin"], "%d/%m/%Y").date()
                except:
                    continue
                
                # Verificar solapamiento
                se_solapan = (fecha_inicio.date() <= ev_fin) and (fecha_fin.date() >= ev_inicio)
                
                if se_solapan:
                    # Contar cuántos de este tipo usa el evento
                    for rd in evento.get("recursos_detalle", []):
                        if (rd["categoria"] == categoria_req and 
                            rd["tipo"] == tipo_req):
                            cantidad_ocupada += 1
            
            disponible = capacidad_total - cantidad_ocupada
            
            if disponible < cantidad_req:
                return False, f"❌ Ocupado en esas fechas: {categoria_req} {tipo_req}. (Total: {capacidad_total}, Ocupados: {cantidad_ocupada}, Necesarios: {cantidad_req})"
    
    return True, ""


# Consume los recursos necesarios para el evento
def consumir_recursos(evento_data, recursos_seleccionados, recursos):
    recursos_requeridos = evento_data.get("recursos_requeridos", [])
    recursos_consumidos = []
    
    for recurso in recursos_seleccionados:
        if recurso["es_combustible"]:
            # Buscar el recurso combustible en la lista principal
            for r in recursos:
                if r["nombre_mostrar"] == recurso["nombre_mostrar"]:
                    # Encontrar cuánto combustible necesita
                    cantidad_necesaria = 0
                    for recurso_req in recursos_requeridos:
                        if (recurso_req["categoria"] == r["categoria"] and 
                            recurso_req["tipo"] == r["tipo"]):
                            cantidad_necesaria = recurso_req["cantidad"]
                            break
                    
                    # Consumir el recurso
                    r["cantidad_disponible"] -= cantidad_necesaria
                    recursos_consumidos.append({
                        "recurso": r["nombre_mostrar"],
                        "cantidad": cantidad_necesaria,
                        "es_consumible": True,
                    })
                    break
        else:
            # Para recursos NO combustibles
            recursos_consumidos.append({
                "recurso": recurso["nombre_mostrar"],
                "cantidad": 1,
                "es_consumible": False,
            })
    
    return recursos_consumidos


# Crea el diccionario del evento
def crear_evento_dict(tipo_evento, fecha_inicio, fecha_fin, duracion, 
                     recursos_seleccionados_nombres, recursos_seleccionados,
                     recursos_requeridos, recursos_consumidos):
    
    # 1. Crear recursos_detalle completo CON CANTIDAD
    recursos_detalle = []
    for recurso in recursos_seleccionados:
        # Determinar cantidad (1 para equipos, cantidad específica para combustible)
        cantidad = 1
        if recurso["es_combustible"]:
            # Buscar la cantidad en recursos_requeridos
            for req in recursos_requeridos:
                if (req["categoria"] == recurso["categoria"] and 
                    req["tipo"] == recurso["tipo"]):
                    cantidad = req.get("cantidad", 1)
                    break
        
        recursos_detalle.append({
            "nombre_mostrar": recurso["nombre_mostrar"],
            "categoria": recurso["categoria"],
            "modelo": recurso["modelo"],
            "tipo": recurso["tipo"],
            "es_combustible": recurso["es_combustible"],
            "es_consumible": recurso["es_combustible"],
            "cantidad": cantidad  # ← CLAVE: cantidad específica para combustible
        })
    
    # 2. Crear diccionario con recursos usados (para compatibilidad)
    uso_recursos_evento = {}
    for recurso in recursos_seleccionados:
        if recurso["es_combustible"]:
            # Encontrar cuánto combustible necesita
            for req in recursos_requeridos:
                if (req["categoria"] == recurso["categoria"] and 
                    req["tipo"] == recurso["tipo"]):
                    uso_recursos_evento[recurso["nombre_mostrar"]] = req.get("cantidad", 1)
                    break
        else:
            uso_recursos_evento[recurso["nombre_mostrar"]] = 1
    
    # 3. Crear evento con estructura UNIFICADA
    nuevo_evento = {
        "tipo": tipo_evento,
        "fecha_inicio": fecha_inicio.strftime("%d/%m/%Y"),
        "fecha_fin": fecha_fin.strftime("%d/%m/%Y"),
        "duracion_dias": duracion,
        "recursos": recursos_seleccionados_nombres,
        "recursos_detalle": recursos_detalle,      # ← ESTRUCTURA COMPLETA
        "recursos_usados": uso_recursos_evento,
        "recursos_consumidos": recursos_consumidos,
        "estado": "planificado",
    }
    
    return nuevo_evento

# Valida si hay recursos seleccionados que no son necesarios ni prohibidos
def validar_recursos_opcionales(evento_data, recursos_seleccionados):
    recursos_requeridos = evento_data.get("recursos_requeridos", [])
    reglas_exclusion = evento_data.get("reglas_exclusion", [])
    
    # Crear conjunto de claves de recursos requeridos
    requeridos_keys = set()
    for req in recursos_requeridos:
        clave = f"{req['categoria']}|{req['tipo']}"
        requeridos_keys.add(clave)
    
    # Crear conjunto de claves de recursos prohibidos
    prohibidos_keys = set()
    for regla in reglas_exclusion:
        categoria = regla.get("categoria", "")
        for tipo in regla.get("tipos_prohibidos", []):
            clave = f"{categoria}|{tipo}"
            prohibidos_keys.add(clave)
    
    # Identificar recursos opcionales (seleccionados pero no requeridos ni prohibidos)
    recursos_opcionales = []
    for recurso in recursos_seleccionados:
        clave = f"{recurso['categoria']}|{recurso['tipo']}"
        if clave not in requeridos_keys and clave not in prohibidos_keys:
            recursos_opcionales.append(recurso)
    
    return recursos_opcionales

# ========== FUNCIÓN PRINCIPAL ==========

def procesar_creacion_evento(tipo_evento, day, month, year, duracion_str,
                            recursos_seleccionados_nombres, recursos,
                            eventos_planificados, tipos_evento_data, modo_validacion=False):
    
    # 1. Validar tipo de evento
    valido, mensaje = validar_tipo_evento(tipo_evento, tipos_evento_data)
    if not valido:
        return False, mensaje, None
    
    # 2. Validar fecha y duración
    valido, mensaje, fecha_inicio, fecha_fin, duracion = validar_fecha_duracion(
        day, month, year, duracion_str, tipo_evento, tipos_evento_data
    )
    if not valido:
        return False, mensaje, None
    
    # 3. Obtener datos del evento
    evento_data = tipos_evento_data[tipo_evento]
    
    # 4. Convertir nombres a información completa de recursos
    valido, mensaje, recursos_seleccionados = validar_recursos_seleccionados(
        recursos_seleccionados_nombres, recursos
    )
    if not valido:
        return False, mensaje, None
    
    # 5. Validar reglas de exclusión
    valido, mensaje = validar_reglas_exclusion(evento_data, recursos_seleccionados)
    if not valido:
        return False, mensaje, None
    
    # 6. Validar requisitos coexistentes
    valido, mensaje = validar_requisitos_coexistentes(evento_data, recursos_seleccionados)
    if not valido:
        return False, mensaje, None
    
    # 7. Validar recursos requeridos
    valido, mensaje = validar_recursos_requeridos(
        evento_data, recursos_seleccionados, recursos, 
        eventos_planificados, fecha_inicio, fecha_fin
    )
    if not valido:
        return False, mensaje, None
    
    # Si estamos en modo validación, solo devolver éxito
    if modo_validacion:
        return True, "✅ Validación exitosa", None
    
    # 8.1. Validar recursos opcionales 
    recursos_opcionales = validar_recursos_opcionales(evento_data, recursos_seleccionados)
    
    # Si estamos en modo validación, devolver advertencia
    if modo_validacion and recursos_opcionales:
        nombres_opcionales = [r["nombre_mostrar"] for r in recursos_opcionales]
        mensaje_advertencia = (
            f"ℹ️ RECURSOS OPCIONALES DETECTADOS:\n"
            f"Los siguientes recursos no son necesarios pero se incluirán:\n"
            f"{', '.join(nombres_opcionales)}\n\n"
            f"✅ No hay problema, puedes continuar."
        )
        return True, mensaje_advertencia, None
    
    # Si estamos creando el evento, añadir advertencia al mensaje final
    mensaje_opcional = ""
    if recursos_opcionales:
        nombres_opcionales = [r["nombre_mostrar"] for r in recursos_opcionales]
        mensaje_opcional = (
            f"\n\nℹ️ NOTA: Se incluyeron recursos opcionales (no necesarios):\n"
            f"{', '.join(nombres_opcionales)}"
        )
    
    # Si estamos en modo validación, solo devolver éxito
    if modo_validacion:
        return True, "✅ Validación exitosa", None
    
    # 8. Consumir recursos
    recursos_consumidos = consumir_recursos(evento_data, recursos_seleccionados, recursos)
    
    # 9. Crear diccionario del evento CON ESTRUCTURA UNIFICADA
    nuevo_evento = crear_evento_dict(
        tipo_evento, fecha_inicio, fecha_fin, duracion,
        recursos_seleccionados_nombres, recursos_seleccionados,
        evento_data.get("recursos_requeridos", []), recursos_consumidos
    )

    mensaje_exito = f"🚀 Evento '{tipo_evento}' creado exitosamente"
    if mensaje_opcional:
        mensaje_exito += mensaje_opcional
    
        return True, mensaje_exito, nuevo_evento