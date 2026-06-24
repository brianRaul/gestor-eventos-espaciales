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