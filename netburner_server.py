import psutil
import asyncio
import websockets
import json
import time
import csv
import os
import threading
from datetime import datetime

# Nuevas librerías para el System Tray
import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as item

# === CONFIGURACIÓN ===
LIMITE_PICO_MB = 5.0 
ARCHIVO_LOG = "historial_picos.csv"

# Memoria global
interfaces_descubiertas = set()
estado_anterior = psutil.net_io_counters(pernic=True)

def registrar_pico(interfaz, rx_mb, tx_mb):
    archivo_existe = os.path.isfile(ARCHIVO_LOG)
    with open(ARCHIVO_LOG, mode='a', newline='') as archivo_csv:
        escritor = csv.writer(archivo_csv)
        if not archivo_existe:
            escritor.writerow(["Fecha y Hora", "Interfaz", "Bajada (MB/s)", "Subida (MB/s)"])
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        escritor.writerow([ahora, interfaz, round(rx_mb, 2), round(tx_mb, 2)])

async def medir_latencia():
    try:
        inicio = time.time()
        futuro = asyncio.open_connection('8.8.8.8', 53)
        reader, writer = await asyncio.wait_for(futuro, timeout=1.0)
        writer.close()
        await writer.wait_closed()
        fin = time.time()
        return int((fin - inicio) * 1000)
    except Exception:
        return 999 

async def transmitir_telemetria(websocket):
    global estado_anterior, interfaces_descubiertas
    
    contador_ping = 0
    ping_actual = 0

    try:
        while True:
            await asyncio.sleep(1)
            estado_actual = psutil.net_io_counters(pernic=True)
            
            # Solo hacemos el Ping a Google cada 5 segundos para no saturar el router
            if contador_ping % 5 == 0:
                ping_actual = await medir_latencia()
            contador_ping += 1
            
            paquete_datos = {"_global_": {"ping": ping_actual}}

            for interfaz, stats_actuales in estado_actual.items():
                stats_anteriores = estado_anterior.get(interfaz)
                if stats_anteriores:
                    descarga_mbs = (stats_actuales.bytes_recv - stats_anteriores.bytes_recv) / (1024 * 1024)
                    subida_mbs = (stats_actuales.bytes_sent - stats_anteriores.bytes_sent) / (1024 * 1024)
                    
                    if descarga_mbs > 0.00 or subida_mbs > 0.00 or interfaz in interfaces_descubiertas:
                        if "Loopback" not in interfaz and interfaz != "lo":
                            interfaces_descubiertas.add(interfaz)
                            paquete_datos[interfaz] = {"rx": round(descarga_mbs, 2), "tx": round(subida_mbs, 2)}
                            
                            if descarga_mbs >= LIMITE_PICO_MB or subida_mbs >= LIMITE_PICO_MB:
                                registrar_pico(interfaz, descarga_mbs, subida_mbs)

            await websocket.send(json.dumps(paquete_datos))
            estado_anterior = estado_actual
    except websockets.exceptions.ConnectionClosed:
        pass
# === MOTOR ASÍNCRONO EN SEGUNDO PLANO ===
async def servidor_ws_main():
    # Arrancamos el servidor usando un "context manager" (async with)
    async with websockets.serve(transmitir_telemetria, "0.0.0.0", 8765):
        await asyncio.Future()  # Mantiene el servidor encendido para siempre

def iniciar_servidor_ws():
    # asyncio.run() se encarga de crear y destruir el loop limpiamente
    asyncio.run(servidor_ws_main())

# === GENERADOR DEL ICONO Y APAGADO ===
def crear_icono():
    # Dibuja un icono cuadrado verde oscuro dinámicamente
    imagen = Image.new('RGB', (64, 64), color=(13, 17, 23))
    dibujo = ImageDraw.Draw(imagen)
    dibujo.rectangle((16, 16, 48, 48), fill=(63, 185, 80))
    return imagen

def apagar_motor(icon, item):
    icon.stop()
    os._exit(0) # Esto destruye el proceso de Python limpiamente

if __name__ == "__main__":
    # 1. Arrancamos el servidor de red en un hilo fantasma
    hilo_servidor = threading.Thread(target=iniciar_servidor_ws, daemon=True)
    hilo_servidor.start()

    # 2. Creamos el menú del reloj de Windows
    menu = (item('🛑 Cerrar NetBurner', apagar_motor),)
    icono_sistema = pystray.Icon("NetBurner", crear_icono(), "NetBurner Server", menu)
    
    # 3. Mantenemos el icono vivo (esto bloquea la consola para que no se cierre sola)
    icono_sistema.run()