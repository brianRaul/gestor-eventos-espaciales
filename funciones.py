def crear_evento(self):
    """Crear un nuevo evento con los datos ingresados"""
    # Obtener datos
    tipo_evento = self.combo_evento.get()
    dia = self.entry_dia.get()
    mes = self.entry_mes.get()
    anio = self.entry_anio.get()
    
    # Validar que todos los campos estén completos
    if tipo_evento == "Elige un tipo de evento" or not tipo_evento:
        self.lbl_info.configure(text="❌ Debes seleccionar un tipo de evento", text_color="red")
        return
    
    if not (dia and mes and anio):
        self.lbl_info.configure(text="❌ Debes completar la fecha", text_color="red")
        return
    
    # Validar formato de fecha (solo básico)
    try:
        dia = int(dia)
        mes = int(mes)
        anio = int(anio)
        
        if not (1 <= dia <= 31 and 1 <= mes <= 12 and 2000 <= anio <= 2100):
            raise ValueError
    except ValueError:
        self.lbl_info.configure(text="❌ Fecha inválida. Usa números válidos", text_color="red")
        return
    
    # Obtener recursos predeterminados para el tipo de evento seleccionado
    recursos = []
    for evento_data in self.tipos_evento_data:
        if evento_data["nombre"] == tipo_evento:
            recursos = evento_data.get("recursos", [])
            break
    
    # Crear el evento
    nuevo_evento = {
        "tipo": tipo_evento,
        "fecha": f"{dia:02d}/{mes:02d}/{anio}",
        "recursos": recursos
    }
    
    # Agregar a la lista
    self.eventos_creados.append(nuevo_evento)
    
    # Actualizar interfaz
    self.actualizar_contador()
    self.lbl_info.configure(
        text=f"✅ Evento '{tipo_evento}' creado para el {dia:02d}/{mes:02d}/{anio}",
        text_color="green"
    )
    
    # Limpiar campos
    self.entry_dia.delete(0, 'end')
    self.entry_mes.delete(0, 'end')
    self.entry_anio.delete(0, 'end')
    
    # Mostrar en consola (para depuración)
    print(f"Evento creado: {nuevo_evento}")
    print(f"Total eventos: {len(self.eventos_creados)}")
    
