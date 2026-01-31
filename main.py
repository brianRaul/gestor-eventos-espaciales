import customtkinter as ctk
import json
from funciones_datos import *
from datetime import datetime, date, timedelta


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

                # Para TODOS los recursos, guardar ambos campos
                recurso_data = {
                    "modelo": recurso["modelo"],
                    "tipo": recurso["tipo"],
                    "cantidad_total": recurso["cantidad_total"],
                    "cantidad_disponible": recurso[
                        "cantidad_disponible"
                    ],  # ¡GUARDAR DISPONIBILIDAD!
                }

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

                # Mostrar cantidad DISPONIBLE vs TOTAL
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

        # Primero desmarcamos todo
        self.limpiar_seleccion_recursos()

        # Obtenemos los recursos requeridos para este evento
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

        # Para cada recurso requerido
        for req in recursos_requeridos:
            categoria_req = req["categoria"].upper()
            tipo_req = req["tipo"].upper()
            cantidad_req = req.get("cantidad", 1)

            # Buscar recursos que coincidan con la categoría y tipo
            recursos_encontrados = 0

            for recurso_nombre, checkbox_var in self.checkbox_vars.items():
                # Buscar el recurso en la lista completa para obtener sus detalles
                recurso_info = None
                for r in self.recursos:
                    if r["nombre_mostrar"] == recurso_nombre:
                        recurso_info = r
                        break

                if not recurso_info:
                    continue

                # Verificar si coincide con el requerimiento
                # Verificar si coincide con el requerimiento
                if (
                    recurso_info["categoria"].upper() == categoria_req
                    and recurso_info["tipo"].upper() == tipo_req
                ):

                    # Para recursos no combustibles, verificar disponibilidad
                    if not recurso_info["es_combustible"]:
                        # NO verificamos cantidad_disponible, solo marcamos
                        checkbox_var.set(True)
                        recursos_encontrados += 1
                        recursos_marcados += 1
                    else:
                        # Para combustible, verificar disponibilidad
                        if recurso_info["cantidad_disponible"] >= cantidad_req:
                            checkbox_var.set(True)
                            recursos_encontrados += 1
                            recursos_marcados += 1

                    # Si ya encontramos la cantidad necesaria, pasamos al siguiente requerimiento
                    if recursos_encontrados >= cantidad_req:
                        break

    # .3 ========== Crear evento ==========
    def crear_evento(self):
        # Obtención y validación de los datos
        tipo_evento = self.combo_evento.get()

        if not tipo_evento or tipo_evento == "Elige un tipo de evento":
            self.lbl_info.configure(
                text="❌ Selecciona un tipo de evento", text_color="red"
            )
            return

        # Obtener datos del evento de la NUEVA estructura
        if tipo_evento not in self.tipos_evento_data:
            self.lbl_info.configure(
                text="❌ Tipo de evento no encontrado", text_color="red"
            )
            return

        evento_data = self.tipos_evento_data[tipo_evento]
        recursos_requeridos = evento_data.get("recursos_requeridos", [])

        # Validar fecha
        day, month, year = (
            self.entry_day.get(),
            self.entry_month.get(),
            self.entry_year.get(),
        )
        duracion_str = self.entry_duracion.get()

        try:
            fecha_inicio = datetime(int(year), int(month), int(day))
            if fecha_inicio.date() < datetime.now().date():
                self.lbl_info.configure(
                    text="❌ No puedes planificar en el pasado", text_color="red"
                )
                return

            duracion = int(duracion_str)
            if duracion <= 0:
                self.lbl_info.configure(
                    text="❌ La duración debe ser mayor a 0", text_color="red"
                )
                return

            # Calcular fecha fin
            fecha_fin = fecha_inicio + timedelta(days=duracion - 1)
        except ValueError:
            self.lbl_info.configure(
                text="❌ Fecha o duración inválida", text_color="red"
            )
            return

        # Validar duración min/max del evento
        config_evento = evento_data.get("configuracion_evento", {})
        d_min = config_evento.get("duracion_minima", 1)
        d_max = config_evento.get("duracion_maxima", 30)
        if not (d_min <= duracion <= d_max):
            self.lbl_info.configure(
                text=f"❌ Duración permitida: {d_min}-{d_max} días",
                text_color="red",
            )
            return

        # Obtener recursos seleccionados (checkboxes)
        recursos_seleccionados_nombres = [
            k for k, v in self.checkbox_vars.items() if v.get()
        ]

        if not recursos_seleccionados_nombres:
            self.lbl_info.configure(
                text="❌ Selecciona al menos un recurso", text_color="red"
            )
            return

        # Convertir nombres a información completa de recursos
        recursos_seleccionados = []
        for nombre_mostrar in recursos_seleccionados_nombres:
            for recurso in self.recursos:
                if recurso["nombre_mostrar"] == nombre_mostrar:
                    recursos_seleccionados.append(recurso)
                    break

        # ========== NUEVA: Validación A - Reglas de Exclusión ==========
        reglas_exclusion = evento_data.get("reglas_exclusion", [])
        for regla in reglas_exclusion:
            categoria_prohibida = regla.get("categoria", "")
            tipos_prohibidos = regla.get("tipos_prohibidos", [])

            for recurso in recursos_seleccionados:
                if (
                    recurso["categoria"] == categoria_prohibida
                    and recurso["tipo"] in tipos_prohibidos
                ):
                    self.lbl_info.configure(
                        text=f"⛔ RECURSO PROHIBIDO: '{recurso['nombre_mostrar']}' no está permitido para este evento.",
                        text_color="red",
                    )
                    return

        # ========== NUEVA: Validación B - Requisitos Coexistentes ==========
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
                        if (
                            recurso["categoria"] == cat_req
                            and recurso["tipo"] == tipo_req
                        ):
                            encontrado = True
                            break

                    if not encontrado:
                        self.lbl_info.configure(
                            text=f"❌ '{categoria_principal} {tipo_principal}' requiere también '{cat_req} {tipo_req}'",
                            text_color="red",
                        )
                        return

                # ========== NUEVA: Validación C - Recursos Requeridos ==========
        # Agrupar recursos seleccionados por categoría y tipo
        recursos_seleccionados_dict = {}
        for recurso in recursos_seleccionados:
            clave = f"{recurso['categoria']}-{recurso['tipo']}"
            if clave not in recursos_seleccionados_dict:
                recursos_seleccionados_dict[clave] = []
            recursos_seleccionados_dict[clave].append(recurso)

        # Verificar cada recurso requerido
        for recurso_req in recursos_requeridos:
            categoria_req = recurso_req.get("categoria", "")
            tipo_req = recurso_req.get("tipo", "")
            cantidad_req = recurso_req.get("cantidad", 1)

            clave_req = f"{categoria_req}-{tipo_req}"

            if clave_req not in recursos_seleccionados_dict:
                self.lbl_info.configure(
                    text=f"❌ El recurso requerido '{categoria_req} {tipo_req}' no está seleccionado",
                    text_color="red",
                )
                return

            recursos_del_tipo = recursos_seleccionados_dict[clave_req]

            # Para combustible, verificar cantidad disponible
            if "COMBUSTIBLE" in categoria_req.upper():
                total_disponible = sum(
                    r["cantidad_disponible"] for r in recursos_del_tipo
                )
                if total_disponible < cantidad_req:
                    self.lbl_info.configure(
                        text=f"❌ No hay suficiente {categoria_req} {tipo_req}. Se necesitan {cantidad_req}, hay {total_disponible}",
                        text_color="red",
                    )
                    return
            else:
                # Para equipos: verificar ocupación en esas fechas
                capacidad_total = sum(r["cantidad_total"] for r in recursos_del_tipo)

                # Buscar eventos que se solapen
                cantidad_ocupada = 0
                for evento in self.eventos_planificados:
                    try:
                        ev_inicio = datetime.strptime(
                            evento["fecha_inicio"], "%d/%m/%Y"
                        ).date()
                        ev_fin = datetime.strptime(
                            evento["fecha_fin"], "%d/%m/%Y"
                        ).date()
                    except:
                        continue

                    # Verificar solapamiento
                    se_solapan = (fecha_inicio.date() <= ev_fin) and (
                        fecha_fin.date() >= ev_inicio
                    )

                    if se_solapan:
                        # Contar cuántos de este tipo usa el evento
                        for rd in evento.get("recursos_detalle", []):
                            if (
                                rd["categoria"] == categoria_req
                                and rd["tipo"] == tipo_req
                            ):
                                cantidad_ocupada += 1

                disponible = capacidad_total - cantidad_ocupada

                if disponible < cantidad_req:
                    self.lbl_info.configure(
                        text=f"❌ Ocupado en esas fechas: {categoria_req} {tipo_req}. (Total: {capacidad_total}, Ocupados: {cantidad_ocupada}, Necesarios: {cantidad_req})",
                        text_color="red",
                    )
                    return

        # ========== CONSUMIR RECURSOS ==========
        recursos_consumidos = []

        # Primero, procesar recursos combustibles (solo estos se consumen permanentemente)
        for recurso in recursos_seleccionados:
            if recurso["es_combustible"]:
                # Buscar el recurso combustible
                for r in self.recursos:
                    if r["nombre_mostrar"] == recurso["nombre_mostrar"]:
                        # Encontrar cuánto combustible necesita este evento
                        cantidad_necesaria = 0
                        for recurso_req in recursos_requeridos:
                            if (
                                recurso_req["categoria"] == r["categoria"]
                                and recurso_req["tipo"] == r["tipo"]
                            ):
                                cantidad_necesaria = recurso_req["cantidad"]
                                break

                        # Consumir el recurso (solo combustible se resta permanentemente)
                        r["cantidad_disponible"] -= cantidad_necesaria
                        recursos_consumidos.append(
                            {
                                "recurso": r["nombre_mostrar"],
                                "cantidad": cantidad_necesaria,
                                "es_consumible": True,
                            }
                        )
                        print(
                            f"🔥 Combustible consumido: {r['nombre_mostrar']} - {cantidad_necesaria}L"
                        )
                        break
            else:
                # Para recursos NO combustibles, NO restar de cantidad_disponible
                # Solo registrar que se usará en esas fechas
                recursos_consumidos.append(
                    {
                        "recurso": recurso["nombre_mostrar"],
                        "cantidad": 1,
                        "es_consumible": False,
                    }
                )
                print(
                    f"📅 Recurso asignado (no consumible): {recurso['nombre_mostrar']}"
                )

        # Guardar cambios en los recursos
        self.guardar_recursos()

        # Actualizar checkboxes para mostrar nueva disponibilidad
        self.crear_checkboxes_recursos()
        # ========== Crear diccionario de recursos usados ==========
        uso_recursos_evento = {}
        for recurso in recursos_seleccionados:
            if recurso["es_combustible"]:
                # Encontrar cuánto combustible necesita este evento para este tipo
                for recurso_req in recursos_requeridos:
                    if (
                        recurso_req["categoria"] == recurso["categoria"]
                        and recurso_req["tipo"] == recurso["tipo"]
                    ):
                        uso_recursos_evento[recurso["nombre_mostrar"]] = recurso_req[
                            "cantidad"
                        ]
                        break
            else:
                uso_recursos_evento[recurso["nombre_mostrar"]] = 1

                # ========== Crear nuevo evento ==========
        nuevo_evento = {
            "tipo": tipo_evento,
            "fecha_inicio": fecha_inicio.strftime("%d/%m/%Y"),
            "fecha_fin": fecha_fin.strftime("%d/%m/%Y"),
            "duracion_dias": duracion,
            "recursos": recursos_seleccionados_nombres,
            "recursos_detalle": [
                {
                    "nombre_mostrar": r["nombre_mostrar"],
                    "categoria": r["categoria"],
                    "modelo": r["modelo"],
                    "tipo": r["tipo"],
                    "es_combustible": r["es_combustible"],
                    "es_consumible": r["es_consumible"],
                }
                for r in recursos_seleccionados
            ],
            "recursos_usados": uso_recursos_evento,
            "recursos_consumidos": recursos_consumidos,
            "estado": "planificado",
        }

        self.eventos_planificados.append(nuevo_evento)
        self.guardar_eventos_en_json()
        self.actualizar_contador()

        # Limpieza
        self.entry_day.delete(0, "end")
        self.entry_month.delete(0, "end")
        self.entry_year.delete(0, "end")
        self.entry_duracion.delete(0, "end")
        self.combo_evento.set("Elige un tipo de evento")
        self.limpiar_seleccion_recursos()
        self.lbl_info.configure(
            text=f"🚀 Evento '{tipo_evento}' creado exitosamente ({fecha_inicio.strftime('%d/%m')})",
            text_color="green",
        )
        print(f"Evento creado: {nuevo_evento}")

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

        # Convertir a formato más manejable
        recursos_necesarios = {}
        for req in recursos_requeridos:
            clave = f"{req['categoria']}|{req['tipo']}"
            recursos_necesarios[clave] = {
                "categoria": req["categoria"],
                "tipo": req["tipo"],
                "cantidad": req["cantidad"],
                "es_combustible": "COMBUSTIBLE" in req["categoria"].upper(),
            }

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

            # Verificar disponibilidad para este rango de fechas
            disponible = self.verificar_disponibilidad_fecha(
                fecha_busqueda, fecha_fin, recursos_necesarios
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

    def verificar_disponibilidad_fecha(
        self, fecha_inicio, fecha_fin, recursos_necesarios
    ):

        print(f"\n🔍 Verificando disponibilidad para: {fecha_inicio} a {fecha_fin}")

        # 1. Buscar todos los eventos que se solapan con este rango
        eventos_solapados = []

        for evento in self.eventos_planificados:
            try:
                ev_inicio = datetime.strptime(evento["fecha_inicio"], "%d/%m/%Y").date()
                ev_fin = datetime.strptime(evento["fecha_fin"], "%d/%m/%Y").date()
            except:
                continue

            # Verificar solapamiento: fechas se cruzan
            se_solapan = (fecha_inicio <= ev_fin) and (fecha_fin >= ev_inicio)

            if se_solapan:
                eventos_solapados.append(evento)

        print(f"   Eventos solapados encontrados: {len(eventos_solapados)}")

        # Si no hay eventos solapados, verificar solo stock de combustible
        if not eventos_solapados:
            print("   ✅ No hay eventos solapados")
            for clave, req in recursos_necesarios.items():
                if req["es_combustible"]:
                    # Buscar stock disponible
                    stock_total = 0
                    for r in self.recursos:
                        if (
                            r["categoria"] == req["categoria"]
                            and r["tipo"] == req["tipo"]
                        ):
                            stock_total += r["cantidad_disponible"]

                    print(
                        f"   🔍 Combustible {req['categoria']} {req['tipo']}: Necesita {req['cantidad']}, hay {stock_total}"
                    )

                    if stock_total < req["cantidad"]:
                        print(
                            f"   ❌ No hay suficiente combustible: {req['categoria']} {req['tipo']}"
                        )
                        return False
            return True

        # 2. Si hay eventos solapados, calcular recursos ocupados
        recursos_ocupados = {}

        for evento in eventos_solapados:
            # Sumar recursos usados por este evento
            for recurso_usado, cantidad in evento.get("recursos_usados", {}).items():
                # Buscar categoría y tipo de este recurso
                for r_detalle in evento.get("recursos_detalle", []):
                    if r_detalle["nombre_mostrar"] == recurso_usado:
                        clave = f"{r_detalle['categoria']}|{r_detalle['tipo']}"

                        if clave not in recursos_ocupados:
                            recursos_ocupados[clave] = 0
                        recursos_ocupados[clave] += cantidad
                        break

        # 3. Verificar disponibilidad para cada recurso necesario
        for clave, req in recursos_necesarios.items():
            # Cantidad necesaria para nuestro nuevo evento
            cantidad_necesaria = req["cantidad"]

            # Si es combustible, solo verificar stock disponible
            if req["es_combustible"]:
                stock_total = 0
                for r in self.recursos:
                    if r["categoria"] == req["categoria"] and r["tipo"] == req["tipo"]:
                        stock_total += r["cantidad_disponible"]

                print(
                    f"   🔍 Combustible {req['categoria']} {req['tipo']}: Necesita {cantidad_necesaria}, hay {stock_total}"
                )

                if stock_total < cantidad_necesaria:
                    print(
                        f"   ❌ No hay suficiente combustible: {req['categoria']} {req['tipo']}"
                    )
                    return False
                continue

            # Para equipos: calcular capacidad total y verificar ocupación
            capacidad_total = 0
            for r in self.recursos:
                if r["categoria"] == req["categoria"] and r["tipo"] == req["tipo"]:
                    capacidad_total += r["cantidad_total"]

            # Cantidad ya ocupada en estas fechas
            cantidad_ocupada = recursos_ocupados.get(clave, 0)

            # Verificar si hay suficiente disponibilidad
            disponible = capacidad_total - cantidad_ocupada

            print(
                f"   🔍 Equipo {req['categoria']} {req['tipo']}: Capacidad {capacidad_total}, Ocupados {cantidad_ocupada}, Necesita {cantidad_necesaria}"
            )

            if disponible < cantidad_necesaria:
                print(
                    f"   ❌ No hay suficiente {req['categoria']} {req['tipo']} en estas fechas"
                )
                return False

        print("   ✅ Todos los recursos están disponibles")
        return True

    def actualizar_campos_fecha(self, fecha):
        """Rellena los campos de fecha con la fecha sugerida"""
        self.entry_day.delete(0, "end")
        self.entry_day.insert(0, str(fecha.day))

        self.entry_month.delete(0, "end")
        self.entry_month.insert(0, str(fecha.month))

        self.entry_year.delete(0, "end")
        self.entry_year.insert(0, str(fecha.year))

    def ver_combustible(self):
        """Abre ventana para ver el estado del combustible"""

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
        """Rellena todo el combustible"""

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

    def rellenar_combustible_con_actualizacion(self):
        """Rellena y actualiza la ventana si está abierta"""
        self.rellenar_combustible()

        # Buscar si hay ventana de combustible abierta
        for ventana in self.winfo_children():
            if (
                isinstance(ventana, ctk.CTkToplevel)
                and "Combustible" in ventana.title()
            ):
                ventana.destroy()
                self.ver_combustible()  # Abrir de nuevo con datos actualizados
                break

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

        # Lista para checkboxes
        self.checkboxes_eliminar = []

        # Crear checkboxes
        for i, evento in enumerate(self.eventos_planificados):
            var_checkbox = ctk.BooleanVar(value=False)
            self.checkboxes_eliminar.append(var_checkbox)

            texto_evento = f"Evento #{i+1}: {evento['tipo']} - {evento['fecha_inicio']}"

            checkbox = ctk.CTkCheckBox(
                frame_scroll,
                text=texto_evento,
                variable=var_checkbox,
                onvalue=True,
                offvalue=False,
            )
            checkbox.pack(anchor="w", pady=3, padx=10)

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

        # 4. Procesar cada evento a eliminar (orden inverso)
        recursos_devueltos = []
        eventos_a_eliminar_indices.sort(reverse=True)

        for indice in eventos_a_eliminar_indices:
            if indice >= len(self.eventos_planificados):
                continue

            evento = self.eventos_planificados[indice]

        # 5. Devolver recursos (SOLO equipos, NO combustible)
        recursos_devueltos = []

        for recurso_detalle in evento.get("recursos_detalle", []):
            # Solo procesar recursos NO combustibles
            if not recurso_detalle.get("es_combustible", False):
                # Verificar si está en recursos_consumidos (para consistencia)
                encontrado = False
                for consumido in evento.get("recursos_consumidos", []):
                    if consumido["recurso"] == recurso_detalle["nombre_mostrar"]:
                        encontrado = True
                        break

                if encontrado:
                    print(f"🔄 Equipo liberado: {recurso_detalle['nombre_mostrar']}")
                    recursos_devueltos.append(
                        {
                            "nombre": recurso_detalle["nombre_mostrar"],
                            "categoria": recurso_detalle["categoria"],
                            "tipo": "equipo",
                        }
                    )
                else:
                    print(
                        f"⚠️ Equipo no encontrado en recursos_consumidos: {recurso_detalle['nombre_mostrar']}"
                    )

        # COMBUSTIBLE: No se hace nada - no se devuelve
        for recurso_detalle in evento.get("recursos_detalle", []):
            if recurso_detalle.get("es_combustible", False):
                print(
                    f"🔥 Combustible NO devuelto (consumido): {recurso_detalle['nombre_mostrar']}"
                )

        # 6. Eliminar el evento
        del self.eventos_planificados[indice]

        # 7. Guardar cambios
        self.guardar_recursos()
        self.guardar_eventos_en_json()

        # 8. Actualizar interfaz
        self.actualizar_contador()
        self.crear_checkboxes_recursos()

        # 9. Cerrar ventana
        ventana_eliminar.destroy()

        # 10. Mostrar mensaje de éxito
        mensaje = f"✅ Se eliminaron {len(eventos_a_eliminar_indices)} evento(s)."

        if recursos_devueltos:
            mensaje += f"\n🔄 {len(recursos_devueltos)} equipo(s) liberado(s) para nuevas asignaciones."

            for recurso in recursos_devueltos:
                print(f"🔄 Liberando equipo: {recurso['nombre']}")

    # ************** INTERFAZ *************#
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
            frame_campos_fecha, placeholder_text="Duracion", width=100
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
