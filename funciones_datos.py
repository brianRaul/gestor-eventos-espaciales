import json
from datetime import datetime, date, timedelta

# ========== FUNCIONES DE CARGA ==========

def cargar_eventos_desde_json():
    """Carga los tipos de eventos desde el JSON (sin cambios)"""
    try:
        with open("eventos_predeterminados.json", "r", encoding="utf-8") as f:
            datos = json.load(f)
            return datos
    except FileNotFoundError:
        return {}

def cargar_recursos_desde_json():
    """Carga los recursos desde JSON y calcula disponibilidad en base a eventos planificados"""
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

def cargar_eventos_planificados():
    """Carga eventos planificados"""
    try:
        with open("eventos_planificados.json", "r", encoding="utf-8") as f:
            contenido = json.load(f)
            return contenido if isinstance(contenido, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def cargar_ocupaciones():
    try:
        with open("ocupaciones.json", "r", encoding="utf-8") as f:
            datos = json.load(f)
        
        # Si el archivo tiene la estructura antigua con sección "ocupaciones"
        if "ocupaciones" in datos:
            print("⚠️ Formato antiguo de ocupaciones detectado, convirtiendo...")
            # Convertir a nuevo formato
            nuevo_formato = {}
            for recurso_id, info in datos["ocupaciones"].items():
                if "unidades" in info:
                    for unidad_id, ocupaciones in info["unidades"].items():
                        if ocupaciones:  # Si hay ocupaciones
                            nuevo_formato[unidad_id] = ocupaciones
            return nuevo_formato
        else:
            # Ya está en el nuevo formato
            ocupaciones_limpias = {}
            for key, value in datos.items():
                # Filtrar solo las claves que parecen IDs de recursos (no metadatos)
                if not key.startswith(("ocupaciones", "combustibles")):
                    ocupaciones_limpias[key] = value
            return ocupaciones_limpias
            
    except FileNotFoundError:
        print("⚠️ No se encontró 'ocupaciones.json'. Se creará uno vacío.")
        return {}
    except Exception as e:
        print(f"❌ Error cargando ocupaciones: {e}")
        return {}

def guardar_ocupaciones(ocupaciones):
    """Guarda las ocupaciones de recursos en JSON"""
    try:
        with open("ocupaciones.json", "w", encoding="utf-8") as f:
            json.dump(ocupaciones, f, indent=4, ensure_ascii=False)
        print("✅ Ocupaciones guardadas")
    except Exception as e:
        print(f"❌ Error guardando ocupaciones: {e}")

def guardar_recursos_combustible(recursos):
    """Guarda solo recursos combustibles"""
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
        
def obtener_id_recurso(categoria, modelo, tipo, numero_unidad=1):
    modelo_limpio = modelo.replace("-", "").replace(" ", "").upper()
    tipo_limpio = tipo.upper()
    
    if "COMBUSTIBLE" in categoria.upper():
        return f"COMBUSTIBLE-{tipo_limpio}"
    else:
        return f"{modelo_limpio}-{tipo_limpio}-{str(numero_unidad).zfill(3)}"