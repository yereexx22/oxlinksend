import json
import sys
import zipfile
import shutil
from pathlib import Path
import tempfile
import threading
import requests

# Versión actual de tu aplicación
VERSION_ACTUAL = "1.0.0"

# URL del archivo version.json en GitHub
URL_VERSION = "https://raw.githubusercontent.com/yereexx22/oxlinksend/master/version.json"

class Actualizador:
    def __init__(self):
        self.version_remota = None
        self.url_descarga = None

    def verificar_actualizacion(self):
        """Verifica si hay una nueva versión disponible."""
        try:
            response = requests.get(URL_VERSION, timeout=10)
            response.raise_for_status()
            datos = json.loads(response.text)
            self.version_remota = datos.get('version', '')
            self.url_descarga = datos.get('url_descarga', '')
            
            if self._comparar_versiones(self.version_remota, VERSION_ACTUAL) > 0:
                return True, self.version_remota
            return False, None
        except Exception as e:
            print(f"Error verificando actualización: {e}")
            return None, None

    def _comparar_versiones(self, v1, v2):
        """Compara versiones. Retorna 1 si v1 > v2, -1 si v1 < v2, 0 si iguales."""
        try:
            partes1 = [int(x) for x in v1.split('.')]
            partes2 = [int(x) for x in v2.split('.')]
            max_len = max(len(partes1), len(partes2))
            partes1.extend([0] * (max_len - len(partes1)))
            partes2.extend([0] * (max_len - len(partes2)))
            
            for p1, p2 in zip(partes1, partes2):
                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1
            return 0
        except:
            return 0

    def descargar_e_instalar(self, callback_progreso=None):
        """Descarga e instala la actualización."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)
                archivo_zip = temp_dir / "actualizacion.zip"
                
                # Descargar
                if callback_progreso:
                    callback_progreso("Descargando actualización...", 0.1)
                
                response = requests.get(self.url_descarga, stream=True)
                total_size = int(response.headers.get('content-length', 0))
                
                with open(archivo_zip, 'wb') as f:
                    descargado = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        descargado += len(chunk)
                        if total_size > 0 and callback_progreso:
                            progreso = 0.1 + (descargado / total_size * 0.6)
                            callback_progreso(f"Descargando... {int(progreso*100)}%", progreso)
                
                # Extraer
                if callback_progreso:
                    callback_progreso("Extrayendo archivos...", 0.7)
                
                with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir / "extraido")
                
                # Obtener directorio de la app
                app_dir = Path(sys.argv[0]).parent
                
                # Crear backup
                if callback_progreso:
                    callback_progreso("Creando backup...", 0.8)
                
                backup_dir = app_dir / "backup"
                if backup_dir.exists():
                    shutil.rmtree(backup_dir)
                backup_dir.mkdir()
                
                # Copiar archivos nuevos
                archivos_nuevos = temp_dir / "extraido"
                for archivo in archivos_nuevos.iterdir():
                    if archivo.name != 'backup':
                        destino = app_dir / archivo.name
                        if destino.exists() and archivo.is_file():
                            shutil.copy2(destino, backup_dir / archivo.name)
                        if archivo.is_dir():
                            if destino.exists():
                                shutil.rmtree(destino)
                            shutil.copytree(archivo, destino)
                        else:
                            shutil.copy2(archivo, destino)
                
                if callback_progreso:
                    callback_progreso("¡Actualización completada!", 1.0)
                
                return True
                
        except Exception as e:
            print(f"Error instalando actualización: {e}")
            return False