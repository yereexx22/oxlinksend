import base64
from datetime import datetime
from pathlib import Path
from supabase_cliente import supabase

# ------------------------------------------------------------
# Trabajadores
# ------------------------------------------------------------
def cargar_trabajadores():
    trabajadores = {}
    try:
        resp = supabase.table('trabajadores').select('*').execute()
        for fila in resp.data:
            id_ = int(fila['id'])
            trabajadores[id_] = (fila['nombre'], fila['email'], fila.get('telefono', ''))
    except Exception as e:
        print(f"Error cargando trabajadores: {e}")
    return trabajadores

def guardar_trabajadores(trabajadores_dict):
    try:
        # Estrategia simple: borrar todos e insertar de nuevo
        supabase.table('trabajadores').delete().neq('id', -1).execute()
        if trabajadores_dict:
            filas = [
                {'id': id_, 'nombre': nombre, 'email': email, 'telefono': telefono}
                for id_, (nombre, email, telefono) in trabajadores_dict.items()
            ]
            supabase.table('trabajadores').insert(filas).execute()
    except Exception as e:
        print(f"Error guardando trabajadores: {e}")

# ------------------------------------------------------------
# Configuración de correo
# ------------------------------------------------------------
def guardar_config_correo(email, password):
    pass_encoded = base64.b64encode(password.encode()).decode()
    try:
        supabase.table('configuraciones').upsert({'clave': 'EMAIL', 'valor': email}).execute()
        supabase.table('configuraciones').upsert({'clave': 'PASSWORD', 'valor': pass_encoded}).execute()
    except Exception as e:
        print(f"Error guardando config correo: {e}")

def cargar_config_correo():
    config = {'EMAIL': '', 'PASSWORD': ''}
    try:
        resp = supabase.table('configuraciones').select('*').in_('clave', ['EMAIL', 'PASSWORD']).execute()
        for fila in resp.data:
            if fila['clave'] == 'EMAIL':
                config['EMAIL'] = fila['valor']
            elif fila['clave'] == 'PASSWORD':
                config['PASSWORD'] = base64.b64decode(fila['valor'].encode()).decode()
    except Exception as e:
        print(f"Error cargando config correo: {e}")
    return config

# ------------------------------------------------------------
# Configuración de Telegram
# ------------------------------------------------------------
def guardar_config_telegram(api_id, api_hash, telefono_remitente):
    try:
        supabase.table('configuraciones').upsert({'clave': 'TELEGRAM_API_ID', 'valor': api_id}).execute()
        supabase.table('configuraciones').upsert({'clave': 'TELEGRAM_API_HASH', 'valor': api_hash}).execute()
        supabase.table('configuraciones').upsert({'clave': 'TELEGRAM_REMITENTE', 'valor': telefono_remitente}).execute()
    except Exception as e:
        print(f"Error guardando config telegram: {e}")

def cargar_config_telegram():
    config = {'api_id': '', 'api_hash': '', 'telefono_remitente': ''}
    try:
        resp = supabase.table('configuraciones').select('*').in_(
            'clave', ['TELEGRAM_API_ID', 'TELEGRAM_API_HASH', 'TELEGRAM_REMITENTE']
        ).execute()
        for fila in resp.data:
            if fila['clave'] == 'TELEGRAM_API_ID':
                config['api_id'] = fila['valor']
            elif fila['clave'] == 'TELEGRAM_API_HASH':
                config['api_hash'] = fila['valor']
            elif fila['clave'] == 'TELEGRAM_REMITENTE':
                config['telefono_remitente'] = fila['valor']
    except Exception as e:
        print(f"Error cargando config telegram: {e}")
    return config

# ------------------------------------------------------------
# Sesión de Telegram (StringSession local)
# ------------------------------------------------------------
def guardar_session_telegram_local(session_string):
    try:
        with open('telegram_session.txt', 'w', encoding='utf-8') as f:
            f.write(session_string)
    except Exception as e:
        print(f"Error guardando session Telegram local: {e}")

def cargar_session_telegram_local():
    try:
        with open('telegram_session.txt', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error cargando session Telegram local: {e}")
        return None

# ------------------------------------------------------------
# Registro de envíos exitosos (reportes)
# ------------------------------------------------------------
def registrar_envio_exitoso(nombre, id_trabajador, metodo, archivo_pdf):
    try:
        supabase.table('envios').insert({
            'fecha': datetime.now().isoformat(),
            'id_trabajador': id_trabajador,
            'nombre': nombre,
            'metodo': metodo,
            'archivo': Path(archivo_pdf).name
        }).execute()
    except Exception as e:
        print(f"Error registrando envío: {e}")

def cargar_envios_exitosos():
    """Devuelve una lista de tuplas (id_envio, fecha, id_trabajador, nombre, metodo, archivo)."""
    try:
        resp = supabase.table('envios').select('*').order('fecha', desc=True).execute()
        resultados = []
        for fila in resp.data:
            fecha = fila['fecha']
            if isinstance(fecha, str):
                fecha_str = fecha
            else:
                fecha_str = fecha.strftime('%Y-%m-%d %H:%M:%S')
            resultados.append((
                fila['id'],                    # id interno del envío
                fecha_str,
                str(fila['id_trabajador']),
                fila['nombre'],
                fila['metodo'],
                fila['archivo']
            ))
        return resultados
    except Exception as e:
        print(f"Error cargando envíos exitosos: {e}")
        return []

def eliminar_envio(id_envio):
    """Elimina un envío por su id interno."""
    try:
        supabase.table('envios').delete().eq('id', id_envio).execute()
        return True
    except Exception as e:
        print(f"Error eliminando envío: {e}")
        return False

def eliminar_envios_anteriores_a(fecha_limite_str):
    """Elimina envíos con fecha menor a la fecha límite (formato ISO)."""
    try:
        supabase.table('envios').delete().lt('fecha', fecha_limite_str).execute()
        return True
    except Exception as e:
        print(f"Error eliminando envíos antiguos: {e}")
        return False