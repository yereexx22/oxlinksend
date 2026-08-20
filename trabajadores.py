from configuracion import cargar_trabajadores, guardar_trabajadores

def agregar_trabajador(id_, nombre, email, telefono=''):
    trabajadores = cargar_trabajadores()
    if id_ in trabajadores:
        return False
    trabajadores[id_] = (nombre, email, telefono)
    guardar_trabajadores(trabajadores)
    return True

def eliminar_trabajador(id_):
    trabajadores = cargar_trabajadores()
    if id_ in trabajadores:
        del trabajadores[id_]
        guardar_trabajadores(trabajadores)
        return True
    return False

def editar_trabajador(id_original, nuevo_id, nuevo_nombre, nuevo_email, nuevo_telefono):
    trabajadores = cargar_trabajadores()
    if id_original not in trabajadores:
        return False
    if id_original != nuevo_id and nuevo_id in trabajadores:
        return False
    del trabajadores[id_original]
    trabajadores[nuevo_id] = (nuevo_nombre, nuevo_email, nuevo_telefono)
    guardar_trabajadores(trabajadores)
    return True

def listar_trabajadores():
    trabajadores = cargar_trabajadores()
    lista = [(id_, nombre, email, telefono) for id_, (nombre, email, telefono) in trabajadores.items()]
    return sorted(lista, key=lambda x: x[0])  # Ordenar por ID

def obtener_trabajador_por_id(id_):
    trabajadores = cargar_trabajadores()
    if id_ in trabajadores:
        nombre, email, telefono = trabajadores[id_]
        return (id_, nombre, email, telefono)
    return None

def importar_trabajadores(lista_trabajadores):
    """
    Importa una lista de trabajadores (id, nombre, email, telefono).
    Retorna (agregados, errores) donde errores es una lista de mensajes.
    """
    trabajadores = cargar_trabajadores()
    agregados = 0
    errores = []
    for id_, nombre, email, telefono in lista_trabajadores:
        if id_ in trabajadores:
            errores.append(f"ID {id_} ya existe")
            continue
        trabajadores[id_] = (nombre, email, telefono)
        agregados += 1
    guardar_trabajadores(trabajadores)
    return agregados, errores