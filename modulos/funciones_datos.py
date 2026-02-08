import json
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
            contenido = json.load(f)
            return contenido if isinstance(contenido, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
# Guarda solo recursos combustibles
def guardar_recursos_combustible(recursos):
    try:
        # Filtrar solo combustibles
        recursos_combustible = [
            r for r in recursos 
            if r.get("es_combustible", False)
        ]
        
        with open("combustible.json", "w", encoding="utf-8") as f:
            json.dump(recursos_combustible, f, indent=4, ensure_ascii=False)
        print(f"✅ Combustible guardado: {len(recursos_combustible)} recursos")
    except Exception as e:
        print(f"❌ Error guardando combustible: {e}")
        