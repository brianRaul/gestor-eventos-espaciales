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
    app=None
):
    # 1. Convertir fecha
    try:
        fecha_inicial = datetime.strptime(fecha_inicio_str, "%d/%m/%Y").date()
    except:
        return False, "❌ Fecha inválida", [], None
    
    if intervalo_dias < duracion_dias:
        return False, f"❌ El intervalo ({intervalo_dias} días) no puede ser menor que la duración ({duracion_dias} días)", [], None
    
    # 2. Obtener datos del tipo de evento
    if tipo_evento not in tipos_evento_data:
        return False, "❌ Tipo de evento no encontrado", [], None
    
    evento_data = tipos_evento_data[tipo_evento]
    recursos_requeridos = evento_data.get("recursos_requeridos", [])
    recursos_necesarios = preparar_recursos_requeridos(recursos_requeridos)
    
    # 3. Verificar combustible para toda la serie antes de nada
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
          faltante = cantidad_necesaria - stock_disponible
          return False, f"❌ COMBUSTIBLE INSUFICIENTE PARA TODA LA SERIE\n\nSe necesitan {cantidad_necesaria}L de {categoria} {tipo} para {num_eventos} eventos.\nStock actual: {stock_disponible}L\nFaltan: {faltante}L\n\n💡 Usa 'Rellenar Todo' o elimina eventos existentes para liberar combustible.", [], None
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
            return False, mensaje, [], fecha_temp
        
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
            eventos_planificados=eventos_planificados,  #  Ahora la lista REAL que se va actualizando
            tipos_evento_data=tipos_evento_data,
            modo_validacion=False  #  CREAR REAL
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
    tipos_evento_data
):
    # --- 1. VALIDACIÓN PREVIA DE COMBUSTIBLE ---
    # Calculamos cuánto se necesita para TODA la serie
    evento_data = tipos_evento_data.get(tipo_evento)
    recursos_req = evento_data.get("recursos_requeridos", [])
    
    # Primero, calcular el combustible total necesario
    total_combustible_necesario = {}
    for req in recursos_req:
        if "COMBUSTIBLE" in req["categoria"].upper():
            clave = f"{req['categoria']}|{req['tipo']}"
            if clave not in total_combustible_necesario:
                total_combustible_necesario[clave] = 0
            total_combustible_necesario[clave] += req["cantidad"] * num_eventos

    # Verificar si hay suficiente combustible
    for clave, cantidad_necesaria in total_combustible_necesario.items():
        categoria, tipo = clave.split("|")
        stock_actual = 0
        
        # Sumar todos los recursos del mismo tipo
        for r in recursos:
            if (r["categoria"] == categoria and 
                r["tipo"] == tipo and
                r.get("es_combustible", False)):
                stock_actual += r["cantidad_disponible"]
        
        if stock_actual < cantidad_necesaria:
         faltante = cantidad_necesaria - stock_actual
         return False, None, f"❌ COMBUSTIBLE INSUFICIENTE\n\nPara {num_eventos} eventos necesitas {cantidad_necesaria}L de {categoria} {tipo}.\nStock actual: {stock_actual}L\nFaltan: {faltante}L.\n\n💡 NOTA: Ya verificamos el combustible al inicio, pero otros eventos\npueden haber consumido combustible durante la búsqueda.\nRevisa el calendario o rellena los tanques."
    # --- 2. BÚSQUEDA PROGRESIVA EN EL CALENDARIO ---
    fecha_inicio_busqueda = datetime.now().date()
    limite_busqueda = 730  # Buscamos en los próximos 2 años 
    
    ultimo_error = "No se encontró un hueco libre en el calendario."

    for dias_offset in range(limite_busqueda):
        fecha_candidata = fecha_inicio_busqueda + timedelta(days=dias_offset)
        puede_toda_la_serie = True
        eventos_simulados = []
        
        for i in range(num_eventos):
            f_actual = fecha_candidata + timedelta(days=i * intervalo_dias)
            
            # Validamos cada evento de la serie
            exito, msg, _ = procesar_creacion_evento(
                tipo_evento, str(f_actual.day), str(f_actual.month), str(f_actual.year),
                str(duracion_dias), recursos_seleccionados_nombres, recursos,
                eventos_planificados + eventos_simulados, tipos_evento_data, modo_validacion=True
            )
            
            if not exito:
                puede_toda_la_serie = False
                ultimo_error = f"En la fecha {f_actual.strftime('%d/%m/%Y')}: {msg}"
                break
            
            # Añadir a la simulación para que el siguiente evento vea los recursos ocupados
            eventos_simulados.append({
                "fecha_inicio": f_actual.strftime("%d/%m/%Y"),
                "fecha_fin": (f_actual + timedelta(days=duracion_dias-1)).strftime("%d/%m/%Y"),
                "recursos_usados": {n: 1 for n in recursos_seleccionados_nombres}
            })
            
        if puede_toda_la_serie:
            return True, fecha_candidata, f"✅ SERIE DISPONIBLE\n\nIniciando el {fecha_candidata.strftime('%d/%m/%Y')}.\nSe han verificado los recursos para los {num_eventos} eventos."

    return False, None, f"❌ IMPOSIBLE PROGRAMAR SERIE\n\n{ultimo_error}"