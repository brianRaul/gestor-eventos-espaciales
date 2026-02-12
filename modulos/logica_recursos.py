def obtener_recursos_por_categoria(recursos):
    """
    Agrupa recursos por categoría para facilitar su visualización
    """
    recursos_por_categoria = {}
    for recurso in recursos:
        categoria = recurso["categoria"]
        if categoria not in recursos_por_categoria:
            recursos_por_categoria[categoria] = []
        recursos_por_categoria[categoria].append(recurso)
    return recursos_por_categoria

def obtener_texto_recurso(recurso):
    """
    Genera el texto a mostrar para un recurso según su tipo
    """
    if recurso["es_combustible"]:
        # Para combustible: mostrar disponible/total
        texto = f"{recurso['nombre_mostrar']} - {recurso['cantidad_disponible']}/{recurso['cantidad_total']}L"
        return texto
    else:
        # Para equipos: solo mostrar cantidad total
        texto = f"{recurso['nombre_mostrar']} - {recurso['cantidad_total']} unidades"
        return texto

def obtener_color_recurso(recurso):
    """
    Determina el color según el tipo y disponibilidad del recurso
    """
    if recurso["es_combustible"]:
        disponible = recurso["cantidad_disponible"]
        total = recurso["cantidad_total"]
        
        if disponible <= 0:
            return "#FF5252"  # Rojo si no hay
        elif disponible < total * 0.2:
            return "#FF9800"  # Naranja si queda poco (<20%)
        else:
            return "#4CAF50"   # Verde si hay suficiente
    else:
        return "#F0F3F4"  # Gris claro para equipos

def obtener_recursos_recomendados(tipo_evento, tipos_evento_data, recursos):
    """
    Obtiene la lista de recursos recomendados para un tipo de evento
    """
    if tipo_evento not in tipos_evento_data:
        return []
    
    evento_data = tipos_evento_data[tipo_evento]
    recursos_requeridos = evento_data.get("recursos_requeridos", [])
    
    recursos_recomendados_nombres = []
    
    for req in recursos_requeridos:
        categoria_req = req["categoria"]
        tipo_req = req["tipo"]
        cantidad_req = req.get("cantidad", 1)
        
        # Buscar todos los recursos que coincidan con la categoría y tipo
        recursos_coincidentes = []
        for recurso in recursos:
            if recurso["categoria"] == categoria_req and recurso["tipo"] == tipo_req:
                recursos_coincidentes.append(recurso)
        
        if not recursos_coincidentes:
            continue
        
        # Para combustible
        if "COMBUSTIBLE" in categoria_req.upper():
            # Buscar un recurso con suficiente combustible
            recurso_suficiente = None
            for recurso in recursos_coincidentes:
                if recurso["cantidad_disponible"] >= cantidad_req:
                    recurso_suficiente = recurso
                    break
            
            if recurso_suficiente:
                recursos_recomendados_nombres.append(recurso_suficiente["nombre_mostrar"])
            else:
                # Si ninguno tiene suficiente, usar el primero
                recursos_recomendados_nombres.append(recursos_coincidentes[0]["nombre_mostrar"])
        else:
            # Para equipos
            # Buscar un recurso con cantidad_total suficiente
            recurso_suficiente = None
            for recurso in recursos_coincidentes:
                if recurso["cantidad_total"] >= cantidad_req:
                    recurso_suficiente = recurso
                    break
            
            if recurso_suficiente:
                recursos_recomendados_nombres.append(recurso_suficiente["nombre_mostrar"])
            else:
                # Si ninguno tiene suficiente, usar el primero
                recursos_recomendados_nombres.append(recursos_coincidentes[0]["nombre_mostrar"])
    
    return recursos_recomendados_nombres
