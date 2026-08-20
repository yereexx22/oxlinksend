import smtplib
import asyncio
import random
import time
from email.message import EmailMessage
from pathlib import Path
from telethon import TelegramClient
from telethon.sessions import StringSession
from configuracion import (
    cargar_config_telegram,
    registrar_envio_exitoso,
    cargar_session_telegram_local,
    guardar_session_telegram_local,
)
from plantillas import cargar_plantilla

def enviar_correo(destinatario, nombre, id_trabajador, archivo_pdf, log_callback, config):
    try:
        asunto_template, cuerpo_template = cargar_plantilla()
        asunto = asunto_template.replace('{nombre}', nombre)
        cuerpo = cuerpo_template.replace('{nombre}', nombre)

        msg = EmailMessage()
        msg['Subject'] = asunto
        msg['From'] = config['EMAIL']
        msg['To'] = destinatario
        msg.set_content(cuerpo)

        with open(archivo_pdf, 'rb') as f:
            pdf_data = f.read()
        msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=Path(archivo_pdf).name)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(config['EMAIL'], config['PASSWORD'])
            server.send_message(msg)

        log_callback(f'✓ [CORREO] Enviado a {nombre} ({destinatario}) - {Path(archivo_pdf).name}\n', 'success')
        registrar_envio_exitoso(nombre, id_trabajador, 'Correo', archivo_pdf)
    except Exception as e:
        log_callback(f'✗ [CORREO] ERROR con {Path(archivo_pdf).name}: {str(e)}\n', 'error')

async def enviar_telegram_async(destinatario_telefono, nombre, id_trabajador, archivo_pdf, log_callback, config_telegram):
    # Cargar sesión desde archivo local
    session_str = cargar_session_telegram_local()
    if not session_str:
        return (False, '✗ No hay sesión de Telegram guardada. Usa el botón \'Autenticar\' en configuración.')

    # Usar StringSession para evitar bloqueo de SQLite
    client = TelegramClient(
        StringSession(session_str),
        int(config_telegram['api_id']),
        config_telegram['api_hash']
    )

    await client.connect()
    try:
        if not await client.is_user_authorized():
            raise Exception('Telegram no autenticado. Usa el botón \'Autenticar\' en configuración.')
        if not destinatario_telefono.startswith('+'):
            destinatario_telefono = '+' + destinatario_telefono
        await client.send_file(destinatario_telefono, archivo_pdf, caption=f'Nómina de {nombre}')
        registrar_envio_exitoso(nombre, id_trabajador, 'Telegram', archivo_pdf)
        return (True, f'✓ [TELEGRAM] Enviado a {nombre} ({destinatario_telefono}) - {Path(archivo_pdf).name}')
    except Exception as e:
        return (False, f'✗ [TELEGRAM] ERROR con {Path(archivo_pdf).name}: {str(e)}')
    finally:
        # Guardar sesión actualizada (por si hubo cambios)
        try:
            nueva_session = client.session.save()
            if nueva_session and nueva_session != session_str:
                guardar_session_telegram_local(nueva_session)
        except:
            pass
        await client.disconnect()

def enviar_telegram_sincrono(destinatario_telefono, nombre, id_trabajador, archivo_pdf, log_callback):
    try:
        config_telegram = cargar_config_telegram()
        if not config_telegram['api_id'] or not config_telegram['api_hash'] or not config_telegram['telefono_remitente']:
            log_callback('✗ Configuración de Telegram incompleta.\n', 'error')
            return
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success, msg = loop.run_until_complete(
            enviar_telegram_async(destinatario_telefono, nombre, id_trabajador, archivo_pdf, log_callback, config_telegram)
        )
        loop.close()
        log_callback(msg + '\n', 'success' if success else 'error')
        pausa = random.randint(8, 9.3)
        log_callback(f'⏳ Esperando {pausa} segundos antes del siguiente envío Telegram...\n', 'normal')
        time.sleep(pausa)
    except Exception as e:
        log_callback(f'✗ [TELEGRAM] Error general: {str(e)}\n', 'error')