import customtkinter as ctk
from datetime import datetime
import modulos.logica_combustible as lc
import modulos.logica_visualizaciones as lv
from modulos.funciones_datos import cargar_eventos_planificados


class GestorSincronizacion:

    # Clase que gestiona la sincronización de ventanas abiertas.

    def __init__(self, app):
        """
        Inicializa el gestor de sincronización.

        Args:
            app: Instancia principal de la aplicación (GestorEventos)
        """
        self.app = app
        self.ventanas_registradas = {
            "combustible": [],  # Ventanas de combustible abiertas
            "eventos": [],  # Ventanas de eventos planificados
            "eliminar": [],  # Ventanas de eliminación
            "series": [],  # Ventanas de series
        }

    def registrar_ventana(self, tipo_ventana, ventana):
        """
        Registra una ventana abierta para recibir actualizaciones.

        Args:
            tipo_ventana: Tipo de ventana ('combustible', 'eventos', etc.)
            ventana: Instancia de la ventana (CTkToplevel)
        """
        if tipo_ventana in self.ventanas_registradas:
            # Verificar que no esté ya registrada
            if ventana not in self.ventanas_registradas[tipo_ventana]:
                self.ventanas_registradas[tipo_ventana].append(ventana)
                print(f"✅ Ventana {tipo_ventana} registrada")
        else:
            print(f"⚠️ Tipo de ventana desconocido: {tipo_ventana}")

    def eliminar_ventana(self, tipo_ventana, ventana):
        """
        Elimina una ventana del registro.

        Args:
            tipo_ventana: Tipo de ventana
            ventana: Instancia de la ventana
        """
        if tipo_ventana in self.ventanas_registradas:
            if ventana in self.ventanas_registradas[tipo_ventana]:
                self.ventanas_registradas[tipo_ventana].remove(ventana)
                print(f"✅ Ventana {tipo_ventana} eliminada del registro")

    def limpiar_ventanas_cerradas(self):
        """
        Limpia automáticamente las ventanas que ya fueron cerradas.
        """
        for tipo_ventana, ventanas in self.ventanas_registradas.items():
            ventanas_validas = []
            for ventana in ventanas:
                try:
                    # Verificar si la ventana aún existe
                    if hasattr(ventana, "winfo_exists") and ventana.winfo_exists():
                        ventanas_validas.append(ventana)
                except:
                    # Si hay error, la ventana ya no existe
                    pass
            self.ventanas_registradas[tipo_ventana] = ventanas_validas

    def actualizar_ventanas_tipo(self, tipo_ventana, datos=None):
        self.limpiar_ventanas_cerradas()

        if tipo_ventana not in self.ventanas_registradas:
            return

        ventanas_actualizadas = 0

        for ventana in self.ventanas_registradas[tipo_ventana]:
            try:
                if tipo_ventana == "combustible":
                    self._actualizar_ventana_combustible(ventana, datos)
                elif tipo_ventana == "eventos":
                    self._actualizar_ventana_eventos(ventana, datos)
                elif tipo_ventana == "eliminar":  # <-- NUEVO
                    self._actualizar_ventana_eliminar(ventana, datos)

                ventanas_actualizadas += 1
            except Exception as e:
                print(f"❌ Error actualizando ventana {tipo_ventana}: {e}")

        print(
            f"✅ Actualizadas {ventanas_actualizadas} ventanas de tipo {tipo_ventana}"
        )

    def _actualizar_ventana_combustible(self, ventana, datos=None):
        """
        Actualiza una ventana de combustible específica.

        Args:
            ventana: Ventana de combustible
            datos: Datos adicionales (opcional)
        """
        # Limpiar todos los widgets de la ventana
        for widget in ventana.winfo_children():
            widget.destroy()

        # Recrear la ventana con datos actualizados
        self._crear_contenido_combustible(ventana)

    def _actualizar_ventana_eventos(self, ventana, datos=None):

        # Actualiza una ventana de eventos específica - ACTUALIZA CONTENIDO

        # Limpiar todos los widgets de la ventana
        for widget in ventana.winfo_children():
            widget.destroy()

        # Volver a crear el contenido con los eventos actualizados
        self._crear_contenido_eventos(ventana)

    def _crear_contenido_combustible(self, ventana):
        """
        Crea el contenido de una ventana de combustible.
        Similar al código original en ver_combustible().
        """
        # Título
        ctk.CTkLabel(
            ventana,
            text="📊 ESTADO DE COMBUSTIBLE",
            font=("Arial", 16, "bold"),
            text_color="#FF9800",
        ).pack(pady=10)

        # Frame con scroll
        frame_scroll = ctk.CTkScrollableFrame(ventana, width=350, height=250)
        frame_scroll.pack(pady=10, padx=10)

        # Obtener combustibles
        combustibles = lc.obtener_combustibles(self.app.recursos)

        if not combustibles:
            ctk.CTkLabel(
                frame_scroll, text="No hay sistemas de combustible", text_color="gray"
            ).pack(pady=20)
        else:
            for recurso in combustibles:
                porcentaje = lc.calcular_porcentaje_combustible(recurso)
                color = lc.obtener_color_porcentaje(porcentaje)

                frame_tanque = ctk.CTkFrame(frame_scroll)
                frame_tanque.pack(fill="x", pady=5, padx=5)

                texto = f"• {recurso['nombre_mostrar']}: {recurso['cantidad_disponible']:,}/{recurso['cantidad_total']:,}L ({porcentaje:.1f}%)"
                ctk.CTkLabel(
                    frame_tanque, text=texto, font=("Arial", 11), text_color=color
                ).pack(anchor="w", padx=10, pady=5)

            tipo_evento_actual = self.app.combo_evento.get()

            if tipo_evento_actual and tipo_evento_actual != "Elige un tipo de evento":
                advertencias = lc.obtener_advertencias_combustible_evento(
                    tipo_evento_actual, combustibles, self.app.tipos_evento_data
                )

                for advertencia in advertencias:
                    frame_advertencia = ctk.CTkFrame(ventana)
                    frame_advertencia.pack(pady=5, padx=20, fill="x")

                    ctk.CTkLabel(
                        frame_advertencia,
                        text=f"⚠️ ATENCIÓN: Evento '{tipo_evento_actual}'",
                        text_color="#FF9800",
                        font=("Arial", 12, "bold"),
                    ).pack(pady=2)

                    ctk.CTkLabel(
                        frame_advertencia,
                        text=f"Faltan {advertencia['faltante']:,}L de {advertencia['categoria']} {advertencia['tipo']}",
                        text_color="#FF5252",
                        font=("Arial", 11),
                    ).pack(pady=2)

                    ctk.CTkLabel(
                        frame_advertencia,
                        text=f"Se necesitan {advertencia['necesario']:,}L por evento",
                        text_color="gray",
                        font=("Arial", 10),
                    ).pack(pady=2)

        # Botón para cerrar
        ctk.CTkButton(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)

    def notificar_cambio_combustible(self):
        """
        Notifica que el combustible ha cambiado y actualiza todas las ventanas.
        """
        self.actualizar_ventanas_tipo("combustible")

    def notificar_cambio_eventos(self):
        """
        Notifica que los eventos han cambiado y actualiza todas las ventanas.
        """
        self.actualizar_ventanas_tipo("eventos")
        self.actualizar_ventanas_tipo("eliminar")

    def notificar_todos_los_cambios(self):
        """
        Notifica todos los tipos de cambios.
        Útil cuando se realizan múltiples modificaciones.
        """
        self.notificar_cambio_combustible()
        self.notificar_cambio_eventos()

    def crear_ventana_eventos(
        self, parent, eventos_planificados, mostrar_recursos_callback
    ):
        """
        Crea una ventana de eventos planificados y la registra automáticamente.
        """
        ventana_eventos = ctk.CTkToplevel(parent)
        ventana_eventos.title("📋 Eventos Planificados")
        ventana_eventos.geometry("420x600")

        ventana_eventos.transient(parent)
        ventana_eventos.lift()
        ventana_eventos.focus_force()

        # Registrar la ventana
        self.registrar_ventana("eventos", ventana_eventos)

        # Configurar cierre
        def on_close():
            self.eliminar_ventana("eventos", ventana_eventos)
            ventana_eventos.destroy()

        ventana_eventos.protocol("WM_DELETE_WINDOW", on_close)

        # Llamar a _crear_contenido_eventos (NO usar el callback directamente)
        self._crear_contenido_eventos(ventana_eventos)

        return ventana_eventos

    def _crear_contenido_eventos(self, ventana):

        # Recargar eventos desde archivo
        eventos_actualizados = cargar_eventos_planificados()
        self.app.eventos_planificados = eventos_actualizados

        # Título
        titulo = ctk.CTkLabel(
            ventana, text="EVENTOS PLANIFICADOS", font=("Arial", 16, "bold")
        )
        titulo.pack(pady=10)

        # Frame con scroll (más grande para que quepan más eventos)
        frame_contenedor = ctk.CTkScrollableFrame(ventana, width=550, height=450)
        frame_contenedor.pack(pady=10, padx=10, fill="both", expand=True)

        # Si no hay eventos
        if not self.app.eventos_planificados:
            sin_eventos = ctk.CTkLabel(
                frame_contenedor,
                text=" No hay eventos planificados todavía.",
                font=("Arial", 12),
                text_color="gray",
            )
            sin_eventos.pack(pady=20)
            btn_cerrar = ctk.CTkButton(
                ventana, text="Cerrar", width=100, command=ventana.destroy
            )
            btn_cerrar.pack(pady=10)
            return

        # Ordenar eventos por fecha (más antiguos primero)
        eventos_ordenados = sorted(
            self.app.eventos_planificados,
            key=lambda x: datetime.strptime(x["fecha_inicio"], "%d/%m/%Y"),
        )

        mes_actual = None

        for i, evento in enumerate(eventos_ordenados, 1):
            # Obtener mes y año del evento
            fecha_obj = datetime.strptime(evento["fecha_inicio"], "%d/%m/%Y")
            mes_anno = fecha_obj.strftime("%B %Y")  # Ejemplo: "March 2026"

            # Si cambia el mes, mostrar encabezado
            if mes_anno != mes_actual:
                mes_actual = mes_anno
                lbl_mes = ctk.CTkLabel(
                    frame_contenedor,
                    text=f"📅 {mes_anno}",
                    font=("Arial", 14, "bold"),
                    text_color="#4CAF50",
                )
                lbl_mes.pack(anchor="w", pady=(15, 5), padx=5)

            # --- MISMO FORMATO DE CADA EVENTO (sin cambios) ---
            frame_evento = ctk.CTkFrame(frame_contenedor)
            frame_evento.pack(fill="x", pady=5, padx=5)

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

            # Botón ver recursos
            btn_recursos = ctk.CTkButton(
                contenido_evento,
                text="📦 Ver Recursos",
                width=100,
                height=30,
                fg_color="#2196F3",
                hover_color="#1976D2",
                command=lambda ev=evento: lv.mostrar_recursos_evento(ventana, ev),
            )
            btn_recursos.grid(
                row=0, column=1, rowspan=4, padx=(20, 0), pady=5, sticky="e"
            )
            # -------------------------------------------------

        # Botón para cerrar
        btn_cerrar = ctk.CTkButton(
            ventana, text="Cerrar", width=100, command=ventana.destroy
        )
        btn_cerrar.pack(pady=10)

    def _actualizar_ventana_eliminar(self, ventana, datos=None):

        # Actualiza una ventana de eliminación de eventos.
        # 1. Recargar eventos desde archivo

        eventos_actualizados = cargar_eventos_planificados()
        self.app.eventos_planificados = eventos_actualizados

        # 2. Obtener el frame scrollable guardado en la ventana
        if hasattr(ventana, "frame_scroll_eliminar"):
            frame_scroll = ventana.frame_scroll_eliminar
        else:
            # Fallback: buscarlo en los hijos (por si acaso)
            frame_scroll = None
            for child in ventana.winfo_children():
                if isinstance(child, ctk.CTkScrollableFrame):
                    frame_scroll = child
                    break

        if frame_scroll is None:
            print("⚠️ No se encontró el frame scrollable en ventana de eliminación")
            return

        # 3. Limpiar SOLO el contenido, NO destruir el frame_scroll
        for widget in frame_scroll.winfo_children():
            widget.destroy()

        # 4. Recrear el contenido (checkboxes)
        self._crear_contenido_eliminar(ventana, frame_scroll)

    def _crear_contenido_eliminar(self, ventana, frame_scroll):

        # Crea el contenido de la ventana de eliminación (checkboxes de eventos).

        if not self.app.eventos_planificados:
            ctk.CTkLabel(
                frame_scroll,
                text=" No hay eventos planificados todavía.",
                font=("Arial", 12),
                text_color="gray",
            ).pack(pady=20)
            return

        # ----- CHECKBOX "SELECCIONAR TODOS" -----
        frame_seleccion_todos = ctk.CTkFrame(frame_scroll)
        frame_seleccion_todos.pack(fill="x", pady=(0, 10), padx=5)

        ventana.var_seleccionar_todos = ctk.BooleanVar(value=False)

        checkbox_seleccionar_todos = ctk.CTkCheckBox(
            frame_seleccion_todos,
            text="📋 SELECCIONAR TODOS LOS EVENTOS",
            variable=ventana.var_seleccionar_todos,
            onvalue=True,
            offvalue=False,
            font=("Arial", 12, "bold"),
            command=lambda: self._toggle_todos_eliminar(
                ventana, ventana.var_seleccionar_todos
            ),
        )
        checkbox_seleccionar_todos.pack(anchor="w", padx=5)

        # ----- LISTA DE EVENTOS -----
        ventana.checkboxes_eliminar = []

        for i, evento in enumerate(self.app.eventos_planificados, 1):
            var_checkbox = ctk.BooleanVar(value=False)
            ventana.checkboxes_eliminar.append(var_checkbox)

            fecha_inicio = evento.get("fecha_inicio", "N/A")
            duracion = evento.get("duracion_dias", 1)
            recursos_count = len(
                evento.get("recursos", evento.get("recursos_detalle", []))
            )
            texto_evento = f"Evento #{i}: {evento['tipo']} - {fecha_inicio} ({duracion} días, {recursos_count} recursos)"

            frame_evento = ctk.CTkFrame(frame_scroll)
            frame_evento.pack(fill="x", pady=2, padx=5)

            checkbox = ctk.CTkCheckBox(
                frame_evento,
                text=texto_evento,
                variable=var_checkbox,
                onvalue=True,
                offvalue=False,
                font=("Arial", 11),
                width=500,
            )
            checkbox.pack(anchor="w", padx=10, pady=5)

    def _toggle_todos_eliminar(self, ventana, var_todos):
        """Activa/desactiva todos los checkboxes de la ventana de eliminación."""
        estado = var_todos.get()
        if hasattr(ventana, "checkboxes_eliminar"):
            for var in ventana.checkboxes_eliminar:
                var.set(estado)


# Funciones de conveniencia para uso directo
def crear_gestor_sincronizacion(app):
    """
    Crea y retorna una instancia del gestor de sincronización.

    Args:
        app: Instancia principal de la aplicación
    """
    return GestorSincronizacion(app)


def registrar_ventana_combustible(gestor, ventana):
    """
    Registra una ventana de combustible.

    Args:
        gestor: Instancia de GestorSincronizacion
        ventana: Ventana de combustible
    """
    gestor.registrar_ventana("combustible", ventana)


def registrar_ventana_eventos(gestor, ventana):
    """
    Registra una ventana de eventos.

    Args:
        gestor: Instancia de GestorSincronizacion
        ventana: Ventana de eventos
    """
    gestor.registrar_ventana("eventos", ventana)
