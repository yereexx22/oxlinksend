import threading
import time
from configuracion import cargar_programados, guardar_programados

class SchedulerThread(threading.Thread):
    def __init__(self, app):
        super().__init__(daemon=True)
        self.app = app
        self.running = True

    def run(self):
        time.sleep(2)
        while self.running:
            ahora = time.time()
            programados = cargar_programados()
            nuevos_programados = []
            for tarea in programados:
                if tarea['timestamp'] <= ahora:
                    self.app.after(0, lambda t=tarea: self.app.ejecutar_tarea_programada(t))
                else:
                    nuevos_programados.append(tarea)
            if len(nuevos_programados) != len(programados):
                guardar_programados(nuevos_programados)
                self.app.after(0, self.app.refresh_lista_programados)
            time.sleep(60)

    def stop(self):
        self.running = False