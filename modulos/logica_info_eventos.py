import customtkinter as ctk
from datetime import datetime

def mostrar_info_eventos(parent, tipos_evento_data):
    """
    Args:
        parent: ventana principal (GestorEventos)
        tipos_evento_data: dict cargado desde eventos_predeterminados.json
    """
    ventana = ctk.CTkToplevel(parent)
    ventana.title("📚 Información de Eventos Predeterminados")
    ventana.geometry("700x600")
    ventana.transient(parent)
    ventana.lift()
    ventana.focus_force()

    # Título principal
    titulo = ctk.CTkLabel(
        ventana,
        text="TIPOS DE EVENTO DISPONIBLES",
        font=("Arial", 18, "bold"),
        text_color="#1087BF"
    )
    titulo.pack(pady=10)

    # Frame con scroll para todos los eventos
    frame_scroll = ctk.CTkScrollableFrame(ventana, width=660, height=500)
    frame_scroll.pack(pady=10, padx=10, fill="both", expand=True)

    if not tipos_evento_data:
        ctk.CTkLabel(
            frame_scroll,
            text="❌ No hay eventos predeterminados cargados.",
            font=("Arial", 14),
            text_color="red"
        ).pack(pady=20)
        return

    # Ordenar eventos alfabéticamente
    for nombre_evento, data in sorted(tipos_evento_data.items()):
        # Frame contenedor para cada evento (tarjeta)
        frame_evento = ctk.CTkFrame(frame_scroll, border_width=1, border_color="#555")
        frame_evento.pack(fill="x", pady=10, padx=5)

        # --- Cabecera: nombre del evento ---
        lbl_nombre = ctk.CTkLabel(
            frame_evento,
            text=f"🚀 {nombre_evento}",
            font=("Arial", 16, "bold"),
            text_color="#4CAF50",
            anchor="w"
        )
        lbl_nombre.pack(anchor="w", padx=10, pady=(10, 5))

        # --- Duración ---
        config = data.get("configuracion_evento", {})
        d_min = config.get("duracion_minima", "?")
        d_max = config.get("duracion_maxima", "?")
        lbl_duracion = ctk.CTkLabel(
            frame_evento,
            text=f"⏱️ Duración: {d_min} - {d_max} días",
            font=("Arial", 12),
            text_color="#DDD"
        )
        lbl_duracion.pack(anchor="w", padx=10, pady=2)

        # --- Recursos requeridos ---
        recursos = data.get("recursos_requeridos", [])
        if recursos:
            lbl_recursos_titulo = ctk.CTkLabel(
                frame_evento,
                text="📦 Recursos requeridos:",
                font=("Arial", 13, "bold"),
                text_color="#FF9800"
            )
            lbl_recursos_titulo.pack(anchor="w", padx=10, pady=(8, 2))

            for req in recursos:
                categoria = req.get("categoria", "")
                tipo = req.get("tipo", "")
                cantidad = req.get("cantidad", 1)
                unidad = "L" if "COMBUSTIBLE" in categoria.upper() else "uds"
                texto = f"  • {categoria} - {tipo}: {cantidad} {unidad}"
                lbl_recurso = ctk.CTkLabel(
                    frame_evento,
                    text=texto,
                    font=("Arial", 11),
                    text_color="#BBB"
                )
                lbl_recurso.pack(anchor="w", padx=20, pady=1)

        # --- Reglas de exclusión ---
        exclusiones = data.get("reglas_exclusion", [])
        if exclusiones:
            lbl_excl_titulo = ctk.CTkLabel(
                frame_evento,
                text="⛔ Reglas de exclusión:",
                font=("Arial", 13, "bold"),
                text_color="#FF5252"
            )
            lbl_excl_titulo.pack(anchor="w", padx=10, pady=(8, 2))

            for regla in exclusiones:
                cat = regla.get("categoria", "")
                tipos = regla.get("tipos_prohibidos", [])
                texto = f"  • {cat}: no puede usar {', '.join(tipos)}"
                lbl_excl = ctk.CTkLabel(
                    frame_evento,
                    text=texto,
                    font=("Arial", 11),
                    text_color="#BBB"
                )
                lbl_excl.pack(anchor="w", padx=20, pady=1)

        # --- Requisitos coexistentes ---
        coexist = data.get("requisitos_coexistentes", [])
        if coexist:
            lbl_coex_titulo = ctk.CTkLabel(
                frame_evento,
                text="🔗 Requisitos coexistentes:",
                font=("Arial", 13, "bold"),
                text_color="#2196F3"
            )
            lbl_coex_titulo.pack(anchor="w", padx=10, pady=(8, 2))

            for req in coexist:
                cat = req.get("categoria", "")
                tipo = req.get("tipo", "")
                requiere = req.get("requiere", [])
                reqs_text = ", ".join([f"{r['categoria']} {r['tipo']}" for r in requiere])
                texto = f"  • {cat} {tipo} requiere: {reqs_text}"
                lbl_coex = ctk.CTkLabel(
                    frame_evento,
                    text=texto,
                    font=("Arial", 11),
                    text_color="#BBB"
                )
                lbl_coex.pack(anchor="w", padx=20, pady=1)

        # Separador visual entre eventos
        ctk.CTkFrame(frame_evento, height=2, fg_color="#333").pack(fill="x", padx=5, pady=10)

    # Botón cerrar
    btn_cerrar = ctk.CTkButton(
        ventana,
        text="Cerrar",
        width=100,
        command=ventana.destroy
    )
    btn_cerrar.pack(pady=10)