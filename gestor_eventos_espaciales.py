import customtkinter as ctk
import json


class GestorEventosSimple(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Configurar ventana
        self.title("Gestor de Eventos Espaciales")
        self.geometry("600x700")

        self.evento_seleccionado = None  # Para guardar el evento actual seleccionado

        self.tipos_evento_data = self.cargar_eventos_desde_json()

        # Extraer solo los nombres para el ComboBox
        self.tipos_evento = [evento["nombre"] for evento in self.tipos_evento_data]
        self.recursos = self.cargar_recursos_desde_json()

        # Cargar eventos planificados
        self.cargar_eventos_planificados()

        # Crear la interfaz
        self.crear_interfaz()

    def cargar_eventos_desde_json(self):
        """Cargar tipos de evento desde archivo JSON con recursos predeterminados"""
        try:
            with open("eventos_predeterminados.json", "r", encoding="utf-8") as f:
                datos = json.load(f)
                return datos.get(
                    "tipos_evento",
                    [
                        {"nombre": "Despegue", "recursos": ["COHETE", "PLATAFORMA"]},
                        {"nombre": "Prueba", "recursos": ["LABORATORIO", "EQUIPO"]},
                    ],
                )
        except FileNotFoundError:
            return [
                {"nombre": "Despegue", "recursos": ["COHETE", "PLATAFORMA"]},
                {"nombre": "Prueba", "recursos": ["LABORATORIO", "EQUIPO"]},
                {"nombre": "Ensayo", "recursos": ["SISTEMA", "CONTROL"]},
            ]

    def cargar_recursos_desde_json(self):
        """Cargar recursos desde archivo JSON"""
        try:
            with open("recursos.json", "r", encoding="utf-8") as f:
                datos = json.load(f)
                return datos.get("recursos", ["Recurso 1", "Recurso 2"])
        except FileNotFoundError:
            return ["COHETE", "PLATAFORMA"]

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

    def mostrar_recursos_evento(self, evento_seleccionado):

        if evento_seleccionado and evento_seleccionado != "Elige un tipo de evento":
            for evento_data in self.tipos_evento_data:
                if evento_data["nombre"] == evento_seleccionado:
                    recursos = evento_data.get("recursos", [])
                    recursos_texto = ", ".join(recursos)
                    self.lbl_recursos.configure(
                        text=f"Recursos predeterminados: {recursos_texto}"
                    )
                    break
        else:
            self.lbl_recursos.configure(text="Recursos predeterminados: ---")

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

        # Validar formato de fecha (solo básico)
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
            "recursos": recursos,
        }

        # Agregar a la lista
        self.eventos_creados.append(nuevo_evento)
        # Guardar en archivo JSON
        self.guardar_eventos_en_json()

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

        # Mostrar en consola (para depuración)
        print(f"Evento creado: {nuevo_evento}")
        print(f"Total eventos: {len(self.eventos_creados)}")

    def crear_interfaz(self):
        """Crear todos los elementos visuales"""

        # ========== 1. TÍTULO ==========
        lbl_titulo = ctk.CTkLabel(
            self, text="GESTOR DE EVENTOS ESPACIALES", font=("Arial", 20, "bold")
        )
        lbl_titulo.pack(pady=20)

        # ========== 2. SELECCIÓN DE EVENTO ==========
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
            command=self.mostrar_recursos_evento
        )
        self.combo_evento.pack(pady=5)
        self.combo_evento.set("Elige un tipo de evento")

        # ========== 3. RECURSOS PREDETERMINADOS ==========
        frame_recursos = ctk.CTkFrame(self)
        frame_recursos.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            frame_recursos, text="Recursos predeterminados:", font=("Arial", 14)
        ).pack(pady=5)

        # Label para mostrar los recursos del evento seleccionado
        self.lbl_recursos = ctk.CTkLabel(
            frame_recursos,
            text="Recursos predeterminados: ---",
            font=("Arial", 12),
            text_color="gray",
            wraplength=500,
            
        )
        self.lbl_recursos.pack(pady=5)

        # ========== 4. FECHA DEL EVENTO ==========
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

        # ========== 5. BOTONES DE ACCIÓN ==========
        frame_botones = ctk.CTkFrame(self)
        frame_botones.pack(pady=20, padx=20)

        # Botón para ver eventos planificados
        self.btn_ver = ctk.CTkButton(
            frame_botones, text="📋 Ver Eventos Planificados", width=180
        )
        self.btn_ver.pack(side="left", padx=10)

        # Botón para eliminar eventos
        self.btn_eliminar = ctk.CTkButton(
            frame_botones,
            text="🗑️ Eliminar Eventos",
            fg_color="#FF5252",
            hover_color="#D32F2F",
            width=180,
        )
        self.btn_eliminar.pack(side="left", padx=10)

        # ========== 6. BOTÓN PRINCIPAL ==========
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

        # ========== 7. ÁREA DE INFORMACIÓN ==========
        self.lbl_info = ctk.CTkLabel(
            self,
            text="Selecciona un tipo de evento para ver sus recursos predeterminados",
            font=("Arial", 12),
            text_color="gray",
        )
        self.lbl_info.pack(pady=10)

        # ========== 8. CONTADOR DE EVENTOS ==========
        frame_contador = ctk.CTkFrame(self)
        frame_contador.pack(pady=10, padx=20, fill="x")

        self.lbl_contador = ctk.CTkLabel(
            frame_contador, text="Eventos planificados: 0", font=("Arial", 12)
        )
        self.lbl_contador.pack(pady=5)
        self.actualizar_contador()


# Ejecutar la aplicación
if __name__ == "__main__":
    app = GestorEventosSimple()
    app.mainloop()
