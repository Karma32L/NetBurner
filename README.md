# 🌐 NetBurner v3.0 Pro

NetBurner es un sistema de auditoría y monitoreo de red en tiempo real. Está diseñado con una arquitectura cliente-servidor ultraligera que se ejecuta en segundo plano, capturando telemetría de red y transmitiéndola a múltiples interfaces gráficas sin consumir apenas recursos del sistema.

## ✨ Características Principales

* **Motor Asíncrono (WebSocket):** Un servidor local en Python que transmite datos en milisegundos sin bloquear tu PC.
* **Sala de Control Web:** Un dashboard en HTML/JS con modo oscuro, gráficas dinámicas de barrido (Chart.js) y lectura de latencia (Ping) en tiempo real.
* **HUD Flotante (Overlay):** Un mini-cliente transparente estilo "Hacker/Steam" que puedes arrastrar por tu pantalla para monitorear tu red mientras juegas o trabajas.
* **Caja Negra (Auto-Logging):** Detecta automáticamente picos anormales de consumo (más de 5 MB/s) y los registra con fecha y hora en un archivo `historial_picos.csv`.
* **Modo Sigilo (System Tray):** Se ejecuta en segundo plano de forma invisible. Incluye un icono dinámico en la barra de tareas de Windows para apagar el motor de forma segura con un clic.

## 🛠️ Requisitos del Sistema

* Python 3.8 o superior.
* Navegador Web moderno (para el Dashboard).

## 📦 Instalación

1. Clona este repositorio o descarga los archivos.
2. Abre tu terminal de preferencia y ejecuta el siguiente comando para instalar las dependencias necesarias:

```bash
pip install psutil websockets pystray pillow

## ☕ Apoya este proyecto

Si NetBurner te ha sido útil para auditar tu red, monitorear tus conexiones o simplemente te gusta el proyecto, considera invitarme un café para seguir desarrollando herramientas:

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](ko-fi.com/karma32l)
