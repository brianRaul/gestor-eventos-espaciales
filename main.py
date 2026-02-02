import customtkinter as ctk
import json
from datetime import datetime, date, timedelta
from funciones_datos import *
from funciones_crear_evento import *
from funciones_buscar_hueco import *
from funciones_series_recurrentes import *


class GestorEventos(ctk.CTk):

    def __init__(self):
        super().__init__()

        # 1.Configurar ventana
        self.title("Gestor de Eventos Espaciales")
        self.geometry("650x930")

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
                text="❌ Selecciona un tipo de evento primero", text_color="red"
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
                if (
                    recurso_info["categoria"].upper() == categoria_req
                    and recurso_info["tipo"].upper() == tipo_req
                ):

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
                text_color="orange",
            )

    # .3 ========== Crear evento ======================
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
            tipos_evento_data=self.tipos_evento_data,
        )

        # 4. Manejar el resultado (INTERFAZ GRÁFICA)
        if resultado and nuevo_evento:
            # Agregar información detallada de los recursos al evento
            recursos_detalle = []

            for recurso_nombre in recursos_seleccionados_nombres:
                # Buscar el recurso en la lista completa para obtener sus detalles
                for recurso in self.recursos:
                    if recurso["nombre_mostrar"] == recurso_nombre:
                        recurso_detalle = {
                            "nombre_mostrar": recurso["nombre_mostrar"],
                            "categoria": recurso["categoria"],
                            "tipo": recurso["tipo"],
                            "es_combustible": recurso.get("es_combustible", False),
                            "cantidad": 1,  # Por defecto 1, puedes ajustar según necesidad
                        }

                        # Para combustible, registrar la cantidad consumida
                        if recurso.get("es_combustible", False):
                            # Buscar en los recursos requeridos del tipo de evento para saber cuánto combustible se necesita
                            evento_data = self.tipos_evento_data.get(tipo_evento, {})
                            recursos_requeridos = evento_data.get(
                                "recursos_requeridos", []
                            )

                            for req in recursos_requeridos:
                                if (
                                    req["categoria"].upper()
                                    == recurso["categoria"].upper()
                                    and req["tipo"].upper() == recurso["tipo"].upper()
                                ):
                                    recurso_detalle["cantidad"] = req.get("cantidad", 1)
                                    break

                        recursos_detalle.append(recurso_detalle)
                        break

            # Agregar los recursos detallados al evento
            nuevo_evento["recursos_detalle"] = recursos_detalle

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
            fecha_str = datetime.strptime(
                nuevo_evento["fecha_inicio"], "%d/%m/%Y"
            ).strftime("%d/%m")
            self.lbl_info.configure(
                text=f"🚀 Evento '{tipo_evento}' creado exitosamente ({fecha_str})",
                text_color="green",
            )
        else:
            # Error: mostrar mensaje
            if (
                "combustible" in mensaje.lower()
                or "fuel" in mensaje.lower()
                or "litro" in mensaje.lower()
            ):
                mensaje_mejorado = (
                    f"❌ NO SE PUEDE CREAR EL EVENTO:\nFalta combustible\n{mensaje}"
                )
            else:
                mensaje_mejorado = f"❌ NO SE PUEDE CREAR EL EVENTO:\n{mensaje}"

            self.lbl_info.configure(text=mensaje_mejorado, text_color="red")

    # .4 ========== Limpiar selección =================
    def limpiar_seleccion_recursos(self):
        """Desmarcar todos los checkboxes de recursos"""
        if hasattr(self, "checkbox_vars"):
            for var in self.checkbox_vars.values():
                var.set(False)
            self.lbl_info.configure(
                text="Todos los recursos desmarcados", text_color="orange"
            )

    # .5 ========== Mostrar eventos planificados ======
    def mostrar_eventos_planificados(self):
        # Crear una nueva ventana emergente
        ventana_eventos = ctk.CTkToplevel(self)
        ventana_eventos.title("📋 Eventos Planificados")
        ventana_eventos.geometry("440x400")

        # Título
        titulo = ctk.CTkLabel(
            ventana_eventos, text="EVENTOS PLANIFICADOS", font=("Arial", 16, "bold")
        )
        titulo.pack(pady=10)

        # Frame para contener los eventos con scroll
        frame_contenedor = ctk.CTkScrollableFrame(
            ventana_eventos, width=550, height=400
        )
        frame_contenedor.pack(pady=10, padx=10, fill="both", expand=True)

        # Verificar si hay eventos
        if not self.eventos_planificados:
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
                lbl_fecha = ctk.CTkLabel(
                    contenido_evento,
                    text=f"📅 Inicio: {evento.get('fecha_inicio', evento.get('fecha', 'N/A'))} | Fin: {evento.get('fecha_fin', 'N/A')}",
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
                    command=lambda ev=evento: self.mostrar_recursos_evento(ev),
                )
                btn_recursos.grid(
                    row=0, column=1, rowspan=4, padx=(20, 0), pady=5, sticky="e"
                )

        # Botón para cerrar la ventana
        btn_cerrar = ctk.CTkButton(
            ventana_eventos, text="Cerrar", width=100, command=ventana_eventos.destroy
        )
        btn_cerrar.pack(pady=10)

    # .5.1 ========== Mostrar recursos de un evento ======
    def mostrar_recursos_evento(self, evento):

        # Crear ventana emergente
        ventana_recursos = ctk.CTkToplevel(self)
        ventana_recursos.title(f"📦 Recursos del Evento: {evento['tipo']}")
        ventana_recursos.geometry("500x500")

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

        # Verificar si hay recursos - intentar diferentes nombres de campo
        recursos = (
            evento.get("recursos_detalle")
            or evento.get("recursos")
            or evento.get("recursos_utilizados")
            or []
        )

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

            ctk.CTkLabel(resumen_frame, text=resumen_text, font=("Arial", 11)).pack(
                pady=5
            )

        # Botón para cerrar
        btn_cerrar = ctk.CTkButton(
            ventana_recursos, text="Cerrar", width=100, command=ventana_recursos.destroy
        )
        btn_cerrar.pack(pady=10)

    # .6 ========== Sugerir Fecha =====================
    def sugerir_fecha_disponible(self):
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
            disponible, mensaje_disponibilidad = verificar_disponibilidad_fecha(
                fecha_busqueda,
                fecha_fin,
                recursos_necesarios,
                self.eventos_planificados,
                self.recursos,
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
        if self.ventana_combustible is not None and self.ventana_combustible.winfo_exists():
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
        frame_scroll = ctk.CTkScrollableFrame(self.ventana_combustible, width=350, height=250)
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
        ctk.CTkButton(
            self.ventana_combustible, 
            text="Cerrar", 
            command=on_close
        ).pack(pady=10)
    # .9 ========== Rellenar sistema de combustible ===
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
            
            # ACTUALIZACIÓN: Si la ventana está abierta, cierra y vuelve a abrir
            if self.ventana_combustible is not None and self.ventana_combustible.winfo_exists():
                self.ventana_combustible.destroy()
                self.ventana_combustible = None
                self.ver_combustible()  # Abre nueva ventana con datos actualizados
            
            # Mensaje de éxito
            mensaje = f"✅ Combustible rellenado\n⛽ +{litros_agregados:,} litros"
            self.lbl_info.configure(text=mensaje, text_color="green")
        else:
            self.lbl_info.configure(
                text="ℹ️ Todo el combustible ya está lleno", 
                text_color="orange"
            )

    # .10 ========= Eliminar Eventos ==================
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
            command=lambda: self.toggle_seleccionar_todos(
                self.checkboxes_eliminar, self.var_seleccionar_todos
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
            texto_evento = (
                f"Evento #{i+1}: {evento['tipo']} - {fecha_inicio} ({duracion} días)"
            )

            checkbox = ctk.CTkCheckBox(
                frame_scroll,
                text=texto_evento,
                variable=var_checkbox,
                onvalue=True,
                offvalue=False,
                font=("Arial", 11),
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

    # .11 ========= Seleccionar todos los eventos para eliminar=========
    def toggle_seleccionar_todos(self, checkboxes_list, var_todos):
        estado = var_todos.get()
        for checkbox_var in checkboxes_list:
            checkbox_var.set(estado)

    # .12 ========= Confirmar eliminación =============
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

        # 3. Pedir confirmación (actualizado para mencionar combustible)
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar {len(eventos_a_eliminar_indices)} evento(s)?\n\n"
            f"Esta acción devolverá:\n"
            f"• Equipos al inventario\n"
            f"• Combustible a los tanques\n"
            f"• Eliminará permanentemente los eventos seleccionados",
        )

        if not respuesta:
            return

        # 5. Procesar cada evento a eliminar (orden inverso)
        recursos_devueltos = []
        combustible_devuelto = []
        eventos_a_eliminar_indices.sort(reverse=True)

        for indice in eventos_a_eliminar_indices:
            if indice >= len(self.eventos_planificados):
                continue

            evento = self.eventos_planificados[indice]

            # Devolver TODOS los recursos (equipos y combustible)
            for recurso_detalle in evento.get("recursos_detalle", []):
                # Buscar el recurso en la lista de recursos
                for recurso in self.recursos:
                    if recurso["nombre_mostrar"] == recurso_detalle["nombre_mostrar"]:

                        # Verificar si es combustible
                        es_combustible = recurso_detalle.get("es_combustible", False)

                        # Intentar detectar por nombre si no está marcado
                        if not es_combustible:
                            nombre = recurso["nombre_mostrar"].lower()
                            categoria = recurso["categoria"].lower()
                            if (
                                "combustible" in nombre
                                or "combustible" in categoria
                                or "fuel" in nombre
                            ):
                                es_combustible = True

                        if es_combustible:
                            # COMBUSTIBLE: devolver al tanque
                            cantidad_usada = recurso_detalle.get("cantidad", 0)
                            if cantidad_usada > 0:
                                # Asegurarse de no exceder la capacidad
                                nuevo_valor = min(
                                    recurso["cantidad_disponible"] + cantidad_usada,
                                    recurso["cantidad_total"],
                                )
                                litros_devueltos = (
                                    nuevo_valor - recurso["cantidad_disponible"]
                                )

                                if litros_devueltos > 0:
                                    recurso["cantidad_disponible"] = nuevo_valor
                                    combustible_devuelto.append(
                                        {
                                            "nombre": recurso["nombre_mostrar"],
                                            "litros": litros_devueltos,
                                            "nuevo_total": nuevo_valor,
                                        }
                                    )
                                    print(
                                        f"🔥 Combustible devuelto: {recurso['nombre_mostrar']} +{litros_devueltos}L"
                                    )

                        else:
                            # EQUIPOS: liberar para uso futuro
                            recursos_devueltos.append(
                                {
                                    "nombre": recurso["nombre_mostrar"],
                                    "categoria": recurso["categoria"],
                                }
                            )
                            print(f"🔄 Equipo liberado: {recurso['nombre_mostrar']}")
                        break

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

        # Resumen de equipos liberados
        if recursos_devueltos:
            equipos_unicos = len(set(item["nombre"] for item in recursos_devueltos))
            mensaje += f"\n🔄 {equipos_unicos} equipo(s) liberado(s)."

        # Resumen de combustible devuelto
        if combustible_devuelto:
            total_litros = sum(item["litros"] for item in combustible_devuelto)
            if len(combustible_devuelto) == 1:
                mensaje += f"\n⛽ +{total_litros}L devueltos a {combustible_devuelto[0]['nombre']}."
            else:
                mensaje += f"\n⛽ +{total_litros}L de combustible devueltos."

        self.lbl_info.configure(text=mensaje, text_color="green")

    def sugerir_serie_completa(self):
        """Busca y sugiere una fecha que pueda acomodar TODA la serie recurrente"""

        # 1. Validar tipo de evento
        tipo_evento = self.combo_evento.get()
        if not tipo_evento or tipo_evento == "Elige un tipo de evento":
            self.lbl_info.configure(
                text="❌ Selecciona un tipo de evento primero", text_color="red"
            )
            return

        # 2. Validar campos de fecha y duración
        day = self.entry_day.get()
        month = self.entry_month.get()
        year = self.entry_year.get()
        duracion = self.entry_duracion.get()

        if not all([day, month, year, duracion]):
            self.lbl_info.configure(
                text="❌ Completa todos los campos de fecha y duración",
                text_color="red",
            )
            return

        # 3. Validar campos de recurrencia
        intervalo = self.entry_intervalo.get() or "7"
        repeticiones = self.entry_repeticiones.get() or "1"

        try:
            intervalo_int = int(intervalo)
            repeticiones_int = int(repeticiones)
            duracion_int = int(duracion)

            if intervalo_int <= 0 or repeticiones_int <= 0 or duracion_int <= 0:
                self.lbl_info.configure(
                    text="❌ Valores deben ser mayores a 0", text_color="red"
                )
                return
            if intervalo_int < duracion_int:
              self.lbl_info.configure(
                text=f"❌ Error: Intervalo ({intervalo_int} días) < Duración ({duracion_int} días)\n" f"Los eventos se solaparían. Usa intervalo ≥ duración.", text_color="red"
                )
              return
        except ValueError:
            self.lbl_info.configure(
                text="❌ Usa números válidos en todos los campos", text_color="red"
            )
            return

        # 4. Obtener recursos seleccionados (directamente)
        if not hasattr(self, "checkbox_vars"):
            self.lbl_info.configure(
                text="❌ Error: no se cargaron los recursos", text_color="red"
            )
            return

        recursos_seleccionados = [k for k, v in self.checkbox_vars.items() if v.get()]

        if not recursos_seleccionados:
            self.lbl_info.configure(
                text="❌ Selecciona al menos un recurso", text_color="red"
            )
            return

        # 5. Convertir fecha
        try:
            fecha_inicio = datetime.strptime(f"{day}/{month}/{year}", "%d/%m/%Y").date()
        except ValueError:
            self.lbl_info.configure(
                text="❌ Fecha inválida. Usa formato DD/MM/YYYY", text_color="red"
            )
            return

        exito, fecha_sugerida, mensaje = buscar_serie_completa_disponible(
            tipo_evento=tipo_evento,
            recursos_seleccionados_nombres=recursos_seleccionados,
            duracion_dias=duracion_int,
            intervalo_dias=intervalo_int,
            num_eventos=repeticiones_int,
            recursos=self.recursos,
            eventos_planificados=self.eventos_planificados,
            tipos_evento_data=self.tipos_evento_data,
            fecha_inicio_busqueda=fecha_inicio,
        )

        # 7. Manejar resultado
        if exito:
            # Usar función existente para actualizar campos
            self.actualizar_campos_fecha(fecha_sugerida)
            self.lbl_info.configure(
                text=f"✅ {mensaje}\nAhora puedes crear la serie con confianza.",
                text_color="green",
            )
        else:
            self.lbl_info.configure(text=mensaje, text_color="red")

    def crear_serie_recurrente(self):
        import tkinter.messagebox as messagebox

        # 1. Validar tipo de evento
        tipo_evento = self.combo_evento.get()
        if not tipo_evento or tipo_evento == "Elige un tipo de evento":
            self.lbl_info.configure(
                text="❌ Selecciona un tipo de evento primero", text_color="red"
            )
            return

        # 2. Validar campos de fecha y duración
        day = self.entry_day.get()
        month = self.entry_month.get()
        year = self.entry_year.get()
        duracion = self.entry_duracion.get()

        if not all([day, month, year, duracion]):
            self.lbl_info.configure(
                text="❌ Completa todos los campos de fecha y duración",
                text_color="red",
            )
            return

        # 3. Validar campos de recurrencia
        intervalo = self.entry_intervalo.get() or "7"
        repeticiones = self.entry_repeticiones.get() or "1"

        try:
            intervalo_int = int(intervalo)
            repeticiones_int = int(repeticiones)
            duracion_int = int(duracion)

            if intervalo_int <= 0 or repeticiones_int <= 0 or duracion_int <= 0:
                self.lbl_info.configure(
                    text="❌ Valores deben ser mayores a 0", text_color="red"
                )
                return
        except ValueError:
            self.lbl_info.configure(
                text="❌ Usa números válidos en todos los campos", text_color="red"
            )
            return

        # 4. Obtener recursos seleccionados (directamente)
        if not hasattr(self, "checkbox_vars"):
            self.lbl_info.configure(
                text="❌ Error: no se cargaron los recursos", text_color="red"
            )
            return

        recursos_seleccionados = [k for k, v in self.checkbox_vars.items() if v.get()]

        if not recursos_seleccionados:
            self.lbl_info.configure(
                text="❌ Selecciona al menos un recurso", text_color="red"
            )
            return

        # 5. Si solo 1 repetición, usar función normal de evento único
        if repeticiones_int == 1:
            self.crear_evento()
            return

        # 6. Confirmar con usuario
        respuesta = messagebox.askyesno(
            "Confirmar serie recurrente",
            f"¿Crear serie de {repeticiones_int} eventos?\n\n"
            f"• Cada {intervalo_int} días\n"
            f"• Tipo: {tipo_evento}\n"
            f"• Recursos: {len(recursos_seleccionados)}\n"
            f"• Duración por evento: {duracion_int} días\n\n"
            f"El sistema validará cada evento individualmente.",
        )

        if not respuesta:
            return

        fecha_str = f"{day}/{month}/{year}"

        exito, mensaje, eventos_creados, fecha_problema = crear_serie_recurrente(
            tipo_evento=tipo_evento,
            recursos_seleccionados_nombres=recursos_seleccionados,
            fecha_inicio_str=fecha_str,
            duracion_dias=duracion_int,
            intervalo_dias=intervalo_int,
            num_eventos=repeticiones_int,
            recursos=self.recursos,
            eventos_planificados=self.eventos_planificados,
            tipos_evento_data=self.tipos_evento_data,
            app=self,
        )

        # 7. Manejar resultado
        if exito and eventos_creados:
            # NO agregar eventos aquí - la función ya los agregó a eventos_planificados
            # Solo guardar y actualizar la interfaz

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

            if hasattr(self, "limpiar_seleccion_recursos"):
                self.limpiar_seleccion_recursos()

            self.lbl_info.configure(
                text=f"✅ Serie creada exitosamente: {len(eventos_creados)} eventos",
                text_color="green",
            )

        elif fecha_problema:
            respuesta_alt = messagebox.askyesno(
                "Conflicto de fecha",
                f"No se pudo crear el evento para {fecha_problema.strftime('%d/%m/%Y')}\n\n"
                f"¿Quieres que busque una fecha alternativa para toda la serie?",
            )

            if respuesta_alt:
                self.sugerir_serie_completa()
        else:
            self.lbl_info.configure(text=mensaje, text_color="red")

    ################## INTERFAZ ###################

    def crear_interfaz(self):
        # ========== Titulo ==========
        lbl_titulo = ctk.CTkLabel(
            self,
            text="GESTOR DE EVENTOS ESPACIALES",
            font=("Monaco", 25, "bold"),
            text_color="#4FC3F7",
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
            width=304,
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
            width=300,  
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
            frame_recursos, width=100, border_color="white", border_width=2
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
            width=120,
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
            width=120,
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
            width=120,
            border_color="#F2F3F2",
            border_width=2,
        )
        self.entry_year.pack(pady=5, padx=5)

        self.entry_duracion = ctk.CTkEntry(
            frame_campos_fecha,
            placeholder_text="Días de duración",
            width=120,
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
            font=("Monaco",12,"bold"),
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
