import customtkinter as ctk
import json


class GestorEventosSimple(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Configurar ventana
        self.title("Gestor de Eventos Espaciales")
        self.geometry("600x800")

        self.evento_seleccionado = None  # Para guardar el evento actual seleccionado

        self.tipos_evento_data = self.cargar_eventos_desde_json()

        # Extraer solo los nombres para el ComboBox
        self.tipos_evento = list(self.tipos_evento_data.keys())
        self.recursos = self.cargar_recursos_desde_json()

        # Cargar eventos planificados
        self.eventos_planificados = self.cargar_eventos_planificados()

        # Crear la interfaz
        self.crear_interfaz()

    def cargar_eventos_desde_json(self):
        try:
            with open("eventos_predeterminados.json", "r", encoding="utf-8") as f:
                datos = json.load(f)
                return datos
        except FileNotFoundError:
            return {
                "Despegue": ["COHETE", "PLATAFORMA"],
                "Prueba": ["LABORATORIO", "EQUIPO"],
                "Ensayo": ["SISTEMA", "CONTROL"],
            }

    def cargar_recursos_desde_json(self):
        """Cargar recursos desde archivo JSON"""
        try:
            with open("recursos.json", "r", encoding="utf-8") as f:
                datos = json.load(f)
                self.datos = datos["recursos"]
                return datos.get(
                    "recursos",
                    [
                        {"nombre": "COHETE", "cantidad": 5},
                        {"nombre": "PLATAFORMA", "cantidad": 3},
                    ],
                )
        except FileNotFoundError:
            return [
                {"nombre": "COHETE", "cantidad": 5},
                {"nombre": "PLATAFORMA", "cantidad": 3},
                {"nombre": "LABORATORIO", "cantidad": 2},
                {"nombre": "EQUIPO", "cantidad": 10},
            ]

    def cargar_eventos_planificados(self):

        try:
            with open("eventos_planificados.json", "r", encoding="utf-8") as f:
                self.eventos_creados = json.load(f)
            print(
                f"✅ Eventos cargados desde JSON: {len(self.eventos_creados)} eventos"
            )

        except FileNotFoundError:
            print("📄 Archivo de eventos no encontrado, se creará uno nuevo")
            self.eventos_creados = []
        except Exception as e:
            print(f"❌ Error al cargar JSON: {e}")
            self.eventos_creados = []

    def guardar_eventos_en_json(self):

        try:
            with open("eventos_planificados.json", "w", encoding="utf-8") as f:
                json.dump(self.eventos_creados, f, ensure_ascii=False, indent=4)
            print(f"✅ Eventos guardados en JSON: {len(self.eventos_creados)} eventos")
        except Exception as e:
            print(f"❌ Error al guardar en JSON: {e}")

    def actualizar_contador(self):
        total = len(self.eventos_creados)
        self.lbl_contador.configure(text=f"Eventos planificados: {total}")

    def guardar_recursos(self):
        try:
            with open("recursos.json", "w", encoding="utf-8") as f:
                json.dump({"recursos": self.datos}, f, ensure_ascii=False, indent=1)
        except Exception as e:
            print(f"Error al actualizar la cantidad de recursos: {e}")

    # ========== Crear checkboxes de recursos ==========
    def crear_checkboxes_recursos(self):
        # Limpiar checkboxes anteriores si existen
        for widget in self.frame_checkboxes.winfo_children():
            widget.destroy()

        self.checkbox_vars = {}  # Diccionario para guardar las variables BooleanVar

        # Crear un checkbox por cada recurso
        for recurso in self.recursos:
            var = ctk.BooleanVar(value=False)  # Todos inician desmarcados
            self.checkbox_vars[recurso["nombre"]] = var

            checkbox = ctk.CTkCheckBox(
                self.frame_checkboxes,
                text=f"{recurso['nombre']} (Disponibles: {recurso['cantidad']})",
                variable=var,
                onvalue=True,
                offvalue=False,
            )
            checkbox.pack(anchor="w", pady=2)

    # ========== Botón para marcar recursos recomendados ==========
    def marcar_recursos_recomendados(self):
        tipo_evento = self.combo_evento.get()

        if tipo_evento == "Elige un tipo de evento" or not tipo_evento:
            self.lbl_info.configure(
                text="❌ Primero selecciona un tipo de evento", text_color="red"
            )
            return

        # Buscar el evento seleccionado en el diccionario
        if tipo_evento in self.tipos_evento_data:
            recursos_predeterminados = self.tipos_evento_data[tipo_evento]

            # Marcar solo los checkboxes de recursos recomendados
            for recurso_nombre in recursos_predeterminados:
                if recurso_nombre in self.checkbox_vars:
                    self.checkbox_vars[recurso_nombre].set(True)

            # Mostrar mensaje
            self.lbl_info.configure(
                text=f"✅ Recursos recomendados marcados para '{tipo_evento}'",
                text_color="green",
            )

    # ========== Crear evento ==========
    def crear_evento(self):

        # Obtener datos
        tipo_evento = self.combo_evento.get()
        dia = self.entry_dia.get()
        mes = self.entry_mes.get()
        anio = self.entry_anio.get()

        # Validar que todos los campos estén completos
        if tipo_evento == "Elige un tipo de evento" or not tipo_evento:
            self.lbl_info.configure(
                text="❌ Debes seleccionar un tipo de evento", text_color="red"
            )
            return

        if not (dia and mes and anio):
            self.lbl_info.configure(
                text="❌ Debes completar la fecha", text_color="red"
            )
            return

        # Validar formato de fecha 
        try:
            dia = int(dia)
            mes = int(mes)
            anio = int(anio)

            if not (1 <= dia <= 31 and 1 <= mes <= 12 and 2000 <= anio <= 2100):
                raise ValueError
        except ValueError:
            self.lbl_info.configure(
                text="❌ Fecha inválida. Usa números válidos", text_color="red"
            )
            return

        # Obtener recursos SELECCIONADOS por el usuario
        recursos_seleccionados = []

        if hasattr(self, "checkbox_vars"):
            for recurso_nombre, var in self.checkbox_vars.items():
                if var.get():  # Si el checkbox está marcado
                    recursos_seleccionados.append(recurso_nombre)

        # Validar que se haya seleccionado al menos un recurso
        if not recursos_seleccionados:
            self.lbl_info.configure(
                text="❌ Debes seleccionar al menos un recurso", text_color="red"
            )
            return

        # Validar fechas y recursos
        # recursos_innecesarios= []
        # for recurso_seleccionado in recursos_seleccionados:

        # Crear el evento
        nuevo_evento = {
            "tipo": tipo_evento,
            "fecha": f"{dia:02d}/{mes:02d}/{anio}",
            "recursos": recursos_seleccionados,
        }

        # Eliminar recursos seleccionados
        for recurso_eliminar in recursos_seleccionados:
            for recursos_dicc in self.datos:
                if recurso_eliminar == recursos_dicc["nombre"]:
                    recursos_dicc["cantidad"] -= 1
                    break

        # Agregar a la lista
        self.eventos_creados.append(nuevo_evento)
        # Guardar en archivo JSON
        self.guardar_eventos_en_json()
        # Actualizar cantidad de eventos
        self.guardar_recursos()
        # Actualizar los checkboxes con los recursos actualizados
        self.crear_checkboxes_recursos()

        # Actualizar interfaz
        self.actualizar_contador()
        self.lbl_info.configure(
            text=f"✅ Evento '{tipo_evento}' creado para el {dia:02d}/{mes:02d}/{anio}",
            text_color="green",
        )

        # Limpiar campos
        self.entry_dia.delete(0, "end")
        self.entry_mes.delete(0, "end")
        self.entry_anio.delete(0, "end")

        # Desmarcar todos los checkboxes después de crear evento
        for var in self.checkbox_vars.values():
            var.set(False)

        # Mostrar en consola (para depuración)
        print(f"Evento creado: {nuevo_evento}")
        print(f"Total eventos: {len(self.eventos_creados)}")

    # ========== Limpiar selección ==========
    def limpiar_seleccion_recursos(self):
        """Desmarcar todos los checkboxes de recursos"""
        if hasattr(self, "checkbox_vars"):
            for var in self.checkbox_vars.values():
                var.set(False)
            self.lbl_info.configure(
                text="🗑️ Todos los recursos desmarcados", text_color="orange"
            )

    def mostrar_eventos_planificados(self):

        # Crear una nueva ventana emergente
        ventana_eventos = ctk.CTkToplevel(self)
        ventana_eventos.title("📋 Eventos Planificados")
        ventana_eventos.geometry("600x400")

        # Título
        titulo = ctk.CTkLabel(
            ventana_eventos, text="EVENTOS PLANIFICADOS", font=("Arial", 16, "bold")
        )
        titulo.pack(pady=10)

        # Frame para contener los eventos con scroll
        frame_contenedor = ctk.CTkScrollableFrame(
            ventana_eventos, width=550, height=300
        )
        frame_contenedor.pack(pady=10, padx=10)

        # Verificar si hay eventos
        if not self.eventos_creados:
            # Si no hay eventos
            sin_eventos = ctk.CTkLabel(
                frame_contenedor,
                text="📭 No hay eventos planificados todavía.",
                font=("Arial", 12),
                text_color="gray",
            )
            sin_eventos.pack(pady=20)
        else:
            # Mostrar cada evento
            for i, evento in enumerate(self.eventos_creados, 1):
                # Crear un frame para cada evento (como una tarjeta)
                frame_evento = ctk.CTkFrame(frame_contenedor)
                frame_evento.pack(fill="x", pady=5, padx=5)

                # Número del evento
                lbl_numero = ctk.CTkLabel(
                    frame_evento, text=f"Evento #{i}", font=("Arial", 12, "bold")
                )
                lbl_numero.pack(anchor="w", padx=10, pady=(5, 0))

                # Tipo de evento
                lbl_tipo = ctk.CTkLabel(
                    frame_evento, text=f"🚀 Tipo: {evento['tipo']}", font=("Arial", 12)
                )
                lbl_tipo.pack(anchor="w", padx=10)

                # Fecha del evento
                lbl_fecha = ctk.CTkLabel(
                    frame_evento,
                    text=f"📅 Fecha: {evento['fecha']}",
                    font=("Arial", 12),
                )
                lbl_fecha.pack(anchor="w", padx=10)

                # Recursos utilizados
                recursos_texto = ", ".join(evento["recursos"])
                lbl_recursos = ctk.CTkLabel(
                    frame_evento,
                    text=f"Recursos: {recursos_texto}",
                    font=("Arial", 11),
                )
                lbl_recursos.pack(anchor="w", padx=10, pady=(0, 5))

        # Botón para cerrar la ventana
        btn_cerrar = ctk.CTkButton(
            ventana_eventos, text="Cerrar", width=100, command=ventana_eventos.destroy
        )
        btn_cerrar.pack(pady=10)

    def eliminar_eventos_planificados(self):
        # Verificar si hay eventos para eliminar
        if not self.eventos_creados:
            self.lbl_info.configure(
                text="📭 No hay eventos para eliminar", text_color="orange"
            )
            return

        # Crear una nueva ventana emergente
        ventana_eliminar = ctk.CTkToplevel(self)
        ventana_eliminar.title("🗑️ Eliminar Eventos")
        ventana_eliminar.geometry("500x450")

        # Título
        titulo = ctk.CTkLabel(
            ventana_eliminar, text="ELIMINAR EVENTOS", font=("Arial", 16, "bold")
        )
        titulo.pack(pady=10)

        # Instrucciones
        instrucciones = ctk.CTkLabel(
            ventana_eliminar,
            text="Selecciona los eventos que quieres eliminar:",
            font=("Arial", 12),
        )
        instrucciones.pack(pady=5)

        # Frame para contener los checkboxes de eventos
        frame_contenedor = ctk.CTkScrollableFrame(
            ventana_eliminar, width=450, height=250
        )
        frame_contenedor.pack(pady=10, padx=10)

        # Crear variables para los checkboxes
        self.checkbox_vars_eliminar = []

        # Crear un checkbox por cada evento
        for i, evento in enumerate(self.eventos_creados):
            var = ctk.BooleanVar(value=False)
            self.checkbox_vars_eliminar.append(var)

            # Texto del evento
            texto_evento = f"Evento #{i+1}: {evento['tipo']} - {evento['fecha']}"

            # Crear checkbox
            checkbox = ctk.CTkCheckBox(
                frame_contenedor,
                text=texto_evento,
                variable=var,
                onvalue=True,
                offvalue=False,
            )
            checkbox.pack(anchor="w", pady=2, padx=5)

        # Frame para botones
        frame_botones_eliminar = ctk.CTkFrame(ventana_eliminar)
        frame_botones_eliminar.pack(pady=10)

        # Botón para eliminar seleccionados
        btn_eliminar_seleccionados = ctk.CTkButton(
            frame_botones_eliminar,
            text="Eliminar Seleccionados",
            fg_color="#FF5252",
            hover_color="#D32F2F",
            command=lambda: self.confirmar_eliminacion(ventana_eliminar),
        )
        btn_eliminar_seleccionados.pack(side="left", padx=5)

        # Botón para cancelar
        btn_cancelar = ctk.CTkButton(
            frame_botones_eliminar, text="Cancelar", command=ventana_eliminar.destroy
        )
        btn_cancelar.pack(side="left", padx=5)

    def confirmar_eliminacion(self, ventana_eliminar):
        # Obtener los índices de los eventos seleccionados
        indices_a_eliminar = []

        for i, var in enumerate(self.checkbox_vars_eliminar):
            if var.get():  # Si el checkbox está marcado
                indices_a_eliminar.append(i)

        # Verificar si seleccionó algún evento
        if not indices_a_eliminar:
            self.lbl_info.configure(
                text="❌ No seleccionaste ningún evento para eliminar", text_color="red"
            )
            return

        # Confirmar con el usuario
        from tkinter import messagebox

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de que quieres eliminar {len(indices_a_eliminar)} evento(s)?",
        )

        if not confirmar:
            return

        # Eliminar los eventos (empezando por el último para no afectar los índices)
        for index in sorted(indices_a_eliminar, reverse=True):
            # Antes de eliminar, restaurar los recursos utilizados
            evento = self.eventos_creados[index]
            for recurso_nombre in evento["recursos"]:
                for recurso_dicc in self.datos:
                    if recurso_nombre == recurso_dicc["nombre"]:
                        recurso_dicc["cantidad"] += 1  # Restaurar 1 unidad
                        break

            # Eliminar el evento de la lista
            del self.eventos_creados[index]

        # Guardar cambios en los archivos JSON
        self.guardar_eventos_en_json()
        self.guardar_recursos()

        # Actualizar la interfaz
        self.actualizar_contador()
        self.crear_checkboxes_recursos()  # Para mostrar las nuevas cantidades de recursos

        # Cerrar la ventana de eliminación
        ventana_eliminar.destroy()

        # Mostrar mensaje de confirmación
        self.lbl_info.configure(
            text=f"✅ Se eliminaron {len(indices_a_eliminar)} evento(s) correctamente",
            text_color="green",
        )

        print(f"✅ Se eliminaron {len(indices_a_eliminar)} evento(s)")

    # ========== INTERFAZ ==========
    def crear_interfaz(self):
        """Crear todos los elementos visuales"""

        # ========== Titulo ==========
        lbl_titulo = ctk.CTkLabel(
            self, text="GESTOR DE EVENTOS ESPACIALES", font=("Arial", 20, "bold")
        )
        lbl_titulo.pack(pady=20)

        # ========== seleccion de evento ==========
        frame_evento = ctk.CTkFrame(self)
        frame_evento.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            frame_evento, text="Seleccionar Tipo de Evento:", font=("Arial", 14)
        ).pack(pady=5)

        # Crear lista desplegable con eventos cargados del JSON
        self.combo_evento = ctk.CTkComboBox(
            frame_evento,
            values=self.tipos_evento,
            width=300,
        )
        self.combo_evento.pack(pady=5)
        self.combo_evento.set("Elige un tipo de evento")

        # ========== seleccion de recursos ==========
        frame_recursos = ctk.CTkFrame(self)
        frame_recursos.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            frame_recursos,
            text="Seleccionar Recursos (marca los que necesites):",
            font=("Arial", 14),
        ).pack(pady=5)

        # Frame con scroll para los checkboxes
        self.frame_checkboxes = ctk.CTkScrollableFrame(
            frame_recursos, width=550, height=150
        )
        self.frame_checkboxes.pack(pady=5, fill="both", expand=True)

        # ========== botones recursos ==========
        frame_botones_recursos = ctk.CTkFrame(frame_recursos)
        frame_botones_recursos.pack(pady=10)

        # Botón para marcar recursos recomendados
        btn_marcar_recomendados = ctk.CTkButton(
            frame_botones_recursos,
            text="✓ Marcar Recomendados",
            width=180,
            fg_color="#2196F3",
            hover_color="#1976D2",
            command=self.marcar_recursos_recomendados,
        )
        btn_marcar_recomendados.pack(side="left", padx=5)

        # Botón para limpiar selección
        btn_limpiar = ctk.CTkButton(
            frame_botones_recursos,
            text="🗑️ Limpiar Selección",
            width=180,
            fg_color="#FF9800",
            hover_color="#F57C00",
            command=self.limpiar_seleccion_recursos,
        )
        btn_limpiar.pack(side="left", padx=5)

        # ========== 5. FECHA DEL EVENTO ==========
        frame_fecha = ctk.CTkFrame(self)
        frame_fecha.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            frame_fecha, text="Fecha del Evento (DD/MM/AAAA):", font=("Arial", 14)
        ).pack(pady=5)

        # Frame para organizar los campos de fecha
        frame_campos_fecha = ctk.CTkFrame(frame_fecha)
        frame_campos_fecha.pack(pady=5)

        # Día
        self.entry_dia = ctk.CTkEntry(
            frame_campos_fecha, placeholder_text="Día", width=60
        )
        self.entry_dia.pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(frame_campos_fecha, text="/").pack(side="left", padx=2)

        # Mes
        self.entry_mes = ctk.CTkEntry(
            frame_campos_fecha, placeholder_text="Mes", width=60
        )
        self.entry_mes.pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(frame_campos_fecha, text="/").pack(side="left", padx=2)

        # Año
        self.entry_anio = ctk.CTkEntry(
            frame_campos_fecha, placeholder_text="Año", width=80
        )
        self.entry_anio.pack(side="left", padx=5)

        # ========== 6. BOTONES DE ACCIÓN ==========
        frame_botones = ctk.CTkFrame(self)
        frame_botones.pack(pady=20, padx=20)

        # Botón para ver eventos planificados
        self.btn_ver = ctk.CTkButton(
            frame_botones,
            text="📋 Ver Eventos Planificados",
            width=180,
            command=self.mostrar_eventos_planificados,
        )
        self.btn_ver.pack(side="left", padx=10)

        # Botón para eliminar eventos
        self.btn_eliminar = ctk.CTkButton(
            frame_botones,
            text="🗑️ Eliminar Eventos",
            fg_color="#FF5252",
            hover_color="#D32F2F",
            width=180,
            command=self.eliminar_eventos_planificados,
        )
        self.btn_eliminar.pack(side="left", padx=10)

        # ========== 7. BOTÓN PRINCIPAL ==========
        self.btn_crear = ctk.CTkButton(
            self,
            text="🚀 Crear Nuevo Evento",
            width=250,
            height=45,
            font=("Arial", 14, "bold"),
            fg_color="#4CAF50",
            hover_color="#388E3C",
            command=self.crear_evento,
        )
        self.btn_crear.pack(pady=15)

        # ========== 8. ÁREA DE INFORMACIÓN ==========
        self.lbl_info = ctk.CTkLabel(
            self,
            text="Selecciona un tipo de evento para ver recursos recomendados",
            font=("Arial", 12),
            text_color="gray",
        )
        self.lbl_info.pack(pady=10)

        # ========== 9. CONTADOR DE EVENTOS ==========
        frame_contador = ctk.CTkFrame(self)
        frame_contador.pack(pady=10, padx=20, fill="x")

        self.lbl_contador = ctk.CTkLabel(
            frame_contador, text="Eventos planificados: 0", font=("Arial", 12)
        )
        self.lbl_contador.pack(pady=5)
        self.actualizar_contador()

        # ========== 10. CREAR CHECKBOXES INICIALES ==========
        self.crear_checkboxes_recursos()


# Ejecutar la aplicación
if __name__ == "__main__":
    app = GestorEventosSimple()
    app.mainloop()
