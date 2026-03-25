import tkinter as tk
import asyncio
import websockets
import json
import threading

# === CONFIGURACIÓN DE LA VENTANA FANTASMA ===
root = tk.Tk()
root.overrideredirect(True) # Quita los bordes de la ventana y los botones de cerrar
root.wm_attributes("-topmost", True) # Fuerza a que siempre esté por encima de otras ventanas
root.wm_attributes("-transparentcolor", "black") # Todo lo que sea negro, se volverá invisible
root.config(bg="black")

# Colocamos la ventana en la esquina superior izquierda (puedes arrastrarla después)
root.geometry("+20+20")

# Diseñamos el texto (Estilo Hacker/Steam)
label = tk.Label(root, text="Cargando HUD...", font=('Consolas', 10, 'bold'), 
                 fg='#3fb950', bg='black', justify='left')
label.pack(padx=5, pady=5)

# === CONEXIÓN AL MOTOR CENTRAL ===
async def recibir_datos():
    uri = "ws://127.0.0.1:8765" # Se conecta a tu propio motor local
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    mensaje = await websocket.recv()
                    datos = json.loads(mensaje)
                    
                    ping = datos.get("_global_", {}).get("ping", "---")
                    
                    # Sumamos todo el tráfico de red de tu PC
                    total_rx = 0.0
                    total_tx = 0.0
                    for interfaz, stats in datos.items():
                        if interfaz != "_global_":
                            total_rx += stats.get("rx", 0.0)
                            total_tx += stats.get("tx", 0.0)
                    
                    # Actualizamos el texto en pantalla
                    texto = f"Ping: {ping} ms\n⬇ {total_rx:.2f} MB/s\n⬆ {total_tx:.2f} MB/s"
                    label.config(text=texto)
                    
        except Exception:
            label.config(text="Desconectado del motor...")
            await asyncio.sleep(2)

# Arrancamos la red en un hilo separado para que no congele el texto
def iniciar_hilo_red():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(recibir_datos())

hilo = threading.Thread(target=iniciar_hilo_red, daemon=True)
hilo.start()

# === FUNCIÓN PARA ARRASTRAR EL HUD ===
# Si haces clic izquierdo y lo mantienes presionado sobre el texto, puedes moverlo por la pantalla
def mover_ventana(event):
    root.geometry(f'+{event.x_root}+{event.y_root}')

label.bind('<B1-Motion>', mover_ventana)

# Iniciar la pantalla gráfica
root.mainloop()