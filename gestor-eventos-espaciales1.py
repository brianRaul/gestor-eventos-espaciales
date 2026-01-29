import customtkinter as ctk
import json
from datetime import datetime, date, timedelta


class GestorEventosSimple(ctk.CTk):

    def __init__(self):
        super().__init__()

        # 1.Configurar ventana
        self.title("Gestor de Eventos Espaciales")
        self.geometry("600x900")

        self.evento_seleccionado = None

        # 2. CARGA DE EVENTOS
        self.tipos_evento_data = self.cargar_eventos_desde_json()

        # Extraemos las llaves (nombres de eventos) para el ComboBox
        self.tipos_evento = list(self.tipos_evento_data.keys())

        # Cargamos los recursos
        self.recursos = self.cargar_recursos_desde_json()
        print(f"DEBUG: Tipo de self.recursos = {type(self.recursos)}")
        print(
            f"DEBUG: Contenido de self.recursos (primeros 3 elementos) = {self.recursos[:3] if isinstance(self.recursos, list) else self.recursos}"
        )

        # 3. CARGA DE ARCHIVOS DE AGENDA
        # Importante: Aseguramos que sea una lista para evitar el error 'NoneType'
        self.eventos_planificados = self.cargar_eventos_planificados()
        if self.eventos_planificados is None:
            self.eventos_planificados = []

        # 4. CREACIÓN DE LA INTERFAZ
        self.crear_interfaz()

    # ****************** GUARDAR/CARGAR RECURSOS ********************#
    def cargar_eventos_desde_json(self):
        try:
            with open("eventos_predeterminados.json", "r", encoding="utf-8") as f:
                datos = json.load(f)
                return datos
        except FileNotFoundError:

            return {
                "Despegue de cohete": {
                    "recursos_recomendados": [
                        "COHETE",
                        "PLATAFORMA DE LANZAMIENTO",
                        "SISTEMA DE COMBUSTIBLE",
                        "SISTEMA DE SEGURIDAD",
                    ],
                    "recursos_prohibidos": [],
                    "duracion_minima": 1,
                    "duracion_maxima": 3,
                },
                "Pruebas de carga útil": {
                    "recursos_recomendados": [
                        "LABORATORIO DE PRUEBAS",
                        "EQUIPO DE CONTROL",
                        "SISTEMA ELÉCTRICO",
                    ],
                    "recursos_prohibidos": [],
                    "duracion_minima": 2,
                    "duracion_maxima": 5,
                },
            }

    def cargar_recursos_desde_json(self):
        try:
            # Abrir y leer el archivo JSON
            with open("recursos.json", "r", encoding="utf-8") as f:
                datos = json.load(f)

            # El archivo tiene esta estructura: {"recursos": {...}}
            recursos_dict = datos["recursos"]

            # Convertir la estructura anidada en una lista plana
            lista_recursos = []

            # Recorrer cada categoría de recurso
            for categoria, subcategorias in recursos_dict.items():
                # Recorrer cada subcategoría dentro de la categoría
                for subcategoria, cantidad in subcategorias.items():
                    # Determinar la unidad de medida
                    if "COMBUSTIBLE" in categoria.upper():
                        unidad = "L"  # Litros para combustible
                    else:
                        unidad = "uds"  # Unidades para el resto

                    # Crear el nombre completo del recurso
                    nombre_completo = f"{categoria} ({subcategoria})"

                    # Añadir el recurso a la lista
                    lista_recursos.append(
                        {
                            "nombre": nombre_completo,
                            "cantidad_total": cantidad,
                            "unidad": unidad,
                            "categoria": categoria,
                        }
                    )

            print(f"✅ Se cargaron {len(lista_recursos)} recursos")
            return lista_recursos

        except FileNotFoundError:
            # Si el archivo no existe, mostrar error y devolver lista vacía
            print("❌ Error: No se encontró el archivo 'recursos.json'")
            return []
        except Exception as e:
            # Cualquier otro error
            print(f"❌ Error cargando recursos: {e}")
            return []

    def cargar_eventos_planificados(self):
        try:
            with open("eventos_planificados.json", "r", encoding="utf-8") as f:
                contenido = json.load(f)
                return contenido if isinstance(contenido, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []

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

        except Exception as e:
            print(f"❌ Error al guardar en JSON: {e}")

    def actualizar_contador(self):
        total = len(self.eventos_planificados)
        self.lbl_contador.configure(text=f"Eventos planificados: {total}")

    def guardar_recursos(self):
        try:
            with open("recursos.json", "w", encoding="utf-8") as f:
                json.dump({"recursos": self.recursos}, f, ensure_ascii=False, indent=1)
        except Exception as e:
            print(f"Error al actualizar la cantidad de recursos: {e}")

    # *********** LOGICA *************#
    # ========== Crear checkboxes de recursos ==========
    def crear_checkboxes_recursos(self):

        # 1. Limpiar checkboxes anteriores si existen
        for widget in self.frame_checkboxes.winfo_children():
            widget.destroy()

        # 2. Diccionario para guardar las variables de los checkboxes
        self.checkbox_vars = {}

        # 3. Verificar que hay recursos cargados
        if not self.recursos:
            print("⚠️ No hay recursos disponibles para mostrar")

            # Mostrar mensaje en lugar de checkboxes
            mensaje = ctk.CTkLabel(
                self.frame_checkboxes,
                text="No hay recursos disponibles. Verifica el archivo recursos.json",
                text_color="orange",
            )
            mensaje.pack(pady=20)
            return

        # 4. Crear un checkbox por cada recurso
        for recurso in self.recursos:
            # Crear variable para el checkbox (inicia desmarcado)
            var = ctk.BooleanVar(value=False)

            # Guardar la variable usando el nombre del recurso como clave
            nombre_recurso = recurso["nombre"]
            self.checkbox_vars[nombre_recurso] = var

            # Crear el texto del checkbox
            cantidad = recurso["cantidad_total"]
            unidad = recurso["unidad"]
            texto_checkbox = f"{nombre_recurso} ({cantidad} {unidad} disponibles)"

            # Crear el checkbox
            checkbox = ctk.CTkCheckBox(
                self.frame_checkboxes,
                text=texto_checkbox,
                variable=var,
                onvalue=True,
                offvalue=False,
            )

            # Colocar el checkbox en la interfaz
            checkbox.pack(anchor="w", pady=2, padx=5)

        print(f"✅ Se crearon {len(self.checkbox_vars)} checkboxes de recursos")

    # ========== Botón para marcar recursos recomendados ==========
    def marcar_recursos_recomendados(self):
        tipo_evento = self.combo_evento.get()

        if tipo_evento not in self.tipos_evento_data:
            self.lbl_info.configure(
                text="❌ Selecciona un evento válido", text_color="red"
            )
            return

        evento_data = self.tipos_evento_data[tipo_evento]

        # 1. Obtener los datos del nuevo JSON
        # Ahora usamos .keys() porque 'recursos_necesarios' es un diccionario {nombre: cantidad}
        necesarios = evento_data.get("recursos_necesarios", {}).keys()
        prohibidos = evento_data.get("recursos_prohibidos", [])

        contador_marcados = 0

        # 2. Resetear y marcar
        for nombre_recurso, var in self.checkbox_vars.items():
            # Desmarcamos primero para limpiar selecciones anteriores
            var.set(False)

            # Si el recurso es necesario para este evento, lo marcamos
            if nombre_recurso in necesarios:
                var.set(True)
                contador_marcados += 1

            # Opcional: Podrías deshabilitar los prohibidos aquí si quisieras
            # if nombre_recurso in prohibidos:
            #    self.checkbox_widgets[nombre_recurso].configure(state="disabled")

        self.lbl_info.configure(
            text=f"✅ Configurado: {contador_marcados} recursos necesarios marcados",
            text_color="green",
        )

    # ========== Crear evento ==========
    def crear_evento(self):
        # Obtención y validación de los datos
        tipo_evento = self.combo_evento.get()
        evento_data = self.tipos_evento_data.get(tipo_evento, {})
        recursos_obligatorios = evento_data.get("recursos_necesarios", {})
        day, month, year = (
            self.entry_day.get(),
            self.entry_month.get(),
            self.entry_year.get(),
        )
        duracion_str = self.entry_duracion.get()

        if not tipo_evento or tipo_evento == "Elige un tipo de evento":
            self.lbl_info.configure(
                text="❌ Selecciona un tipo de evento", text_color="red"
            )
            return

        # Validar fechas
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

        # Validar duración min/max 
        if tipo_evento in self.tipos_evento_data:
            evento_data = self.tipos_evento_data[tipo_evento]
            d_min = evento_data.get("duracion_minima", 1)
            d_max = evento_data.get("duracion_maxima", 30)
            if not (d_min <= duracion <= d_max):
                self.lbl_info.configure(
                    text=f"❌ Duración permitida: {d_min}-{d_max} días",
                    text_color="red",
                )
                return

        # Obtener recursos seleccionados (checkboxes)
        recursos_seleccionados = [k for k, v in self.checkbox_vars.items() if v.get()]
        if not recursos_seleccionados:
            self.lbl_info.configure(
                text="❌ Selecciona al menos un recurso", text_color="red"
            )
            return

        # A. Verificar Recursos Prohibidos (Exclusión Mutua)
        prohibidos = evento_data.get("recursos_prohibidos", [])
        for rec in recursos_seleccionados:
            if rec in prohibidos:
                self.lbl_info.configure(
                    text=f"⛔ REGLA VIOLADA: '{rec}' está prohibido en este evento.",
                    text_color="red",
                )
                return
        # B Validar Co-requisitos
        corequisitos = evento_data.get("recursos_corequisitos", {})

        if corequisitos:  # Solo validar si hay co-requisitos definidos
            errores_corequisitos = []

            # Para cada recurso principal y sus recursos requeridos
            for recurso_principal, recursos_requeridos in corequisitos.items():
                # Si el usuario seleccionó el recurso principal...
                if recurso_principal in recursos_seleccionados:
                    # ...debe tener TODOS los recursos requeridos
                    for requerido in recursos_requeridos:
                        if requerido not in recursos_seleccionados:
                            errores_corequisitos.append(
                                f"❌ '{recurso_principal}' requiere también '{requerido}'"
                            )

            # Si hay errores, mostrarlos y detener
            if errores_corequisitos:
                # Mostrar máximo 3 errores para no saturar la pantalla
                if len(errores_corequisitos) > 3:
                    errores_a_mostrar = errores_corequisitos[:3]
                    errores_a_mostrar.append(
                        f"... y {len(errores_corequisitos) - 3} error(es) más"
                    )
                else:
                    errores_a_mostrar = errores_corequisitos

                    self.lbl_info.configure(
                        text="\n".join(errores_a_mostrar), text_color="red"
                    )
                return  # Detener la creación del evento

        # C. Verificar SI FALTA ALGUNO
        for obligatorio in recursos_obligatorios.keys():
            encontrado = False

            # Revisamos los que el usuario marcó en los cuadritos
            for marcado in recursos_seleccionados:
                # Si el obligatorio está dentro del nombre marcado (sin importar mayúsculas)
                if obligatorio.upper() in marcado.upper():
                    encontrado = True
                    break  # Si ya lo encontramos, dejamos de buscar este

            # Si terminamos de revisar y NO lo encontramos...
            if encontrado == False:
                self.lbl_info.configure(
                    text=f"❌ ¡Oye! Te falta marcar: {obligatorio}", text_color="red"
                )
                return  # Detenemos todo porque falta algo

        # CÁLCULO DE DISPONIBILIDAD TEMPORAL 
        necesarios_config = evento_data.get("recursos_necesarios", {})
        uso_recursos_evento = {}

        for rec_nombre in recursos_seleccionados:
            # Calcular cantidad requerida
            cantidad_requerida = 1
            for recurso_necesario, cantidad in necesarios_config.items():
                if recurso_necesario.upper() in rec_nombre.upper():
                    cantidad_requerida = cantidad
                    break

            # Buscar recurso en inventario
            recurso_info = None
            for r in self.recursos:
                if rec_nombre.upper() in r["nombre"].upper():
                    recurso_info = r
                    break

            if recurso_info:
                # Calcular uso en esas fechas
                cantidad_usada = 0
                for ev in self.eventos_planificados:
                    e_ini = datetime.strptime(ev["fecha_inicio"], "%d/%m/%Y")
                    e_fin = datetime.strptime(ev["fecha_fin"], "%d/%m/%Y")

                    if fecha_inicio <= e_fin and fecha_fin >= e_ini:
                        for nombre_usado, cant in ev.get("recursos_usados", {}).items():
                            if rec_nombre.upper() in nombre_usado.upper():
                                cantidad_usada += cant
                                break

                # Verificar disponibilidad
                disponible = recurso_info["cantidad_total"] - cantidad_usada

                if disponible < cantidad_requerida:
                    self.lbl_info.configure(
                        text=f"❌ No hay suficiente {recurso_info['nombre']}",
                        text_color="red",
                    )
                    return

        # GUARDADO
        nuevo_evento = {
            "tipo": tipo_evento,
            "fecha_inicio": fecha_inicio.strftime("%d/%m/%Y"),
            "fecha_fin": fecha_fin.strftime("%d/%m/%Y"),
            "duracion_dias": duracion,
            "recursos": recursos_seleccionados,  # Lista de nombres (para mostrar en GUI)
            "recursos_usados": uso_recursos_evento,  # Diccionario con cantidades (para lógica interna)
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

    # ========== Limpiar selección ==========
    def limpiar_seleccion_recursos(self):
        """Desmarcar todos los checkboxes de recursos"""
        if hasattr(self, "checkbox_vars"):
            for var in self.checkbox_vars.values():
                var.set(False)
            self.lbl_info.configure(
                text="Todos los recursos desmarcados", text_color="orange"
            )

    # =========== Mostrar eventos planificados ========
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

    # ============ Sugerir Fecha =============
    def sugerir_fecha_disponible(self):

        # Validaciones iniciales
        if self.combo_evento.get() == "Elige un tipo de evento":
            self.lbl_info.configure(
                text="❌ Primero selecciona un evento", text_color="red"
            )
            return

        tipo_evento = self.combo_evento.get()

        if tipo_evento not in self.tipos_evento_data:
            self.lbl_info.configure(
                text="❌ Tipo de evento no encontrado", text_color="red"
            )
            return

        # Obtener datos
        evento_data = self.tipos_evento_data[tipo_evento]
        recursos_necesarios = evento_data.get("recursos_necesarios", {})

        if not recursos_necesarios:
            self.lbl_info.configure(
                text="⚠️ Este evento no tiene recursos necesarios definidos",
                text_color="orange",
            )
            return

        # Obtener duración
        try:
            duracion = max(1, int(self.entry_duracion.get()))
        except:
            duracion = 1

        # Validar duración
        d_min = evento_data.get("duracion_minima", 1)
        d_max = evento_data.get("duracion_maxima", 30)
        duracion = max(d_min, min(duracion, d_max))

        # Preprocesar recursos necesarios
        recursos_a_verificar = []
        for recurso_nombre, cantidad in recursos_necesarios.items():
            recurso_info = None
            for r in self.recursos:
                if recurso_nombre.upper() in r["nombre"].upper():
                    recurso_info = r
                    break

            if not recurso_info:
                self.lbl_info.configure(
                    text=f"❌ Recurso '{recurso_nombre}' no encontrado",
                    text_color="red",
                )
                return

            recursos_a_verificar.append(
                {
                    "nombre": recurso_info["nombre"],
                    "total": recurso_info["cantidad_total"],
                    "necesario": cantidad,
                    "unidad": recurso_info["unidad"],
                    "buscar": recurso_nombre,
                }
            )

        # Función para verificar disponibilidad en un período específico
        def verificar_disponibilidad(fecha_inicio, fecha_fin):
            for recurso in recursos_a_verificar:
                disponible = recurso["total"]

                # Buscar eventos que se solapen (optimizado)
                for ev in self.eventos_planificados:
                    # Convertir fechas
                    ev_inicio = datetime.strptime(ev["fecha_inicio"], "%d/%m/%Y").date()
                    ev_fin = datetime.strptime(ev["fecha_fin"], "%d/%m/%Y").date()

                    # Si el evento está después del período, dejar de buscar
                    if ev_inicio > fecha_fin:
                        break

                    # Si hay solapamiento
                    if fecha_inicio <= ev_fin and fecha_fin >= ev_inicio:
                        # Buscar uso del recurso (coincidencia parcial)
                        for nombre_usado, cantidad in ev.get(
                            "recursos_usados", {}
                        ).items():
                            # Búsqueda más flexible
                            if (
                                recurso["buscar"].upper() in nombre_usado.upper()
                                or nombre_usado.upper() in recurso["buscar"].upper()
                            ):
                                disponible -= cantidad
                                break

                    # Si ya no hay suficiente, terminar
                    if disponible < recurso["necesario"]:
                        return False, recurso

            return True, None

        # Algoritmo principal de búsqueda
        hoy = datetime.now().date()

        # Si no hay eventos, probar desde mañana
        if not self.eventos_planificados:
            fecha_prueba = hoy + timedelta(days=1)
            fecha_fin_prueba = fecha_prueba + timedelta(days=duracion - 1)

            disponible, recurso_problema = verificar_disponibilidad(
                fecha_prueba, fecha_fin_prueba
            )
            if disponible:
                self.actualizar_fecha_campos(fecha_prueba)
                return

        # Buscar huecos entre eventos
        eventos_ordenados = self.eventos_planificados

        # Hueco antes del primer evento
        primer_evento_inicio = datetime.strptime(
            eventos_ordenados[0]["fecha_inicio"], "%d/%m/%Y"
        ).date()
        fecha_inicio_hueco = hoy + timedelta(days=1)

        if fecha_inicio_hueco + timedelta(days=duracion - 1) < primer_evento_inicio:
            disponible, _ = verificar_disponibilidad(
                fecha_inicio_hueco, fecha_inicio_hueco + timedelta(days=duracion - 1)
            )
            if disponible:
                self.actualizar_fecha_campos(fecha_inicio_hueco)
                return

        # Huecos entre eventos
        for i in range(len(eventos_ordenados) - 1):
            evento_actual_fin = datetime.strptime(
                eventos_ordenados[i]["fecha_fin"], "%d/%m/%Y"
            ).date()
            eventoSiguiente_inicio = datetime.strptime(
                eventos_ordenados[i + 1]["fecha_inicio"], "%d/%m/%Y"
            ).date()

            # Si hay al menos 'duracion' días entre eventos
            if evento_actual_fin + timedelta(days=duracion) < eventoSiguiente_inicio:
                fecha_candidata = evento_actual_fin + timedelta(days=1)
                fecha_fin_candidata = fecha_candidata + timedelta(days=duracion - 1)

                disponible, _ = verificar_disponibilidad(
                    fecha_candidata, fecha_fin_candidata
                )
                if disponible:
                    self.actualizar_fecha_campos(fecha_candidata)
                    return

        # Hueco después del último evento
        ultimo_evento_fin = datetime.strptime(
            eventos_ordenados[-1]["fecha_fin"], "%d/%m/%Y"
        ).date()
        fecha_candidata = ultimo_evento_fin + timedelta(days=1)

        # Probar los próximos 30 días después del último evento
        for i in range(30):
            fecha_prueba = fecha_candidata + timedelta(days=i)
            fecha_fin_prueba = fecha_prueba + timedelta(days=duracion - 1)

            disponible, recurso_problema = verificar_disponibilidad(
                fecha_prueba, fecha_fin_prueba
            )
            if disponible:
                self.actualizar_fecha_campos(fecha_prueba)
                return

        # No se encontró fecha
        self.lbl_info.configure(
            text="❌ No se encontraron fechas disponibles", text_color="red"
        )

    def actualizar_fecha_campos(self, fecha):

        self.entry_day.delete(0, "end")
        self.entry_day.insert(0, fecha.day)
        self.entry_month.delete(0, "end")
        self.entry_month.insert(0, fecha.month)
        self.entry_year.delete(0, "end")
        self.entry_year.insert(0, fecha.year)

        self.lbl_info.configure(
            text=f"✅ Fecha sugerida: {fecha.strftime('%d/%m/%Y')}", text_color="green"
        )

    def eliminar_eventos_planificados(self):
        # PASO 1: Verificar si hay eventos para eliminar
        if len(self.eventos_planificados) == 0:
            self.lbl_info.configure(
                text="❌ No hay eventos para eliminar", text_color="red"
            )
            return

        # PASO 2: Crear una nueva ventana emergente
        ventana_eliminar = ctk.CTkToplevel(self)
        ventana_eliminar.title("🗑️ Eliminar Eventos")
        ventana_eliminar.geometry("600x500")

        # PASO 3: Título de la ventana
        titulo = ctk.CTkLabel(
            ventana_eliminar,
            text="SELECCIONA EVENTOS A ELIMINAR",
            font=("Arial", 18, "bold"),
        )
        titulo.pack(pady=10)

        # PASO 4: Instrucciones
        instrucciones = ctk.CTkLabel(
            ventana_eliminar,
            text="Marca los eventos que quieres eliminar:",
            font=("Arial", 14),
        )
        instrucciones.pack(pady=5)

        # PASO 5: Crear un área con scroll para los eventos
        frame_scroll = ctk.CTkScrollableFrame(ventana_eliminar, width=550, height=300)
        frame_scroll.pack(pady=10, padx=10)

        # PASO 6: Lista para guardar los checkboxes
        self.checkboxes_eliminar = []  # Esta lista guardará todos los checkboxes

        # PASO 7: Crear un checkbox por cada evento
        for i, evento in enumerate(self.eventos_planificados):
            # Crear una variable para el checkbox
            var_checkbox = ctk.BooleanVar(value=False)
            self.checkboxes_eliminar.append(var_checkbox)  # Guardar en lista

            # Crear el texto para mostrar
            # CAMBIO IMPORTANTE: Usamos 'fecha_inicio' en lugar de 'fecha'
            texto_evento = f"Evento #{i+1}: {evento['tipo']} - {evento['fecha_inicio']}"

            # Crear el checkbox
            checkbox = ctk.CTkCheckBox(
                frame_scroll,
                text=texto_evento,
                variable=var_checkbox,
                onvalue=True,
                offvalue=False,
            )
            checkbox.pack(anchor="w", pady=3, padx=10)

        # PASO 8: Frame para los botones
        frame_botones = ctk.CTkFrame(ventana_eliminar)
        frame_botones.pack(pady=15)

        # PASO 9: Botón para eliminar
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

        # PASO 10: Botón para cancelar
        btn_cancelar = ctk.CTkButton(
            frame_botones,
            text="CANCELAR",
            width=100,
            height=40,
            command=ventana_eliminar.destroy,
        )
        btn_cancelar.pack(side="left", padx=10)

    def confirmar_eliminacion(self, ventana_eliminar):
        # Importar messagebox para mostrar mensajes
        import tkinter.messagebox as messagebox

        # PASO 1: Contar cuántos eventos están marcados
        eventos_a_eliminar = []

        for i, checkbox_var in enumerate(self.checkboxes_eliminar):
            if checkbox_var.get() == True:  # Si el checkbox está marcado
                eventos_a_eliminar.append(i)  # Guardar el índice

        # PASO 2: Verificar si se seleccionó algo
        if len(eventos_a_eliminar) == 0:
            messagebox.showwarning(
                "Sin selección", "No has seleccionado ningún evento para eliminar."
            )
            return

        # PASO 3: Preguntar confirmación al usuario
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar {len(eventos_a_eliminar)} evento(s)?",
        )

        if not respuesta:  # Si el usuario dice "No"
            return

        # PASO 4: Eliminar los eventos (empezando del último al primero)
        eventos_eliminados = 0

        # Ordenar de mayor a menor para no afectar índices
        eventos_a_eliminar.sort(reverse=True)

        for indice in eventos_a_eliminar:
            # Verificar que el índice sea válido
            if indice < len(self.eventos_planificados):
                # Obtener información del evento antes de eliminarlo
                evento_info = self.eventos_planificados[indice]
                print(
                    f"✅ Eliminando: {evento_info['tipo']} del {evento_info['fecha_inicio']}"
                )

                # Eliminar de la lista
                del self.eventos_planificados[indice]
                eventos_eliminados += 1

        # PASO 5: Guardar los cambios en el archivo
        self.guardar_eventos_en_json()

        # PASO 6: Actualizar el contador en pantalla
        self.actualizar_contador()

        # PASO 7: Cerrar la ventana de eliminación
        ventana_eliminar.destroy()

        # PASO 8: Mostrar mensaje de éxito
        self.lbl_info.configure(
            text=f"✅ Se eliminaron {eventos_eliminados} evento(s)", text_color="green"
        )

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
        self.btn_sugerir.pack(pady=5)

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
