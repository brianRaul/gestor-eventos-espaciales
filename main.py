import customtkinter as ctk
import json
from datetime import datetime, date, timedelta
import tkinter.messagebox as messagebox
from modulos.funciones_datos import *
from modulos.funciones_crear_evento import *
from modulos.funciones_buscar_hueco import *
import modulos.funciones_series_recurrentes as fsr
import modulos.logica_combustible as lc
import modulos.logica_eliminacion as le
import modulos.logica_serie as ls
import modulos.logica_visualizaciones as lv
import modulos.logica_recursos as lr
import modulos.logica_fechas as lf


class GestorEventos(ctk.CTk):

    def __init__(self):
        super().__init__()

        # 1.Configurar ventana
        self.title("Gestor de Eventos Espaciales")
        self.geometry("670x975")

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

        # Referencia para la ventana de combustible
        self.ventana_combustible = None

        # Inicializar lista de checkboxes para eliminar eventos
        self.checkboxes_eliminar = []

        # 4. CREACIÓN DE LA INTERFAZ
        self.crear_interfaz()

    ################ GUARDAR DATOS ###################

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

    #################### LOGICA #######################

    # .0 ======== Actualizar contador ================
    def actualizar_contador(self):
        total = len(self.eventos_planificados)
        self.lbl_contador.configure(text=f"Eventos planificados: {total}")

        # Asegurar que la interfaz se actualice inmediatamente
        self.update_idletasks()

    # .1 ========== Crear checkboxes de recursos ======
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

        # Usar función del módulo para agrupar por categoría
        recursos_por_categoria = lr.obtener_recursos_por_categoria(self.recursos)

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

                # Usar funciones del módulo para obtener texto y color
                texto, _ = lr.obtener_texto_recurso(recurso)
                color = lr.obtener_color_recurso(recurso)

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
                text="❌ Selecciona un tipo de evento primero", text_color="red"
            )
            return

        # Desmarcar todos los recursos
        for var in self.checkbox_vars.values():
            var.set(False)

        # Usar función del módulo para obtener recursos recomendados
        recursos_recomendados = lr.obtener_recursos_recomendados(
            tipo_evento, self.tipos_evento_data, self.recursos
        )

        # Marcar los recursos recomendados
        for nombre_recurso in recursos_recomendados:
            if nombre_recurso in self.checkbox_vars:
                self.checkbox_vars[nombre_recurso].set(True)

        # Contar cuántos recursos se marcaron
        recursos_marcados = sum(1 for var in self.checkbox_vars.values() if var.get())
        if recursos_marcados > 0:
            self.lbl_info.configure(
                text=f"✅ Recursos recomendados marcados: {recursos_marcados}",
                text_color="green",
            )
        else:
            self.lbl_info.configure(
                text="⚠️ No se pudo marcar ningún recurso recomendado",
                text_color="orange",
            )

    # .4 ========== Limpiar selección =================
    def limpiar_seleccion_recursos(self):
        # Desmarcar todos los checkboxes de recursos
        if hasattr(self, "checkbox_vars"):
            for var in self.checkbox_vars.values():
                var.set(False)
            self.lbl_info.configure(
                text="Todos los recursos desmarcados", text_color="orange"
            )

    # .3 ========== Crear evento ======================
    def crear_evento(self):
        # 1. Obtener datos de la interfaz
        tipo_evento = self.combo_evento.get()
        day = self.entry_day.get()
        month = self.entry_month.get()
        year = self.entry_year.get()
        duracion_str = self.entry_duracion.get()

        # Validación rápida de límite de años
        try:
            fecha_ingresada = datetime(int(year), int(month), int(day))
            fecha_limite = datetime.now() + timedelta(days=1095)  # 3 años

            if fecha_ingresada > fecha_limite:
                self.lbl_info.configure(
                    text="❌ La fecha excede el límite de 3 años",
                    text_color="red",
                )
                return
        except:
            pass  # La validación detallada se hará después

        # 2. Obtener recursos seleccionados de los checkboxes
        recursos_seleccionados_nombres = [
            k for k, v in self.checkbox_vars.items() if v.get()
        ]

        # 3. Llamar a la función de lógica externa (CORREGIDO: 4 valores)
        resultado, mensaje, nuevo_evento, _ = procesar_creacion_evento(
            tipo_evento=tipo_evento,
            day=day,
            month=month,
            year=year,
            duracion_str=duracion_str,
            recursos_seleccionados_nombres=recursos_seleccionados_nombres,
            recursos=self.recursos,
            eventos_planificados=self.eventos_planificados,
            tipos_evento_data=self.tipos_evento_data,
        )

        # 4. Manejar el resultado (INTERFAZ GRÁFICA)
        if resultado and nuevo_evento:
            # Éxito: agregar evento (ya viene con estructura completa)
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
            self.lbl_info.configure(text=mensaje, text_color="green")
        else:
            # Error: mostrar mensaje TAL CUAL viene (ya es corto)
            self.lbl_info.configure(text=mensaje, text_color="red")

    # .5 ========== Mostrar eventos planificados ======
    def mostrar_eventos_planificados(self):
        lv.mostrar_eventos_planificados(
            self, self.eventos_planificados, lv.mostrar_recursos_evento
        )

    # .6 ========== Sugerir Fecha =====================
    def sugerir_fecha_disponible(self):
        tipo_evento = self.combo_evento.get()
        day = self.entry_day.get()
        month = self.entry_month.get()
        year = self.entry_year.get()
        duracion_str = self.entry_duracion.get()

        # Usar la función del módulo para la lógica
        fecha_encontrada, mensaje, es_error_combustible = (
            lf.sugerir_fecha_disponible_logica(
                tipo_evento=tipo_evento,
                tipos_evento_data=self.tipos_evento_data,
                day=day,
                month=month,
                year=year,
                duracion_str=duracion_str,
                eventos_planificados=self.eventos_planificados,
                recursos=self.recursos,
                preparar_recursos_requeridos_func=preparar_recursos_requeridos,  # de funciones_buscar_hueco
                verificar_disponibilidad_fecha_func=verificar_disponibilidad_fecha,  # de funciones_buscar_hueco
            )
        )

        # Manejar el resultado en la interfaz
        if fecha_encontrada:
            self.actualizar_campos_fecha(fecha_encontrada)
            self.lbl_info.configure(text=mensaje, text_color="green")
        else:
            if es_error_combustible:
                mensaje = (
                    f"❌ {mensaje}\n\n💡 Usa 'Rellenar Todo' para reponer combustible."
                )
            self.lbl_info.configure(text=mensaje, text_color="red")

    # .7 ========== Actualizar campos fecha ===========
    def actualizar_campos_fecha(self, fecha):
        """Rellena los campos de fecha con la fecha sugerida"""
        self.entry_day.delete(0, "end")
        self.entry_day.insert(0, str(fecha.day))

        self.entry_month.delete(0, "end")
        self.entry_month.insert(0, str(fecha.month))

        self.entry_year.delete(0, "end")
        self.entry_year.insert(0, str(fecha.year))

    # .8 ========== Ver Combustible Disponible ========
    def ver_combustible(self):
        # Si ya existe una ventana de combustible, enfocarla en lugar de crear otra
        if (
            self.ventana_combustible is not None
            and self.ventana_combustible.winfo_exists()
        ):
            self.ventana_combustible.lift()
            return

        # Crear ventana nueva
        self.ventana_combustible = ctk.CTkToplevel(self)
        self.ventana_combustible.title("📊 Estado de Combustible")
        self.ventana_combustible.geometry("400x350")

        # Configurar para que al cerrar se limpie la referencia
        def on_close():
            if self.ventana_combustible is not None:
                self.ventana_combustible.destroy()
                self.ventana_combustible = None

        self.ventana_combustible.protocol("WM_DELETE_WINDOW", on_close)

        # Título
        ctk.CTkLabel(
            self.ventana_combustible,
            text="📊 ESTADO DE COMBUSTIBLE",
            font=("Arial", 16, "bold"),
            text_color="#FF9800",
        ).pack(pady=10)

        # Frame con scroll
        frame_scroll = ctk.CTkScrollableFrame(
            self.ventana_combustible, width=350, height=250
        )
        frame_scroll.pack(pady=10, padx=10)

        # Usar la función del módulo para obtener combustibles
        combustibles = lc.obtener_combustibles(self.recursos)

        if not combustibles:
            ctk.CTkLabel(
                frame_scroll, text="No hay sistemas de combustible", text_color="gray"
            ).pack(pady=20)
        else:
            for recurso in combustibles:
                # Usar funciones del módulo para cálculos
                porcentaje = lc.calcular_porcentaje_combustible(recurso)
                color = lc.obtener_color_porcentaje(porcentaje)

                # Frame para cada combustible
                frame_tanque = ctk.CTkFrame(frame_scroll)
                frame_tanque.pack(fill="x", pady=5, padx=5)

                # Mostrar información
                texto = f"• {recurso['nombre_mostrar']}: {recurso['cantidad_disponible']:,}/{recurso['cantidad_total']:,}L ({porcentaje:.1f}%)"
                ctk.CTkLabel(
                    frame_tanque, text=texto, font=("Arial", 11), text_color=color
                ).pack(anchor="w", padx=10, pady=5)

            tipo_evento_actual = self.combo_evento.get()

            if tipo_evento_actual and tipo_evento_actual != "Elige un tipo de evento":
                # Usar función del módulo para obtener advertencias
                advertencias = lc.obtener_advertencias_combustible_evento(
                    tipo_evento_actual, combustibles, self.tipos_evento_data
                )

                for advertencia in advertencias:
                    # Crear frame para advertencia
                    frame_advertencia = ctk.CTkFrame(self.ventana_combustible)
                    frame_advertencia.pack(pady=5, padx=20, fill="x")

                    # Mostrar advertencia
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
        ctk.CTkButton(self.ventana_combustible, text="Cerrar", command=on_close).pack(
            pady=10
        )

    # .9 ========== Rellenar sistema de combustible ===
    def rellenar_combustible(self):
        # Usar función del módulo para la lógica de rellenado
        litros_agregados, recursos_modificados = lc.rellenar_combustible_logica(
            self.recursos
        )

        if litros_agregados > 0:
            # Guardar cambios
            self.guardar_recursos()

            # ACTUALIZACIÓN: Si la ventana está abierta, cierra y vuelve a abrir
            if (
                self.ventana_combustible is not None
                and self.ventana_combustible.winfo_exists()
            ):
                self.ventana_combustible.destroy()
                self.ventana_combustible = None
                self.ver_combustible()  # Abre nueva ventana con datos actualizados

            # Mensaje de éxito
            mensaje = f"✅ Combustible rellenado\n⛽ +{litros_agregados:,} litros"
            self.lbl_info.configure(text=mensaje, text_color="green")
        else:
            self.lbl_info.configure(
                text="ℹ️ Todo el combustible ya está lleno", text_color="orange"
            )

    # .9.1========= Verifica si hay combustible suficiente para toda la serie =======
    def verificar_combustible_para_serie(self, tipo_evento, repeticiones, recursos):
        # Usar función del módulo
        return lc.verificar_combustible_para_serie_logica(
            tipo_evento, repeticiones, recursos, self.tipos_evento_data
        )

    # .10 ========= Eliminar Eventos ==================
    def eliminar_eventos_planificados(self):

        self.eventos_planificados = cargar_eventos_planificados()

        if len(self.eventos_planificados) == 0:
            self.lbl_info.configure(
                text="❌ No hay eventos para eliminar", text_color="red"
            )
            return

        ventana_eliminar = ctk.CTkToplevel(self)
        ventana_eliminar.title("🗑️ Eliminar Eventos")
        ventana_eliminar.geometry("600x500")

        # Hacer que la ventana sea modal
        ventana_eliminar.grab_set()
        ventana_eliminar.transient(self)

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
            command=lambda: self.toggle_seleccionar_todos_eventos(
                self.var_seleccionar_todos
            ),
        )
        checkbox_seleccionar_todos.pack(anchor="w", padx=5)

        # Lista para checkboxes de eventos
        self.checkboxes_eliminar = []

        # Crear checkboxes para cada evento
        for i, evento in enumerate(self.eventos_planificados):
            var_checkbox = ctk.BooleanVar(value=False)
            self.checkboxes_eliminar.append(var_checkbox)

            # Formatear texto del evento
            fecha_inicio = evento.get("fecha_inicio", "N/A")
            duracion = evento.get("duracion_dias", 1)

            # Mostrar información resumida
            recursos_count = len(
                evento.get("recursos", evento.get("recursos_detalle", []))
            )
            texto_evento = f"Evento #{i+1}: {evento['tipo']} - {fecha_inicio} ({duracion} días, {recursos_count} recursos)"

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

    # .11 ========= Seleccionar todos los eventos para eliminar=========
    def toggle_seleccionar_todos_eventos(self, var_todos):
        estado = var_todos.get()
        if hasattr(self, "checkboxes_eliminar"):
            for checkbox_var in self.checkboxes_eliminar:
                checkbox_var.set(estado)

    # .12 ========= Confirmar eliminación =============
    def confirmar_eliminacion(self, ventana_eliminar):
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
            f"Esta acción devolverá:\n"
            f"• Equipos al inventario\n"
            f"• Combustible a los tanques (el exceso se perderá)\n"
            f"• Eliminará permanentemente los eventos seleccionados",
        )

        if not respuesta:
            return

        # 4. Procesar cada evento a eliminar usando la función del módulo
        recursos_devueltos, combustible_devuelto, nuevos_eventos = (
            le.procesar_eliminacion_eventos(
                eventos_a_eliminar_indices,
                self.eventos_planificados.copy(),  # Usamos copia para no modificar la original directamente
                self.recursos,
            )
        )

        # 5. Actualizar la lista de eventos
        self.eventos_planificados = nuevos_eventos

        # 5.1. Actualizar contador y recursos disponibles
        self.actualizar_contador()
        self.crear_checkboxes_recursos()

        # 6. Guardar cambios
        self.guardar_recursos()
        self.guardar_eventos_en_json()

        # 7. Cerrar ventana
        ventana_eliminar.destroy()

        # 8. Generar y mostrar mensaje de éxito
        mensaje = le.generar_mensaje_resumen(
            eventos_a_eliminar_indices, recursos_devueltos, combustible_devuelto
        )
        self.lbl_info.configure(text=mensaje, text_color="green")

    # .14 ========= Crear serie de eventos ==========

    def crear_serie_recurrente(self):
        # 1. Obtener datos de la interfaz
        tipo_evento = self.combo_evento.get()
        day = self.entry_day.get()
        month = self.entry_month.get()
        year = self.entry_year.get()
        duracion = self.entry_duracion.get()
        intervalo = self.entry_intervalo.get()
        repeticiones = self.entry_repeticiones.get()

        # 2. Verificar si hay recursos seleccionados
        tiene_recursos = hasattr(self, "checkbox_vars") and any(
            v.get() for v in self.checkbox_vars.values()
        )

        # 3. Validar datos usando el módulo
        valido, mensaje, datos_validados = ls.validar_datos_serie(
            tipo_evento,
            day,
            month,
            year,
            duracion,
            intervalo,
            repeticiones,
            tiene_recursos,
        )

        if not valido:
            self.lbl_info.configure(text=mensaje, text_color="red")
            return

        # 4. Obtener recursos seleccionados
        recursos_seleccionados = [k for k, v in self.checkbox_vars.items() if v.get()]

        # 5. Confirmar con usuario
        texto_confirmacion = ls.generar_texto_confirmacion_serie(datos_validados)
        respuesta = messagebox.askyesno(
            "Confirmar serie recurrente", texto_confirmacion
        )

        if not respuesta:
            return

        # 6. Llamar a la función de creación de serie
        exito, mensaje, eventos_creados, fecha_problema = fsr.crear_serie_recurrente(
            tipo_evento=tipo_evento,
            recursos_seleccionados_nombres=recursos_seleccionados,
            fecha_inicio_str=datos_validados["fecha_str"],
            duracion_dias=datos_validados["duracion"],
            intervalo_dias=datos_validados["intervalo"],
            num_eventos=datos_validados["repeticiones"],
            recursos=self.recursos,
            eventos_planificados=self.eventos_planificados,
            tipos_evento_data=self.tipos_evento_data,
            app=self,
        )

        # 7. Manejar resultado
        if exito and eventos_creados:
            # NO agregar eventos aquí - la función ya los agregó a eventos_planificados
            self.guardar_eventos_en_json()
            self.guardar_recursos()
            self.actualizar_contador()
            self.crear_checkboxes_recursos()

            # Limpiar campos después de éxito
            self.entry_day.delete(0, "end")
            self.entry_month.delete(0, "end")
            self.entry_year.delete(0, "end")
            self.entry_duracion.delete(0, "end")
            self.entry_intervalo.delete(0, "end")
            self.entry_repeticiones.delete(0, "end")
            self.entry_intervalo.insert(0, "7")
            self.entry_repeticiones.insert(0, "1")
            self.combo_evento.set("Elige un tipo de evento")
            self.limpiar_seleccion_recursos()

            self.lbl_info.configure(
                text=mensaje,
                text_color="green",
            )

        elif fecha_problema:
            # SOLO sugerir buscar fecha alternativa si es error de solapamiento
            respuesta_alt = messagebox.askyesno(
                "Conflicto de fecha",
                f"No se pudo crear el evento del {fecha_problema.strftime('%d/%m/%Y')}\n\n"
                f"Razón: {mensaje}\n\n"
                f"¿Quieres que busque una fecha alternativa para toda la serie?",
            )

            if respuesta_alt:
                self.sugerir_serie_completa()
        else:
            # Error de validación: mostrar solo el error (ya es corto)
            self.lbl_info.configure(text=mensaje, text_color="red")

    # .15 ========= sugerir serie ===================
    def sugerir_serie_completa(self):
        # --- 1. CAPTURA DE DATOS DE LA INTERFAZ ---
        tipo = self.combo_evento.get()
        duracion = self.entry_duracion.get()
        repeticiones = self.entry_repeticiones.get()
        intervalo = self.entry_intervalo.get()

        # --- 2. VERIFICAR SI HAY RECURSOS SELECCIONADOS ---
        tiene_recursos = hasattr(self, "checkbox_vars") and any(
            v.get() for v in self.checkbox_vars.values()
        )

        # --- 3. VALIDAR DATOS USANDO EL MÓDULO ---
        valido, mensaje, datos_validados = ls.validar_datos_sugerencia_serie(
            tipo, duracion, repeticiones, intervalo, tiene_recursos
        )

        if not valido:
            self.lbl_info.configure(text=mensaje, text_color="red")
            return

        # --- 4. OBTENER RECURSOS SELECCIONADOS ---
        recursos_check = [k for k, v in self.checkbox_vars.items() if v.get()]

        # --- 5. LLAMADA AL MOTOR DE BÚSQUEDA ---
        self.lbl_info.configure(
            text="🔍 Buscando fechas disponibles...", text_color="orange"
        )
        self.update()

        # Esta función ya incluye todas las validaciones
        exito, fecha, mensaje = fsr.buscar_serie_completa_disponible(
            tipo_evento=datos_validados["tipo_evento"],
            recursos_seleccionados_nombres=recursos_check,
            duracion_dias=datos_validados["duracion"],
            intervalo_dias=datos_validados["intervalo"],
            num_eventos=datos_validados["repeticiones"],
            recursos=self.recursos,
            eventos_planificados=self.eventos_planificados,
            tipos_evento_data=self.tipos_evento_data,
            app=self,
        )

        # --- 6. GESTIÓN DEL RESULTADO ---
        if exito:
            # Si encontramos fecha, llenamos los campos automáticamente
            self.actualizar_campos_fecha(fecha)
            self.lbl_info.configure(text=mensaje, text_color="#4CAF50")
        else:
            # Verificar si es un error de combustible y mejorar el mensaje
            mensaje_lower = mensaje.lower()
            if any(
                palabra in mensaje_lower
                for palabra in [
                    "combustible",
                    "fuel",
                    "litro",
                    "litros",
                    "capacidad insuficiente",
                    "stock",
                ]
            ):
                mensaje_mejorado = (
                    f"{mensaje}\n\n💡 Usa 'Rellenar Todo' para reponer combustible."
                )
                self.lbl_info.configure(text=mensaje_mejorado, text_color="red")
            else:
                self.lbl_info.configure(text=mensaje, text_color="red")

    ################## INTERFAZ ###################

    def crear_interfaz(self):
        # ========== Titulo ==========
        lbl_titulo = ctk.CTkLabel(
            self,
            text="GESTOR DE EVENTOS ESPACIALES",
            font=("Monaco", 25, "bold"),
            text_color="#1087BF",
        )
        lbl_titulo.pack(pady=20)

        # ========== seleccion de evento ==========
        frame_evento = ctk.CTkFrame(self)
        frame_evento.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            frame_evento,
            text="Seleccionar Tipo de Evento:",
            font=("Monaco", 18, "bold"),
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
            font=("Monaco", 16),
        ).pack(pady=5)

        # Frame con borde blanco
        frame_borde = ctk.CTkFrame(
            frame_recursos,
            width=344,
            height=190,
            border_color="white",
            border_width=2,
            corner_radius=0,
            fg_color="transparent",
        )
        frame_borde.pack(side="left")
        frame_borde.grid_propagate(False)

        # Frame scrollable dentro
        self.frame_checkboxes = ctk.CTkScrollableFrame(
            frame_borde,
            width=340,
            height=186,
            border_width=0,
            fg_color="#2B2B2B",
        )

        # Usar grid para control preciso
        self.frame_checkboxes.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        frame_borde.grid_rowconfigure(0, weight=1)
        frame_borde.grid_columnconfigure(0, weight=1)

        # ========== 5. FECHA DEL EVENTO ==========
        frame_fecha_evento = ctk.CTkFrame(
            frame_recursos, width=50, border_color="white", border_width=2
        )
        frame_fecha_evento.pack(side="left", padx=5)

        ctk.CTkLabel(
            frame_fecha_evento, text="Fecha del Evento:", font=("Monaco", 15)
        ).pack(pady=4)

        # Frame para organizar los campos de fecha
        frame_campos_fecha = ctk.CTkFrame(frame_fecha_evento)
        frame_campos_fecha.pack(side="left", padx=80, pady=2)

        # Day
        self.entry_day = ctk.CTkEntry(
            frame_campos_fecha,
            placeholder_text="Día",
            width=125,
            border_color="#F2F3F2",
            border_width=2,
        )
        self.entry_day.pack(pady=5, padx=5)

        # Separador
        # ctk.CTkLabel(frame_campos_fecha, text="/").pack(side="left", padx=2)

        # month
        self.entry_month = ctk.CTkEntry(
            frame_campos_fecha,
            placeholder_text="Mes",
            width=125,
            border_color="#F2F3F2",
            border_width=2,
        )
        self.entry_month.pack(pady=5, padx=5)

        # Separador
        # ctk.CTkLabel(frame_campos_fecha, text="/").pack(side="left", padx=2)

        # Año
        self.entry_year = ctk.CTkEntry(
            frame_campos_fecha,
            placeholder_text="Año",
            width=125,
            border_color="#F2F3F2",
            border_width=2,
        )
        self.entry_year.pack(pady=5, padx=5)

        self.entry_duracion = ctk.CTkEntry(
            frame_campos_fecha,
            placeholder_text="Días de duración",
            width=125,
            border_color="#F2F3F2",
            border_width=2,
        )
        self.entry_duracion.pack(pady=5)

        # ========== botones recursos ==========
        frame_botones_recursos = ctk.CTkFrame(self)
        frame_botones_recursos.pack(pady=10)

        # Botón para marcar recursos recomendados
        btn_marcar_recomendados = ctk.CTkButton(
            frame_botones_recursos,
            text="✓ Marcar Recomendados",
            width=150,
            fg_color="#2196F3",
            hover_color="#1976D2",
            command=self.marcar_recursos_recomendados,
        )
        btn_marcar_recomendados.pack(side="left", padx=5)

        # Botón para limpiar selección
        btn_limpiar = ctk.CTkButton(
            frame_botones_recursos,
            text="🗑️ Limpiar Selección",
            width=150,
            fg_color="#FF9800",
            hover_color="#F57C00",
            command=self.limpiar_seleccion_recursos,
        )
        btn_limpiar.pack(side="left", padx=5)

        # ========== 5. RECURRENCIA (NUEVA SECCIÓN) ==========
        frame_recurrencia = ctk.CTkFrame(self)
        frame_recurrencia.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(frame_recurrencia, text="Recurrencia:", font=("Monaco", 14)).pack(
            pady=5
        )

        frame_campos_recurrencia = ctk.CTkFrame(frame_recurrencia)
        frame_campos_recurrencia.pack(pady=5)

        # Intervalo
        ctk.CTkLabel(frame_campos_recurrencia, text="Cada:").pack(side="left", padx=5)
        self.entry_intervalo = ctk.CTkEntry(
            frame_campos_recurrencia, width=60, border_color="#F2F3F2", border_width=2
        )
        self.entry_intervalo.pack(side="left", padx=5)
        self.entry_intervalo.insert(0, "")
        ctk.CTkLabel(frame_campos_recurrencia, text="días").pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(frame_campos_recurrencia, text=" | ").pack(side="left", padx=10)

        # Repeticiones
        ctk.CTkLabel(frame_campos_recurrencia, text="Repetir:").pack(
            side="left", padx=5
        )
        self.entry_repeticiones = ctk.CTkEntry(
            frame_campos_recurrencia, width=60, border_color="#F2F3F2", border_width=2
        )
        self.entry_repeticiones.pack(side="left", padx=5)
        ctk.CTkLabel(frame_campos_recurrencia, text="veces").pack(side="left", padx=5)

        # Botones de serie
        frame_botones_serie = ctk.CTkFrame(frame_recurrencia)
        frame_botones_serie.pack(pady=10)

        btn_sugerir_serie = ctk.CTkButton(
            frame_botones_serie,
            text="🔍 Sugerir Serie",
            width=150,
            fg_color="#1f538d",
            command=self.sugerir_serie_completa,
        )
        btn_sugerir_serie.pack(side="left", padx=5)

        btn_crear_serie = ctk.CTkButton(
            frame_botones_serie,
            text="🔄 Crear Serie",
            font=("Monaco", 12, "bold"),
            width=150,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            command=self.crear_serie_recurrente,
        )
        btn_crear_serie.pack(side="left", padx=5)

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
            width=100,
            height=45,
            font=("Monaco", 14, "bold"),
            fg_color="#4CAF50",
            hover_color="#388E3C",
            command=self.crear_evento,
        )
        self.btn_crear.pack(pady=5)

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
        frame_contador.pack(pady=20, padx=20, fill="x")

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
