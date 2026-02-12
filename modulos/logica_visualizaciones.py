import customtkinter as ctk

def mostrar_eventos_planificados(
    parent, eventos_planificados, mostrar_recursos_callback
):
    """
    Muestra una ventana con la lista de eventos planificados

    Args:
        parent: ventana padre (main window)
        eventos_planificados: lista de eventos a mostrar
        mostrar_recursos_callback: función para mostrar recursos de un evento
    """
    # Crear una nueva ventana emergente
    ventana_eventos = ctk.CTkToplevel(parent)
    ventana_eventos.title("📋 Eventos Planificados")
    ventana_eventos.geometry("440x500")

    ventana_eventos.transient(parent)  # Hace que sea ventana hija
    ventana_eventos.lift()  # Trae la ventana al frente
    ventana_eventos.focus_force()  # Enfoca la ventana

    # Título
    titulo = ctk.CTkLabel(
        ventana_eventos, text="EVENTOS PLANIFICADOS", font=("Arial", 16, "bold")
    )
    titulo.pack(pady=10)

    # Frame para contener los eventos con scroll
    frame_contenedor = ctk.CTkScrollableFrame(ventana_eventos, width=550, height=400)
    frame_contenedor.pack(pady=10, padx=10, fill="both", expand=True)

    # Verificar si hay eventos
    if not eventos_planificados:
        sin_eventos = ctk.CTkLabel(
            frame_contenedor,
            text=" No hay eventos planificados todavía.",
            font=("Arial", 12),
            text_color="gray",
        )
        sin_eventos.pack(pady=20)
    else:
        # Mostrar cada evento
        for i, evento in enumerate(eventos_planificados, 1):
            # Crear un frame para cada evento (como una tarjeta)
            frame_evento = ctk.CTkFrame(frame_contenedor)
            frame_evento.pack(fill="x", pady=5, padx=5)

            # Contenido del evento
            contenido_evento = ctk.CTkFrame(frame_evento)
            contenido_evento.pack(fill="x", padx=10, pady=5)

            # Número del evento
            lbl_numero = ctk.CTkLabel(
                contenido_evento, text=f"Evento #{i}", font=("Arial", 12, "bold")
            )
            lbl_numero.grid(row=0, column=0, sticky="w", pady=(0, 5))

            # Tipo de evento
            lbl_tipo = ctk.CTkLabel(
                contenido_evento, text=f"Tipo: {evento['tipo']}", font=("Arial", 12)
            )
            lbl_tipo.grid(row=1, column=0, sticky="w")

            # Fecha de inicio y fin
            fecha_inicio = evento.get("fecha_inicio", evento.get("fecha", "N/A"))
            fecha_fin = evento.get("fecha_fin", "N/A")

            lbl_fecha = ctk.CTkLabel(
                contenido_evento,
                text=f"📅 Inicio: {fecha_inicio} | Fin: {fecha_fin}",
                font=("Arial", 12),
            )
            lbl_fecha.grid(row=2, column=0, sticky="w")

            # Duración
            lbl_duracion = ctk.CTkLabel(
                contenido_evento,
                text=f"⏱️ Duración: {evento.get('duracion_dias', 1)} días",
                font=("Arial", 11),
            )
            lbl_duracion.grid(row=3, column=0, sticky="w")

            # Botón para ver recursos
            btn_recursos = ctk.CTkButton(
                contenido_evento,
                text="📦 Ver Recursos",
                width=100,
                height=30,
                fg_color="#2196F3",
                hover_color="#1976D2",
                command=lambda ev=evento: mostrar_recursos_callback(
                    ventana_eventos, ev
                ),
            )
            btn_recursos.grid(
                row=0, column=1, rowspan=4, padx=(20, 0), pady=5, sticky="e"
            )

    # Botón para cerrar la ventana
    btn_cerrar = ctk.CTkButton(
        ventana_eventos, text="Cerrar", width=100, command=ventana_eventos.destroy
    )
    btn_cerrar.pack(pady=10)

def mostrar_recursos_evento(parent, evento):
    """
    Muestra los recursos utilizados en un evento específico

    Args:
        parent: ventana padre
        evento: diccionario con la información del evento
    """
    # Crear ventana emergente
    ventana_recursos = ctk.CTkToplevel(parent)
    ventana_recursos.title(f"📦 Recursos del Evento: {evento['tipo']}")
    ventana_recursos.geometry("500x500")

    ventana_recursos.transient(parent)  # Hace que sea hija de ventana_eventos
    ventana_recursos.lift()  # Trae la ventana al frente
    ventana_recursos.focus_force()  # Enfoca la ventana

    # Título
    titulo = ctk.CTkLabel(
        ventana_recursos,
        text=f"RECURSOS UTILIZADOS: {evento['tipo']}",
        font=("Arial", 16, "bold"),
    )
    titulo.pack(pady=10)

    # Información del evento
    info_frame = ctk.CTkFrame(ventana_recursos)
    info_frame.pack(pady=5, padx=20, fill="x")

    ctk.CTkLabel(
        info_frame,
        text=f"📅 Fecha: {evento.get('fecha_inicio', 'N/A')} | Duración: {evento.get('duracion_dias', 1)} días",
        font=("Arial", 12),
    ).pack(pady=5)

    # Frame con scroll para recursos
    frame_scroll = ctk.CTkScrollableFrame(ventana_recursos, width=450, height=250)
    frame_scroll.pack(pady=10, padx=10, fill="both", expand=True)

    # Verificar qué campos de recursos existen
    if "recursos_detalle" in evento:
        # Usar recursos_detalle aunque esté vacío
        recursos = evento["recursos_detalle"]
    elif "recursos" in evento:
        # Para compatibilidad con eventos antiguos
        recursos = evento["recursos"]
    elif "recursos_utilizados" in evento:
        # Para compatibilidad con eventos muy antiguos
        recursos = evento["recursos_utilizados"]
    else:
        # No hay recursos en ningún formato
        recursos = []

    if not recursos:
        ctk.CTkLabel(
            frame_scroll,
            text="ℹ️ Este evento no tiene información de recursos\n(o fue creado antes de implementar esta función)",
            text_color="orange",
            font=("Arial", 12),
        ).pack(pady=50)

        # Mostrar el evento completo para depuración
        ctk.CTkLabel(
            frame_scroll,
            text=f"Campos disponibles en el evento: {list(evento.keys())}",
            text_color="gray",
            font=("Arial", 10),
        ).pack(pady=10)
    else:
        # Contadores
        recursos_combustible = 0
        recursos_equipos = 0

        # Mostrar cada recurso
        for recurso in recursos:
            # Crear frame para cada recurso
            frame_recurso = ctk.CTkFrame(frame_scroll)
            frame_recurso.pack(fill="x", pady=3, padx=5)

            # Determinar si es combustible
            es_combustible = recurso.get("es_combustible", False)
            if not es_combustible:
                # Intentar detectar por nombre o categoría
                nombre = recurso.get("nombre_mostrar", "").lower()
                categoria = recurso.get("categoria", "").lower()
                if (
                    "combustible" in nombre
                    or "combustible" in categoria
                    or "fuel" in nombre
                ):
                    es_combustible = True

            # Color según tipo
            if es_combustible:
                color = "#FF9800"  # Naranja para combustible
                icono = "⛽"
                recursos_combustible += 1
                cantidad = recurso.get("cantidad", 1)
                cantidad_texto = f"{cantidad}L"
            else:
                color = "#2196F3"  # Azul para equipos
                icono = "🛠️"
                recursos_equipos += 1
                cantidad = recurso.get("cantidad", 1)
                cantidad_texto = f"{cantidad} unidades"

            # Obtener nombre para mostrar
            nombre_mostrar = recurso.get(
                "nombre_mostrar", recurso.get("nombre", "Recurso sin nombre")
            )

            # Mostrar información del recurso
            texto_recurso = f"{icono} {nombre_mostrar} - {cantidad_texto}"
            lbl_recurso = ctk.CTkLabel(
                frame_recurso,
                text=texto_recurso,
                font=("Arial", 11),
                text_color=color,
            )
            lbl_recurso.pack(anchor="w", padx=10, pady=5)

        # Mostrar resumen
        resumen_frame = ctk.CTkFrame(ventana_recursos)
        resumen_frame.pack(pady=5, padx=20, fill="x")

        resumen_text = f"📊 Total: {len(recursos)} recursos"
        if recursos_combustible > 0:
            resumen_text += f" | ⛽ Combustible: {recursos_combustible}"
        if recursos_equipos > 0:
            resumen_text += f" | 🛠️ Equipos: {recursos_equipos}"

        ctk.CTkLabel(resumen_frame, text=resumen_text, font=("Arial", 11)).pack(pady=5)

    # Botón para cerrar
    btn_cerrar = ctk.CTkButton(
        ventana_recursos, text="Cerrar", width=100, command=ventana_recursos.destroy
    )
    btn_cerrar.pack(pady=10)
    
def mostrar_recursos_opcionales(parent, recursos_opcionales):
    """
    Muestra una ventana emergente con la lista de recursos opcionales seleccionados.

    Args:
        parent: ventana principal (GestorEventos) o cualquier Toplevel padre
        recursos_opcionales: lista de dicts o strings con nombres de recursos
    """
    ventana = ctk.CTkToplevel(parent)
    ventana.title("ℹ️ Recursos Opcionales")
    ventana.geometry("400x300")
    ventana.transient(parent)
    ventana.lift()
    ventana.focus_force()

    ctk.CTkLabel(
        ventana,
        text="Recursos opcionales incluidos:",
        font=("Arial", 14, "bold")
    ).pack(pady=10)

    frame_scroll = ctk.CTkScrollableFrame(ventana, width=350, height=200)
    frame_scroll.pack(pady=10, padx=10, fill="both", expand=True)

    for recurso in recursos_opcionales:
        nombre = recurso["nombre_mostrar"] if isinstance(recurso, dict) else recurso
        ctk.CTkLabel(
            frame_scroll,
            text=f"• {nombre}",
            font=("Arial", 12)
        ).pack(anchor="w", padx=10, pady=2)

    ctk.CTkButton(
        ventana,
        text="Cerrar",
        command=ventana.destroy
    ).pack(pady=10)
