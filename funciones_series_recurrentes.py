"""
Módulo para series recurrentes - REUTILIZA funciones existentes
"""
from datetime import datetime, date, timedelta
from funciones_crear_evento import procesar_creacion_evento
from funciones_buscar_hueco import preparar_recursos_requeridos

def crear_serie_recurrente(
    tipo_evento,
    recursos_seleccionados_nombres,
    fecha_inicio_str,      # "DD/MM/YYYY"
    duracion_dias,
    intervalo_dias,
    num_eventos,
    recursos,
    eventos_planificados,
    tipos_evento_data,
    app=None
):
    """Crea serie de eventos - VERSIÓN MEJORADA (valida combustible para TODA la serie)"""
    
    # 1. Convertir fecha
    try:
        fecha_inicial = datetime.strptime(fecha_inicio_str, "%d/%m/%Y").date()
    except:
        return False, "❌ Fecha inválida", [], None
    
    # 2. Obtener datos del tipo de evento
    if tipo_evento not in tipos_evento_data:
        return False, "❌ Tipo de evento no encontrado", [], None
    
    evento_data = tipos_evento_data[tipo_evento]
    recursos_requeridos = evento_data.get("recursos_requeridos", [])
    recursos_necesarios = preparar_recursos_requeridos(recursos_requeridos)
    
    # 3. VERIFICAR COMBUSTIBLE PARA TODA LA SERIE ANTES DE NADA
    # Calcular combustible total necesario
    total_combustible_necesario = {}
    
    for clave, req in recursos_necesarios.items():
        if req["es_combustible"]:
            categoria_tipo = f"{req['categoria']}|{req['tipo']}"
            total_combustible_necesario[categoria_tipo] = req["cantidad"] * num_eventos
    
    # Verificar si hay suficiente combustible
    for categoria_tipo, cantidad_necesaria in total_combustible_necesario.items():
        # Obtener stock disponible
        categoria, tipo = categoria_tipo.split("|")
        stock_disponible = 0
        
        for recurso in recursos:
            if (recurso["es_combustible"] and 
                recurso["categoria"] == categoria and 
                recurso["tipo"] == tipo):
                stock_disponible += recurso["cantidad_disponible"]
        
        if stock_disponible < cantidad_necesaria:
            return False, f"❌ COMBUSTIBLE INSUFICIENTE PARA TODA LA SERIE\nSe necesitan {cantidad_necesaria}L de {categoria} {tipo}\nSolo hay {stock_disponible}L disponibles", [], None
    
    eventos_creados = []
    
    # 4. PRIMERO: VALIDAR TODOS LOS EVENTOS (sin crear)
    eventos_validados = []  # Para guardar información de eventos validados
    
    fecha_temp = fecha_inicial
    for i in range(num_eventos):
        # Validar este evento específico
        exito, mensaje, _ = procesar_creacion_evento(
            tipo_evento=tipo_evento,
            day=str(fecha_temp.day),
            month=str(fecha_temp.month),
            year=str(fecha_temp.year),
            duracion_str=str(duracion_dias),
            recursos_seleccionados_nombres=recursos_seleccionados_nombres,
            recursos=recursos,
            eventos_planificados=eventos_planificados + eventos_validados,  # ← Incluye eventos YA validados de la serie
            tipos_evento_data=tipos_evento_data,
            modo_validacion=True  # ← SOLO VALIDAR
        )
        
        if not exito:
            return False, f"❌ Evento {i+1} falló en validación: {mensaje}", [], fecha_temp
        
        # Si pasa validación, guardar información temporal del evento
        evento_simulado = {
            "fecha_inicio": fecha_temp.strftime("%d/%m/%Y"),
            "fecha_fin": (fecha_temp + timedelta(days=duracion_dias - 1)).strftime("%d/%m/%Y"),
            "recursos_detalle": [],
            "recursos_usados": {}
        }
        
        # Llenar recursos del evento simulado
        for nombre_recurso in recursos_seleccionados_nombres:
            for recurso in recursos:
                if recurso["nombre_mostrar"] == nombre_recurso:
                    evento_simulado["recursos_detalle"].append({
                        "nombre_mostrar": recurso["nombre_mostrar"],
                        "categoria": recurso["categoria"],
                        "tipo": recurso["tipo"],
                        "es_combustible": recurso["es_combustible"]
                    })
                    
                    # Calcular cantidad usada
                    cantidad = 1
                    if recurso["es_combustible"]:
                        for req in recursos_requeridos:
                            if (req["categoria"] == recurso["categoria"] and 
                                req["tipo"] == recurso["tipo"]):
                                cantidad = req.get("cantidad", 1)
                                break
                    
                    evento_simulado["recursos_usados"][nombre_recurso] = cantidad
                    break
        
        eventos_validados.append(evento_simulado)
        fecha_temp += timedelta(days=intervalo_dias)
    
    # 5. SEGUNDO: SI TODOS PASARON LA VALIDACIÓN, CREARLOS
    fecha_temp = fecha_inicial
    eventos_creados = []
    
    for i in range(num_eventos):
        # Crear el evento real
        exito, mensaje, nuevo_evento = procesar_creacion_evento(
            tipo_evento=tipo_evento,
            day=str(fecha_temp.day),
            month=str(fecha_temp.month),
            year=str(fecha_temp.year),
            duracion_str=str(duracion_dias),
            recursos_seleccionados_nombres=recursos_seleccionados_nombres,
            recursos=recursos,
            eventos_planificados=eventos_planificados,  # ← Ahora la lista REAL que se va actualizando
            tipos_evento_data=tipos_evento_data,
            modo_validacion=False  # ← CREAR REAL
        )
        
        if exito and nuevo_evento:
            # Marcar como serie
            nuevo_evento["es_serie"] = True
            nuevo_evento["serie_info"] = {
                "total": num_eventos,
                "numero": i + 1,
                "intervalo": intervalo_dias
            }
            eventos_creados.append(nuevo_evento)
            # Agregar a la lista principal
            eventos_planificados.append(nuevo_evento)
        else:
            # Esto no debería pasar porque ya validamos, pero por si acaso
            return False, f"❌ Evento {i+1} falló inesperadamente: {mensaje}", eventos_creados, fecha_temp
        
        fecha_temp += timedelta(days=intervalo_dias)
    
    return True, f"✅ Serie creada: {len(eventos_creados)} eventos", eventos_creados, None


def buscar_serie_completa_disponible(
    tipo_evento,
    recursos_seleccionados_nombres,
    duracion_dias,
    intervalo_dias,
    num_eventos,
    recursos,
    eventos_planificados,
    tipos_evento_data,
    fecha_inicio_busqueda=None
):
    """Busca fecha que pueda acomodar TODA la serie """
    
    if fecha_inicio_busqueda is None:
        fecha_inicio_busqueda = date.today()
    
    # 1. Primero verificar combustible para toda la serie
    if tipo_evento not in tipos_evento_data:
        return False, None, "❌ Tipo de evento no encontrado"
    
    evento_data = tipos_evento_data[tipo_evento]
    recursos_requeridos = evento_data.get("recursos_requeridos", [])
    recursos_necesarios = preparar_recursos_requeridos(recursos_requeridos)
    
    # Calcular combustible total necesario
    total_combustible_necesario = {}
    for clave, req in recursos_necesarios.items():
        if req["es_combustible"]:
            categoria_tipo = f"{req['categoria']}|{req['tipo']}"
            total_combustible_necesario[categoria_tipo] = req["cantidad"] * num_eventos
    
    # Verificar si hay suficiente combustible
    for categoria_tipo, cantidad_necesaria in total_combustible_necesario.items():
        categoria, tipo = categoria_tipo.split("|")
        stock_disponible = 0
        
        for recurso in recursos:
            if (recurso["es_combustible"] and 
                recurso["categoria"] == categoria and 
                recurso["tipo"] == tipo):
                stock_disponible += recurso["cantidad_disponible"]
        
        if stock_disponible < cantidad_necesaria:
            return False, None, f"❌ COMBUSTIBLE INSUFICIENTE PARA {num_eventos} EVENTOS\n{categoria} {tipo}: Se necesitan {cantidad_necesaria}L, hay {stock_disponible}L"
    
    # 2. Buscar fecha que pueda acomodar toda la serie
    for dias in range(365):
        fecha_candidata = fecha_inicio_busqueda + timedelta(days=dias)
        puede_serie = True
        
        # Lista temporal para simular eventos de esta serie
        eventos_simulados_serie = []
        fecha_temp = fecha_candidata
        
        # Validar cada evento de la serie
        for i in range(num_eventos):
            exito, mensaje, _ = procesar_creacion_evento(
                tipo_evento=tipo_evento,
                day=str(fecha_temp.day),
                month=str(fecha_temp.month),
                year=str(fecha_temp.year),
                duracion_str=str(duracion_dias),
                recursos_seleccionados_nombres=recursos_seleccionados_nombres,
                recursos=recursos,
                eventos_planificados=eventos_planificados + eventos_simulados_serie,  # ← Eventos reales + simulados
                tipos_evento_data=tipos_evento_data,
                modo_validacion=True
            )
            
            if not exito:
                puede_serie = False
                break
            
            # Si pasa validación, simular el evento para los siguientes
            evento_simulado = {
                "fecha_inicio": fecha_temp.strftime("%d/%m/%Y"),
                "fecha_fin": (fecha_temp + timedelta(days=duracion_dias - 1)).strftime("%d/%m/%Y"),
                "recursos_detalle": [],
                "recursos_usados": {}
            }
            
            # Llenar recursos_detalle y recursos_usados
            for nombre_recurso in recursos_seleccionados_nombres:
                for recurso in recursos:
                    if recurso["nombre_mostrar"] == nombre_recurso:
                        evento_simulado["recursos_detalle"].append({
                            "nombre_mostrar": recurso["nombre_mostrar"],
                            "categoria": recurso["categoria"],
                            "tipo": recurso["tipo"],
                            "es_combustible": recurso.get("es_combustible", False)
                        })
                        
                        # Calcular cantidad
                        cantidad = 1
                        if recurso.get("es_combustible", False):
                            for req in recursos_requeridos:
                                if req["categoria"] == recurso["categoria"] and req["tipo"] == recurso["tipo"]:
                                    cantidad = req.get("cantidad", 1)
                                    break
                        
                        evento_simulado["recursos_usados"][nombre_recurso] = cantidad
                        break
            
            eventos_simulados_serie.append(evento_simulado)
            fecha_temp += timedelta(days=intervalo_dias)
        
        if puede_serie:
            return True, fecha_candidata, f"✅ Serie disponible desde {fecha_candidata.strftime('%d/%m/%Y')}"
    
    return False, None, "❌ No se encontró fecha para toda la serie"