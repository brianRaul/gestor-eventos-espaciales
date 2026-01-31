import customtkinter as ctk
import json
from funciones_datos import *
from datetime import datetime, date, timedelta
from funciones_crear_evento import *
from funciones_buscar_hueco import *

class GestorEventos(ctk.CTk):

    def __init__(self):
        super().__init__()

        # 1.Configurar ventana
        self.title("Gestor de Eventos Espaciales")
        self.geometry("650x950")

        self.evento_seleccionado = None

        # 2. CARGA DE EVENTOS
        self.tipos_evento_data = cargar_eventos_desde_json()

        # Extraemos las llaves (nombres de eventos) para el ComboBox
        self.tipos_evento = list(self.tipos_evento_data.keys())

        # Cargamos los recursos
        self.recursos = cargar_recursos_desde_json()
        # 3. CARGA DE ARCHIVOS DE AGENDA
        # Importante: Aseguramos que sea una lista para evitar el error 'NoneType'
        self.eventos_planificados = cargar_eventos_planificados()
        if self.eventos_planificados is None:
            self.eventos_planificados = []

        # 4. CREACIÓN DE LA INTERFAZ
        self.crear_interfaz()

    # =======Guaardar datos===========
    def guardar_eventos_en_json(self):
        try:
            # Ordenar eventos por fecha de inicio (más antigua primero)
            eventos_ordenados = sorted(
                self.eventos_planificados,
                key=lambda x: datetime.strptime(x["fecha_inicio"], "%d/%m/%Y"),
            )

            with open("eventos_planificados.json", "w", encoding="utf-8") as f:
                json.dump(eventos_ordenados, f, ensure_ascii=False, indent=4)

            print(f"✅ Eventos guardados y ordenados: {len(eventos_ordenados)} eventos")

            # Actualizar la lista en memoria
            self.eventos_planificados = eventos_ordenados
            return True

        except Exception as e:
            print(f"❌ Error al guardar en JSON: {e}")
            return False

    def guardar_recursos(self):
        try:
            estructura_original = {"recursos": {}}

            for recurso in self.recursos:
                categoria = recurso["categoria"]
                if categoria not in estructura_original["recursos"]:
                    estructura_original["recursos"][categoria] = []

                recurso_data = {
                    "modelo": recurso["modelo"],
                    "tipo": recurso["tipo"],
                    "cantidad_total": recurso["cantidad_total"],
                }

                # Solo guardar cantidad_disponible para combustible
                if recurso["es_combustible"]:
                    recurso_data["cantidad_disponible"] = recurso["cantidad_disponible"]

                estructura_original["recursos"][categoria].append(recurso_data)

            with open("recursos.json", "w", encoding="utf-8") as f:
                json.dump(estructura_original, f, ensure_ascii=False, indent=2)

            print(f"✅ Recursos guardados: {len(self.recursos)} recursos")
            return True
        except Exception as e:
            print(f"Error al guardar recursos: {e}")
            return False

    ################## LOGICA ##################
    def actualizar_contador(self):
        total = len(self.eventos_planificados)
        self.lbl_contador.configure(text=f"Eventos planificados: {total}")

    # .1 ========== Crear checkboxes de recursos ==========
    def crear_checkboxes_recursos(self):
        for widget in self.frame_checkboxes.winfo_children():
            widget.destroy()

        self.checkbox_vars = {}

        if not self.recursos:
            mensaje = ctk.CTkLabel(
                self.frame_checkboxes,
                text="No hay recursos disponibles",
                text_color="orange",
            )
            mensaje.pack(pady=20)
            return

        # Agrupar por categoría
        recursos_por_categoria = {}
        for recurso in self.recursos:
            categoria = recurso["categoria"]
            if categoria not in recursos_por_categoria:
                recursos_por_categoria[categoria] = []
            recursos_por_categoria[categoria].append(recurso)

        # Mostrar por categoría
        for categoria, recursos in recursos_por_categoria.items():
            # Título de la categoría
            lbl_categoria = ctk.CTkLabel(
                self.frame_checkboxes,
                text=f"▸ {categoria}:",
                font=("Arial", 12, "bold"),
                text_color="#D8DFDE",
            )
            lbl_categoria.pack(anchor="w", pady=(10, 5), padx=10)

            # Recursos de esta categoría
            for recurso in recursos:
                var = ctk.BooleanVar(value=False)
                self.checkbox_vars[recurso["nombre_mostrar"]] = var

                # Mostrar información según tipo de recurso
                if recurso["es_combustible"]:
                    # Para combustible: mostrar disponible/total
                    texto = f"{recurso['nombre_mostrar']} - {recurso['cantidad_disponible']}/{recurso['cantidad_total']}L"
                    # Color según disponibilidad
                    if recurso["cantidad_disponible"] <= 0:
                        color = "#FF5252"  # Rojo si no hay
                    elif (
                        recurso["cantidad_disponible"] < recurso["cantidad_total"] * 0.2
                    ):
                        color = "#FF9800"  # Naranja si queda poco (<20%)
                    else:
                        color = "#4CAF50"  # Verde si hay suficiente
                else:
                    # Para equipos: solo mostrar cantidad total
                    texto = f"{recurso['nombre_mostrar']} - {recurso['cantidad_total']} unidades"
                    color = "#2196F3"

                # Crear checkbox
                checkbox = ctk.CTkCheckBox(
                    self.frame_checkboxes,
                    text=texto,
                    variable=var,
                    onvalue=True,
                    offvalue=False,
                    text_color=color,
                )
                checkbox.pack(anchor="w", padx=20, pady=2)
    # .2 ========== Botón para marcar recursos recomendados ==========
    def marcar_recursos_recomendados(self, event=None):
     tipo_evento = self.combo_evento.get()
    
     if tipo_evento not in self.tipos_evento_data:
        self.lbl_info.configure(
            text="❌ Selecciona un tipo de evento primero", 
            text_color="red"
        )
        return
    
    # Desmarcar todos los recursos SIN mostrar mensaje
     for var in self.checkbox_vars.values():
        var.set(False)
    
    # Obtener los recursos requeridos para este evento
     evento_data = self.tipos_evento_data[tipo_evento]
     recursos_requeridos = evento_data.get("recursos_requeridos", [])
    
     if not recursos_requeridos:
        self.lbl_info.configure(
            text="⚠️ No hay recursos requeridos definidos para este evento",
            text_color="orange",
        )
        return
    
    # Contador de recursos marcados
     recursos_marcados = 0
     recursos_no_disponibles = 0
    
    # Para cada recurso requerido
     for req in recursos_requeridos:
        categoria_req = req["categoria"].upper()
        tipo_req = req["tipo"].upper()
        cantidad_req = req.get("cantidad", 1)
        
        # Buscar recursos que coincidan con la categoría y tipo
        recursos_encontrados = 0
        
        for recurso_nombre, checkbox_var in self.checkbox_vars.items():
            # Buscar el recurso en la lista completa
            recurso_info = None
            for r in self.recursos:
                if r["nombre_mostrar"] == recurso_nombre:
                    recurso_info = r
                    break
            
            if not recurso_info:
                continue
            
            # Verificar si coincide con el requerimiento
            if (recurso_info["categoria"].upper() == categoria_req and 
                recurso_info["tipo"].upper() == tipo_req):
                
                # Para combustible, verificar disponibilidad
                if recurso_info["es_combustible"]:
                    if recurso_info["cantidad_disponible"] >= cantidad_req:
                        checkbox_var.set(True)
                        recursos_encontrados += 1
                        recursos_marcados += 1
                else:
                    # Para equipos, siempre marcar (no verificar disponibilidad aquí)
                    checkbox_var.set(True)
                    recursos_encontrados += 1
                    recursos_marcados += 1
                
                # Si ya encontramos la cantidad necesaria, pasar al siguiente
                if recursos_encontrados >= cantidad_req:
                    break
    
    # Mostrar mensaje con la cantidad de recursos marcados
     if recursos_marcados > 0:
        mensaje = f"✅ Recursos marcados: {recursos_marcados} "
        if recursos_no_disponibles > 0:
            mensaje += f"({recursos_no_disponibles} no disponibles)"
        self.lbl_info.configure(text=mensaje, text_color="green")
     else:
        self.lbl_info.configure(
            text="⚠️ No se pudo marcar ningún recurso recomendado",
            text_color="orange"
        )
    # .3 ========== Crear evento ==========
    def crear_evento(self):
        # 1. Obtener datos de la interfaz
        tipo_evento = self.combo_evento.get()
        day = self.entry_day.get()
        month = self.entry_month.get()
        year = self.entry_year.get()
        duracion_str = self.entry_duracion.get()
        
        # 2. Obtener recursos seleccionados de los checkboxes
        recursos_seleccionados_nombres = [
            k for k, v in self.checkbox_vars.items() if v.get()
        ]
        
        # 3. Llamar a la función de lógica externa
        resultado, mensaje, nuevo_evento = procesar_creacion_evento(
            tipo_evento=tipo_evento,
            day=day,
            month=month,
            year=year,
            duracion_str=duracion_str,
            recursos_seleccionados_nombres=recursos_seleccionados_nombres,
            recursos=self.recursos,
            eventos_planificados=self.eventos_planificados,
            tipos_evento_data=self.tipos_evento_data
        )
        
        # 4. Manejar el resultado (INTERFAZ GRÁFICA)
        if resultado and nuevo_evento:
            # Éxito: agregar evento
            self.eventos_planificados.append(nuevo_evento)
            
            # Guardar datos
            self.guardar_eventos_en_json()
            self.guardar_recursos()
            
            # Actualizar interfaz
            self.actualizar_contador()
            self.crear_checkboxes_recursos()
            
            # Limpiar campos de entrada
            self.entry_day.delete(0, "end")
            self.entry_month.delete(0, "end")
            self.entry_year.delete(0, "end")
            self.entry_duracion.delete(0, "end")
            self.combo_evento.set("Elige un tipo de evento")
            self.limpiar_seleccion_recursos()
            
            # Mostrar mensaje de éxito
            fecha_str = datetime.strptime(nuevo_evento["fecha_inicio"], "%d/%m/%Y").strftime("%d/%m")
            self.lbl_info.configure(
                text=f"🚀 Evento '{tipo_evento}' creado exitosamente ({fecha_str})",
                text_color="green"
            )
        else:
            # Error: mostrar mensaje
            self.lbl_info.configure(text=mensaje, text_color="red")
    # .4 ========== Limpiar selección ==========
    def limpiar_seleccion_recursos(self):
        """Desmarcar todos los checkboxes de recursos"""
        if hasattr(self, "checkbox_vars"):
            for var in self.checkbox_vars.values():
                var.set(False)
            self.lbl_info.configure(
                text="Todos los recursos desmarcados", text_color="orange"
            )
    # .5 =========== Mostrar eventos planificados ========
    def mostrar_eventos_planificados(self):

        # Crear una nueva ventana emergente
        ventana_eventos = ctk.CTkToplevel(self)
        ventana_eventos.title("📋 Eventos Planificados")
        ventana_eventos.geometry("400x400")

        # Título
        titulo = ctk.CTkLabel(
            ventana_eventos, text="EVENTOS PLANIFICADOS", font=("Arial", 16, "bold")
        )
        titulo.pack(pady=10)

        # Frame para contener los eventos con scroll
        frame_contenedor = ctk.CTkScrollableFrame(
            ventana_eventos, width=300, height=300
        )
        frame_contenedor.pack(pady=10, padx=10)

        # Verificar si hay eventos
        if not self.eventos_planificados:
            # si no hay eventos
            sin_eventos = ctk.CTkLabel(
                frame_contenedor,
                text=" No hay eventos planificados todavía.",
                font=("Arial", 12),
                text_color="gray",
            )
            sin_eventos.pack(pady=20)
        else:
            # Mostrar cada evento
            for i, evento in enumerate(self.eventos_planificados, 1):
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
                    frame_evento, text=f"Tipo: {evento['tipo']}", font=("Arial", 12)
                )
                lbl_tipo.pack(anchor="w", padx=10)

                # Fecha de inicio y fin
                lbl_fecha = ctk.CTkLabel(
                    frame_evento,
                    text=f"📅 Inicio: {evento.get('fecha_inicio', evento.get('fecha', 'N/A'))} | Fin: {evento.get('fecha_fin', 'N/A')}",
                    font=("Arial", 12),
                )
                lbl_fecha.pack(anchor="w", padx=10)

                # Duración
                lbl_duracion = ctk.CTkLabel(
                    frame_evento,
                    text=f"⏱️ Duración: {evento.get('duracion_dias', 1)} días",
                    font=("Arial", 11),
                )
                lbl_duracion.pack(anchor="w", padx=10)

        # Botón para cerrar la ventana
        btn_cerrar = ctk.CTkButton(
            ventana_eventos, text="Cerrar", width=100, command=ventana_eventos.destroy
        )
        btn_cerrar.pack(pady=10)
    # .6 ============ Seccioón Sugerir Fecha =============
    def sugerir_fecha_disponible(self):
        """Busca la próxima fecha disponible basada en solapamientos reales"""
        tipo_evento = self.combo_evento.get()
        if tipo_evento not in self.tipos_evento_data:
            self.lbl_info.configure(
                text="❌ Selecciona un evento primero", text_color="red"
            )
            return

        try:
            duracion = int(self.entry_duracion.get())
        except:
            duracion = 1

        # Obtener recursos requeridos para este evento
        evento_data = self.tipos_evento_data[tipo_evento]
        recursos_requeridos = evento_data.get("recursos_requeridos", [])

        # Usar función preparada para convertir recursos requeridos
        recursos_necesarios = preparar_recursos_requeridos(recursos_requeridos)

        # Empezar la búsqueda desde la fecha que el usuario puso, o desde mañana
        try:
            day = int(self.entry_day.get())
            month = int(self.entry_month.get())
            year = int(self.entry_year.get())
            fecha_busqueda = date(year, month, day)

            # Si la fecha es en el pasado, empezar desde mañana
            if fecha_busqueda < date.today():
                fecha_busqueda = date.today() + timedelta(days=1)
        except:
            # Si no hay fecha válida, empezar desde mañana
            fecha_busqueda = date.today() + timedelta(days=1)

        # Buscar por 365 días
        for _ in range(365):
            fecha_fin = fecha_busqueda + timedelta(days=duracion - 1)

            # Usar la función de disponibilidad externa
            disponible = verificar_disponibilidad_fecha(
                fecha_busqueda, fecha_fin, recursos_necesarios,
                self.eventos_planificados, self.recursos
            )

            if disponible:
                self.actualizar_campos_fecha(fecha_busqueda)
                self.lbl_info.configure(
                    text=f"✅ Fecha disponible: {fecha_busqueda.strftime('%d/%m/%Y')}",
                    text_color="green",
                )
                return

            # Pasar al siguiente día
            fecha_busqueda += timedelta(days=1)

        self.lbl_info.configure(
            text="❌ No se encontró fecha disponible en el próximo año",
            text_color="red",
        )
        
    def actualizar_campos_fecha(self, fecha):
        """Rellena los campos de fecha con la fecha sugerida"""
        self.entry_day.delete(0, "end")
        self.entry_day.insert(0, str(fecha.day))

        self.entry_month.delete(0, "end")
        self.entry_month.insert(0, str(fecha.month))

        self.entry_year.delete(0, "end")
        self.entry_year.insert(0, str(fecha.year))

    def ver_combustible(self):
        # Crear ventana nueva
        ventana = ctk.CTkToplevel(self)
        ventana.title("📊 Estado de Combustible")
        ventana.geometry("400x350")

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

        # Buscar combustibles
        combustibles = []
        for recurso in self.recursos:
            if (
                recurso.get("es_combustible", False)
                or "COMBUSTIBLE" in recurso.get("categoria", "").upper()
            ):
                combustibles.append(recurso)

        if not combustibles:
            ctk.CTkLabel(
                frame_scroll, text="No hay sistemas de combustible", text_color="gray"
            ).pack(pady=20)
        else:
            for recurso in combustibles:
                disponible = recurso["cantidad_disponible"]
                total = recurso["cantidad_total"]
                porcentaje = (disponible / total * 100) if total > 0 else 0

                # Color según porcentaje
                if porcentaje >= 80:
                    color = "#4CAF50"
                elif porcentaje >= 30:
                    color = "#FF9800"
                else:
                    color = "#F44336"

                # Frame para cada combustible
                frame_tanque = ctk.CTkFrame(frame_scroll)
                frame_tanque.pack(fill="x", pady=5, padx=5)

                # Mostrar información
                texto = f"• {recurso['nombre_mostrar']}: {disponible:,}/{total:,}L ({porcentaje:.1f}%)"
                ctk.CTkLabel(
                    frame_tanque, text=texto, font=("Arial", 11), text_color=color
                ).pack(anchor="w", padx=10, pady=5)

        # Botón para cerrar
        ctk.CTkButton(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)

    def rellenar_combustible(self):
        litros_agregados = 0

        for recurso in self.recursos:
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

        if litros_agregados > 0:
            # Guardar cambios
            self.guardar_recursos()

            # Mensaje de éxito
            mensaje = f"✅ Combustible rellenado\n⛽ +{litros_agregados:,} litros"
            self.lbl_info.configure(text=mensaje, text_color="green")
        else:
            self.lbl_info.configure(
                text="ℹ️ Todo el combustible ya está lleno", text_color="orange"
            )

    def eliminar_eventos_planificados(self):
        if len(self.eventos_planificados) == 0:
            self.lbl_info.configure(
                text="❌ No hay eventos para eliminar", text_color="red"
            )
            return

        ventana_eliminar = ctk.CTkToplevel(self)
        ventana_eliminar.title("🗑️ Eliminar Eventos")
        ventana_eliminar.geometry("600x500")

        # Título
        ctk.CTkLabel(
            ventana_eliminar,
            text="SELECCIONA EVENTOS A ELIMINAR",
            font=("Arial", 18, "bold"),
        ).pack(pady=10)

        # Instrucciones
        ctk.CTkLabel(
            ventana_eliminar,
            text="Marca los eventos que quieres eliminar:",
            font=("Arial", 14),
        ).pack(pady=5)

        # Área con scroll
        frame_scroll = ctk.CTkScrollableFrame(ventana_eliminar, width=550, height=300)
        frame_scroll.pack(pady=10, padx=10)

        # ========== CHECKBOX "SELECCIONAR TODOS" ==========
        frame_seleccion_todos = ctk.CTkFrame(frame_scroll)
        frame_seleccion_todos.pack(fill="x", pady=(0, 10), padx=5)
        
        self.var_seleccionar_todos = ctk.BooleanVar(value=False)
        
        checkbox_seleccionar_todos = ctk.CTkCheckBox(
            frame_seleccion_todos,
            text="📋 SELECCIONAR TODOS LOS EVENTOS",
            variable=self.var_seleccionar_todos,
            onvalue=True,
            offvalue=False,
            font=("Arial", 12, "bold"),
            command=lambda: self.toggle_seleccionar_todos(self.checkboxes_eliminar, self.var_seleccionar_todos)
        )
        checkbox_seleccionar_todos.pack(anchor="w", padx=5)

        # Lista para checkboxes de eventos
        self.checkboxes_eliminar = []

        # Crear checkboxes para cada evento
        for i, evento in enumerate(self.eventos_planificados):
            var_checkbox = ctk.BooleanVar(value=False)
            self.checkboxes_eliminar.append(var_checkbox)

            # Formatear texto del evento
            fecha_inicio = evento.get('fecha_inicio', 'N/A')
            duracion = evento.get('duracion_dias', 1)
            texto_evento = f"Evento #{i+1}: {evento['tipo']} - {fecha_inicio} ({duracion} días)"

            checkbox = ctk.CTkCheckBox(
                frame_scroll,
                text=texto_evento,
                variable=var_checkbox,
                onvalue=True,
                offvalue=False,
                font=("Arial", 11)
            )
            checkbox.pack(anchor="w", pady=2, padx=20)

        # Botones
        frame_botones = ctk.CTkFrame(ventana_eliminar)
        frame_botones.pack(pady=15)

        btn_eliminar = ctk.CTkButton(
            frame_botones,
            text="ELIMINAR SELECCIONADOS",
            fg_color="#FF5252",
            hover_color="#D32F2F",
            width=200,
            height=40,
            font=("Arial", 14, "bold"),
            command=lambda: self.confirmar_eliminacion(ventana_eliminar),
        )
        btn_eliminar.pack(side="left", padx=10)

        btn_cancelar = ctk.CTkButton(
            frame_botones,
            text="CANCELAR",
            width=100,
            height=40,
            command=ventana_eliminar.destroy,
        )
        btn_cancelar.pack(side="left", padx=10)

    def toggle_seleccionar_todos(self, checkboxes_list, var_todos):
        estado = var_todos.get()
        for checkbox_var in checkboxes_list:
            checkbox_var.set(estado)

    def confirmar_eliminacion(self, ventana_eliminar):
        import tkinter.messagebox as messagebox

        # 1. Obtener índices de eventos seleccionados para eliminar
        eventos_a_eliminar_indices = []
        for i, checkbox_var in enumerate(self.checkboxes_eliminar):
            if checkbox_var.get():
                eventos_a_eliminar_indices.append(i)

        # 2. Verificar si hay algo seleccionado
        if len(eventos_a_eliminar_indices) == 0:
            messagebox.showwarning(
                "Sin selección", "No has seleccionado ningún evento para eliminar."
            )
            return

        # 3. Pedir confirmación
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar {len(eventos_a_eliminar_indices)} evento(s)?\n\n"
            f"Esta acción devolverá los recursos no consumibles al inventario.",
        )

        if not respuesta:
            return

        # 4. Pedir confirmación
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar {len(eventos_a_eliminar_indices)} evento(s)?\n\n"
            f"Esta acción devolverá los recursos no consumibles al inventario.",
        )

        if not respuesta:
            return

        # 5. Procesar cada evento a eliminar (orden inverso)
        recursos_devueltos = []
        eventos_a_eliminar_indices.sort(reverse=True)

        for indice in eventos_a_eliminar_indices:
            if indice >= len(self.eventos_planificados):
                continue

            evento = self.eventos_planificados[indice]

            # Devolver recursos (SOLO equipos, NO combustible)
            for recurso_detalle in evento.get("recursos_detalle", []):
                # Solo procesar recursos NO combustibles
                if not recurso_detalle.get("es_combustible", False):
                    # Buscar el recurso en la lista de recursos
                    for recurso in self.recursos:
                        if recurso["nombre_mostrar"] == recurso_detalle["nombre_mostrar"]:
                            # Incrementar la cantidad disponible (para equipos, esto es lo mismo que total)
                            # O simplemente marcarlo como disponible nuevamente
                            print(f"🔄 Equipo liberado: {recurso['nombre_mostrar']}")
                            recursos_devueltos.append({
                                "nombre": recurso["nombre_mostrar"],
                                "categoria": recurso["categoria"],
                                "tipo": "equipo",
                            })
                            break

            # COMBUSTIBLE: No se hace nada - no se devuelve
            for recurso_detalle in evento.get("recursos_detalle", []):
                if recurso_detalle.get("es_combustible", False):
                    print(f"🔥 Combustible NO devuelto (consumido): {recurso_detalle['nombre_mostrar']}")

            # Eliminar el evento
            del self.eventos_planificados[indice]

        # 6. Guardar cambios
        self.guardar_recursos()
        self.guardar_eventos_en_json()

        # 7. Actualizar interfaz
        self.actualizar_contador()
        self.crear_checkboxes_recursos()

        # 8. Cerrar ventana
        ventana_eliminar.destroy()

        # 9. Mostrar mensaje de éxito
        mensaje = f"✅ Se eliminaron {len(eventos_a_eliminar_indices)} evento(s)."

        if recursos_devueltos:
            mensaje += f"\n🔄 {len(recursos_devueltos)} equipo(s) liberado(s) para nuevas asignaciones."

        self.lbl_info.configure(text=mensaje, text_color="green")

    # ************** INTERFAZ *************#
    def crear_interfaz(self):
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
            text="Seleccionar Recursos:",
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

        # Day
        self.entry_day = ctk.CTkEntry(
            frame_campos_fecha, placeholder_text="Día", width=60
        )
        self.entry_day.pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(frame_campos_fecha, text="/").pack(side="left", padx=2)

        # month
        self.entry_month = ctk.CTkEntry(
            frame_campos_fecha, placeholder_text="month", width=60
        )
        self.entry_month.pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(frame_campos_fecha, text="/").pack(side="left", padx=2)

        # Año
        self.entry_year = ctk.CTkEntry(
            frame_campos_fecha, placeholder_text="Año", width=80
        )
        self.entry_year.pack(side="left", padx=5)

        self.entry_duracion = ctk.CTkEntry(
            frame_campos_fecha, placeholder_text="Días de duración", width=120
        )
        self.entry_duracion.pack(pady=5)

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

        # ========== BOTONES DE COMBUSTIBLE ==========
        frame_combustible = ctk.CTkFrame(self)
        frame_combustible.pack(pady=5, padx=20)

        # Botón 1: Ver combustible
        btn_ver = ctk.CTkButton(
            frame_combustible,
            text="📊 Ver Combustible",
            width=180,
            fg_color="#2196F3",
            hover_color="#1976D2",
            command=self.ver_combustible,
        )
        btn_ver.pack(side="left", padx=10)

        # Botón 2: Rellenar todo
        btn_rellenar = ctk.CTkButton(
            frame_combustible,
            text="⛽ Rellenar Todo",
            width=180,
            fg_color="#FF9800",
            hover_color="#F57C00",
            command=self.rellenar_combustible,
        )
        btn_rellenar.pack(side="left", padx=10)

        # ========== BOTÓN DE SUGERENCIA ==========
        self.btn_sugerir = ctk.CTkButton(
            self,
            text="🔍 Sugerir Próxima Fecha Libre",
            width=250,
            height=35,
            fg_color="#1f538d",
            hover_color="#14375e",
            command=self.sugerir_fecha_disponible,
        )
        self.btn_sugerir.pack(pady=10)

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

        # ========== 11. CREAR CHECKBOXES INICIALES ==========
        self.crear_checkboxes_recursos()


# Ejecutar la aplicación
if __name__ == "__main__":
    app = GestorEventos()
    app.mainloop()
