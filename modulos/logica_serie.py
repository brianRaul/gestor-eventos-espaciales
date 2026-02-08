def validar_datos_serie(tipo_evento, day, month, year, duracion_str, intervalo_str, repeticiones_str, tiene_recursos):
    """
    Valida los datos básicos para crear una serie de eventos
    
    Retorna:
    - valido: True/False
    - mensaje: mensaje de error/success
    - datos_validados: diccionario con datos convertidos o None
    """
    
    # 1. Validar tipo de evento
    if not tipo_evento or tipo_evento == "Elige un tipo de evento":
        return False, "❌ Selecciona un tipo de evento primero", None
    
    # 2. Validar campos de fecha y duración
    if not all([day, month, year, duracion_str]):
        return False, "❌ Completa todos los campos de fecha y duración", None
    
    # 3. Validar campos de recurrencia
    if not repeticiones_str:
        return False, "❌ Completa el campo de repeticiones", None
    
    # 4. Validar que sean números válidos
    try:
        # Convertir a números
        duracion = int(duracion_str)
        repeticiones = int(repeticiones_str)
        
        # Si intervalo está vacío, usar 7 por defecto
        intervalo = int(intervalo_str) if intervalo_str and intervalo_str.strip() else 7
        
        # Verificar que no sean números demasiado largos
        if len(str(duracion)) > 4 or len(str(repeticiones)) > 4 or len(str(intervalo)) > 4:
            return False, "❌ Número demasiado largo (máximo 4 dígitos)", None
        
        if duracion <= 0 or repeticiones <= 0 or intervalo <= 0:
            return False, "❌ Valores deben ser mayores a 0", None
        
    except ValueError:
        return False, "❌ Usa solo números válidos en todos los campos", None
    
    # 5. Validar que haya recursos seleccionados
    if not tiene_recursos:
        return False, "❌ Selecciona al menos un recurso", None
    
    # 6. Verificar límite de 1 año ANTES de confirmar
    duracion_total_aproximada = (repeticiones - 1) * intervalo + duracion
    
    if duracion_total_aproximada > 365:
        eventos_posibles = (365 - duracion) // intervalo + 1
        eventos_posibles = max(1, eventos_posibles)
        
        mensaje = f"❌ Serie demasiado larga (máximo {eventos_posibles} eventos)"
        return False, mensaje, None
    
    # 7. Devolver datos validados
    datos_validados = {
        "tipo_evento": tipo_evento,
        "day": day,
        "month": month,
        "year": year,
        "duracion": duracion,
        "intervalo": intervalo,
        "repeticiones": repeticiones,
        "fecha_str": f"{day}/{month}/{year}"
    }
    
    return True, "Datos válidos", datos_validados

def validar_datos_sugerencia_serie(tipo_evento, duracion_str, repeticiones_str, intervalo_str, tiene_recursos):
    """
    Valida los datos para sugerir una serie completa
    
    Retorna:
    - valido: True/False
    - mensaje: mensaje de error/success
    - datos_validados: diccionario con datos convertidos o None
    """
    
    # 1. Validar tipo de evento
    if tipo_evento == "Elige un tipo de evento" or not tipo_evento:
        return False, "❌ Selecciona un tipo de evento primero.", None
    
    # 2. Validar campos básicos
    if not duracion_str or not repeticiones_str:
        return False, "❌ Rellena Duración y Repeticiones primero.", None
    
    # 3. Validar que haya recursos
    if not tiene_recursos:
        return False, "❌ Selecciona al menos un recurso.", None
    
    # 4. Validar que sean números válidos
    try:
        dur_int = int(duracion_str)
        rep_int = int(repeticiones_str)
        
        # Si intervalo está vacío, usar 7 por defecto
        int_int = int(intervalo_str) if (intervalo_str and intervalo_str.strip()) else 7
        
        # Verificar que no sean números demasiado largos
        if len(str(dur_int)) > 4 or len(str(rep_int)) > 4 or len(str(int_int)) > 4:
            return False, "❌ Número demasiado largo (máximo 4 dígitos)", None
        
    except ValueError:
        return False, "❌ Duración, Repeticiones e Intervalo deben ser números.", None
    
    # 5. Verificar límite de 1 año
    duracion_total_aproximada = (rep_int - 1) * int_int + dur_int
    
    if duracion_total_aproximada > 365:
        eventos_posibles = (365 - dur_int) // int_int + 1
        eventos_posibles = max(1, eventos_posibles)
        
        mensaje = (
            f"❌ SERIE DEMASIADO LARGA\n\n"
            f"Duración total: {duracion_total_aproximada} días\n"
            f"Límite máximo: 365 días (1 año)\n\n"
            f"Máximo eventos posibles: {eventos_posibles}"
        )
        
        return False, mensaje, None
    
    # 6. Devolver datos validados
    datos_validados = {
        "tipo_evento": tipo_evento,
        "duracion": dur_int,
        "repeticiones": rep_int,
        "intervalo": int_int
    }
    
    return True, "Datos válidos para sugerencia", datos_validados

def generar_texto_confirmacion_serie(datos_serie):
    """
    Genera el texto para la confirmación de creación de serie
    """
    tipo_evento = datos_serie["tipo_evento"]
    duracion = datos_serie["duracion"]
    intervalo = datos_serie["intervalo"]
    repeticiones = datos_serie["repeticiones"]
    duracion_total = (repeticiones - 1) * intervalo + duracion
    
    return (
        f"¿Crear serie de {repeticiones} eventos?\n\n"
        f"• Tipo: {tipo_evento}\n"
        f"• Duración por evento: {duracion} días\n"
        f"• Intervalo: {intervalo} días\n"
        f"• Duración total: {duracion_total} días\n"
        f"• Primera fecha: {datos_serie.get('fecha_str', 'No especificada')}"
    )