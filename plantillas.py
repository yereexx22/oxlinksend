def guardar_plantilla(asunto, cuerpo):
    with open('plantilla.txt', 'w', encoding='utf-8') as f:
        f.write(asunto + '\n')
        f.write(cuerpo)

def cargar_plantilla():
    asunto_default = 'Tu nómina de pago - {nombre}'
    cuerpo_default = 'Hola {nombre},\n\nAdjunto encontrarás tu nómina de este periodo.\n\nSaludos cordiales.'
    try:
        with open('plantilla.txt', 'r', encoding='utf-8') as f:
            lineas = f.read().split('\n', 1)
            asunto = lineas[0].strip()
            cuerpo = lineas[1].strip() if len(lineas) > 1 else cuerpo_default
            return (asunto, cuerpo)
    except FileNotFoundError:
        guardar_plantilla(asunto_default, cuerpo_default)
        return (asunto_default, cuerpo_default)