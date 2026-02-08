def procesar_eliminacion_eventos(eventos_a_eliminar_indices, eventos_planificados, recursos):
    """
    Procesa la eliminación de eventos y devuelve los recursos que se liberan/recuperan
    
    Retorna:
    - recursos_devueltos: lista de equipos liberados
    - combustible_devuelto: lista de combustible recuperado con detalles
    - nuevos_eventos: lista de eventos después de eliminar
    """
    recursos_devueltos = []
    combustible_devuelto = []
    eventos_a_eliminar_indices = sorted(eventos_a_eliminar_indices, reverse=True)
    
    for indice in eventos_a_eliminar_indices:
        if indice >= len(eventos_planificados):
            continue

        evento = eventos_planificados[indice]

        # TODOS LOS EVENTOS (INDIVIDUALES Y DE SERIE) TIENEN MISMA ESTRUCTURA
        if "recursos_detalle" in evento and evento["recursos_detalle"]:
            for recurso_detalle in evento["recursos_detalle"]:
                # Buscar el recurso en la lista de recursos
                for recurso in recursos:
                    if (
                        recurso["nombre_mostrar"]
                        == recurso_detalle["nombre_mostrar"]
                    ):
                        cantidad = recurso_detalle.get("cantidad", 1)
                        es_combustible = recurso_detalle.get(
                            "es_combustible", False
                        )

                        if es_combustible and cantidad > 0:
                            # COMBUSTIBLE: devolver al tanque calculando desperdicio
                            disponible_actual = recurso["cantidad_disponible"]
                            capacidad_maxima = recurso["cantidad_total"]
                            
                            # Calcular cuánto se puede devolver y cuánto se desperdicia
                            espacio_disponible = capacidad_maxima - disponible_actual
                            litros_devueltos = min(cantidad, espacio_disponible)
                            litros_desperdiciados = cantidad - litros_devueltos
                            
                            if litros_devueltos > 0:
                                recurso["cantidad_disponible"] = disponible_actual + litros_devueltos
                                combustible_devuelto.append(
                                    {
                                        "nombre": recurso["nombre_mostrar"],
                                        "litros": litros_devueltos,
                                        "desperdiciados": litros_desperdiciados,
                                        "nuevo_total": recurso["cantidad_disponible"],
                                    }
                                )
                            elif litros_desperdiciados > 0:
                                # Si no se puede devolver nada (tanque lleno) pero había combustible
                                combustible_devuelto.append(
                                    {
                                        "nombre": recurso["nombre_mostrar"],
                                        "litros": 0,
                                        "desperdiciados": litros_desperdiciados,
                                        "nuevo_total": disponible_actual,
                                    }
                                )
                        else:
                            # EQUIPOS: registrar que se liberó
                            encontrado = False
                            for r in recursos_devueltos:
                                if r["nombre"] == recurso["nombre_mostrar"]:
                                    encontrado = True
                                    break

                            if not encontrado:
                                recursos_devueltos.append(
                                    {
                                        "nombre": recurso["nombre_mostrar"],
                                        "categoria": recurso["categoria"],
                                    }
                                )
                        break

        # Eliminar el evento
        del eventos_planificados[indice]

    return recursos_devueltos, combustible_devuelto, eventos_planificados

def generar_mensaje_resumen(eventos_eliminados, recursos_devueltos, combustible_devuelto):
    """
    Genera un mensaje resumen de la eliminación
    """
    mensaje = f"✅ Se eliminaron {len(eventos_eliminados)} evento(s)."

    # Resumen de equipos liberados
    if recursos_devueltos:
        equipos_unicos = len(set(item["nombre"] for item in recursos_devueltos))
        mensaje += f"\n🔄 {equipos_unicos} equipo(s) liberado(s)."

    # Resumen de combustible devuelto
    if combustible_devuelto:
        total_litros = sum(item["litros"] for item in combustible_devuelto)
        total_desperdiciado = sum(item.get("desperdiciados", 0) for item in combustible_devuelto)
        
        if len(combustible_devuelto) == 1:
            item = combustible_devuelto[0]
            mensaje += f"\n⛽ +{item['litros']}L devueltos a {item['nombre']}"
            if item.get("desperdiciados", 0) > 0:
                mensaje += f" (💥 {item['desperdiciados']}L desperdiciados)"
        else:
            mensaje += f"\n⛽ +{total_litros}L de combustible devueltos"
            if total_desperdiciado > 0:
                mensaje += f" (💥 {total_desperdiciado}L desperdiciados)"

    return mensaje