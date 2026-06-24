import json
from datetime import datetime, date, timedelta

# ========== FUNCIONES DE CARGA ==========
# Carga los tipos de eventos desde el JSON 
def cargar_eventos_desde_json():
    try:
        with open("eventos_predeterminados.json", "r", encoding="utf-8") as f:
            datos = json.load(f)
            return datos
    except FileNotFoundError:
        return {}

def cargar_recursos_desde_json():
    try:
        with open("recursos.json", "r", encoding="utf-8") as f:
            datos = json.load(f)

        categorias_recursos = datos.get("recursos", {})
        lista_recursos = []

        for categoria, lista_modelos in categorias_recursos.items():
            for recurso_info in lista_modelos:
                modelo = recurso_info.get("modelo", "")
                tipo = recurso_info.get("tipo", "")
                
                # Obtener cantidad_total y cantidad_disponible
                cantidad_total = recurso_info.get("cantidad_total", 0)
                cantidad_disponible = recurso_info.get("cantidad_disponible", cantidad_total)
                
                # Determinar si es combustible
                es_combustible = "COMBUSTIBLE" in categoria.upper()
                
                # Crear nombre para mostrar
                if es_combustible:
                    nombre_mostrar = f"{modelo} ({tipo})"
                    unidad = "L"
                else:
                    nombre_mostrar = f"{modelo} ({tipo})"
                    unidad = "uds"

                lista_recursos.append({
                    "id": f"{modelo}-{tipo}",
                    "nombre_mostrar": nombre_mostrar,
                    "categoria": categoria,
                    "modelo": modelo,
                    "tipo": tipo,
                    "cantidad_total": cantidad_total,
                    "cantidad_disponible": cantidad_disponible,  # Usa el valor del archivo
                    "unidad": unidad,
                    "es_combustible": es_combustible,
                    "es_consumible": es_combustible
                })

        print(f"✅ Se cargaron {len(lista_recursos)} recursos.")
        return lista_recursos

    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'recursos.json'")
        return []
    except Exception as e:
        print(f"❌ Error cargando recursos: {e}")
        return []

# Carga eventos planificados
def cargar_eventos_planificados():
    try:
        with open("eventos_planificados.json", "r", encoding="utf-8") as f:
            eventos = json.load(f)
        # Convertir fechas a objetos date y agregar resumen de recursos
        for ev in eventos:
            ev["fecha_inicio_date"] = datetime.strptime(ev["fecha_inicio"], "%d/%m/%Y").date()
            ev["fecha_fin_date"] = datetime.strptime(ev["fecha_fin"], "%d/%m/%Y").date()
            # Agregar resumen de recursos si no existe (para eventos antiguos)
            if "resumen_recursos" not in ev and "recursos_detalle" in ev:
                resumen = {}
                for rd in ev["recursos_detalle"]:
                    clave = f"{rd['categoria']}|{rd['tipo']}"
                    resumen[clave] = resumen.get(clave, 0) + rd["cantidad"]
                ev["resumen_recursos"] = resumen
        return eventos if isinstance(eventos, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    