def obtener_combustibles(recursos):
    """
    Filtra y retorna solo los recursos que son combustibles
    """
    combustibles = []
    for recurso in recursos:
        if (
            recurso.get("es_combustible", False)
            or "COMBUSTIBLE" in recurso.get("categoria", "").upper()
        ):
            combustibles.append(recurso)
    return combustibles

def rellenar_combustible_logica(recursos):
    """
    Rellena todos los combustibles y retorna:
    - litros_agregados: total de litros rellenados
    - recursos_modificados: lista de recursos modificados
    """
    litros_agregados = 0
    recursos_modificados = []
    
    for recurso in recursos:
        if (
            recurso.get("es_combustible", False)
            or "COMBUSTIBLE" in recurso.get("categoria", "").upper()
        ):
            disponible = recurso["cantidad_disponible"]
            total = recurso["cantidad_total"]
            
            if disponible < total:
                litros_faltantes = total - disponible
                recurso["cantidad_disponible"] = total
                litros_agregados += litros_faltantes
                recursos_modificados.append(recurso)
    
    return litros_agregados, recursos_modificados

def verificar_combustible_para_serie_logica(tipo_evento, repeticiones, recursos, tipos_evento_data):
    """
    Verifica si hay combustible suficiente para una serie de eventos
    """
    if tipo_evento not in tipos_evento_data:
        return False, "Tipo de evento no válido"

    evento_data = tipos_evento_data[tipo_evento]
    recursos_requeridos = evento_data.get("recursos_requeridos", [])

    # Calcular combustible total necesario
    combustible_necesario = {}

    for req in recursos_requeridos:
        if "COMBUSTIBLE" in req["categoria"].upper():
            clave = f"{req['categoria']}|{req['tipo']}"
            if clave not in combustible_necesario:
                combustible_necesario[clave] = 0
            combustible_necesario[clave] += req["cantidad"] * repeticiones

    # Verificar stock disponible
    for clave, cantidad_necesaria in combustible_necesario.items():
        categoria, tipo = clave.split("|")
        stock_disponible = 0

        # Sumar todo el combustible del mismo tipo
        for recurso in recursos:
            if (
                recurso.get("es_combustible", False)
                and recurso["categoria"] == categoria
                and recurso["tipo"] == tipo
            ):
                stock_disponible += recurso["cantidad_disponible"]

        if stock_disponible < cantidad_necesaria:
            faltante = cantidad_necesaria - stock_disponible
            return False, f"⛽ Faltan {faltante}L de {categoria} {tipo}"

    return True, ""

def obtener_advertencias_combustible_evento(tipo_evento, combustibles, tipos_evento_data):
    """
    Obtiene advertencias de combustible para un tipo de evento específico
    """
    advertencias = []
    
    if tipo_evento not in tipos_evento_data:
        return advertencias
    
    evento_data = tipos_evento_data[tipo_evento]
    recursos_requeridos = evento_data.get("recursos_requeridos", [])
    
    for req in recursos_requeridos:
        if "COMBUSTIBLE" in req["categoria"].upper():
            for recurso_comb in combustibles:
                if (
                    recurso_comb["categoria"] == req["categoria"]
                    and recurso_comb["tipo"] == req["tipo"]
                ):
                    if recurso_comb["cantidad_disponible"] < req["cantidad"]:
                        faltante = req["cantidad"] - recurso_comb["cantidad_disponible"]
                        advertencias.append({
                            "recurso": recurso_comb["nombre_mostrar"],
                            "categoria": req["categoria"],
                            "tipo": req["tipo"],
                            "necesario": req["cantidad"],
                            "disponible": recurso_comb["cantidad_disponible"],
                            "faltante": faltante
                        })
                    break
    
    return advertencias

def calcular_porcentaje_combustible(recurso):
    """
    Calcula el porcentaje de combustible disponible
    """
    disponible = recurso["cantidad_disponible"]
    total = recurso["cantidad_total"]
    return (disponible / total * 100) if total > 0 else 0

def obtener_color_porcentaje(porcentaje):
    """
    Determina el color basado en el porcentaje de combustible
    """
    if porcentaje >= 80:
        return "#4CAF50"
    elif porcentaje >= 30:
        return "#FF9800"
    else:
        return "#F44336"