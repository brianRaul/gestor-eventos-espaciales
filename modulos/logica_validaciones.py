def validar_tipo_evento(tipo_evento, tipos_evento_data):
    """
    Valida que el tipo de evento sea válido
    """
    if not tipo_evento or tipo_evento == "Elige un tipo de evento":
        return False, "❌ Selecciona un tipo de evento"

    if tipo_evento not in tipos_evento_data:
        return False, "❌ Tipo de evento no encontrado"

    return True, ""

def validar_recursos_seleccionados(recursos_seleccionados_nombres, recursos):
    """
    Convierte nombres de recursos a objetos completos y valida
    """
    recursos_seleccionados = []
    for nombre_mostrar in recursos_seleccionados_nombres:
        for recurso in recursos:
            if recurso["nombre_mostrar"] == nombre_mostrar:
                recursos_seleccionados.append(recurso)
                break

    if not recursos_seleccionados:
        return False, "❌ Selecciona al menos un recurso", None

    return True, "", recursos_seleccionados

def validar_reglas_exclusion(evento_data, recursos_seleccionados):
    """
    Valida reglas de exclusión de recursos
    """
    reglas_exclusion = evento_data.get("reglas_exclusion", [])

    for regla in reglas_exclusion:
        categoria_prohibida = regla.get("categoria", "")
        tipos_prohibidos = regla.get("tipos_prohibidos", [])

        for recurso in recursos_seleccionados:
            if (
                recurso["categoria"] == categoria_prohibida
                and recurso["tipo"] in tipos_prohibidos
            ):
                return (
                    False,
                    f"⛔ RECURSO PROHIBIDO: '{recurso['nombre_mostrar']}' no está permitido para este evento.",
                )

    return True, ""

def validar_requisitos_coexistentes(evento_data, recursos_seleccionados):
    """
    Valida requisitos de recursos coexistentes
    """
    requisitos_coexistentes = evento_data.get("requisitos_coexistentes", [])

    for requisito in requisitos_coexistentes:
        categoria_principal = requisito.get("categoria", "")
        tipo_principal = requisito.get("tipo", "")
        requiere_lista = requisito.get("requiere", [])

        # Verificar si el recurso principal está seleccionado
        principal_seleccionado = False
        for recurso in recursos_seleccionados:
            if (
                recurso["categoria"] == categoria_principal
                and recurso["tipo"] == tipo_principal
            ):
                principal_seleccionado = True
                break

        if principal_seleccionado:
            # Verificar que todos los recursos requeridos estén seleccionados
            for requerido in requiere_lista:
                cat_req = requerido.get("categoria", "")
                tipo_req = requerido.get("tipo", "")
                encontrado = False

                for recurso in recursos_seleccionados:
                    if recurso["categoria"] == cat_req and recurso["tipo"] == tipo_req:
                        encontrado = True
                        break

                if not encontrado:
                    return (
                        False,
                        f"❌ '{categoria_principal} {tipo_principal}' requiere también '{cat_req} {tipo_req}'",
                    )

    return True, ""

def validar_recursos_opcionales(evento_data, recursos_seleccionados):
    """
    Valida si hay recursos seleccionados que no son necesarios ni prohibidos
    """
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

def es_error_solapamiento(mensaje_error):
    """
    Determina si un error es de solapamiento (recursos ocupados en fechas)
    """
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