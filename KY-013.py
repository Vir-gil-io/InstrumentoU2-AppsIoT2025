import network
import machine
from umqtt.simple import MQTTClient
from machine import Pin, ADC
import time
import json

# Configuración WiFi
SSID = "DESKTOP-LU8P09G 2015"
PASSWORD = "39w2F61?"

# Configuración MQTT
MQTT_BROKER = "192.168.137.69"  # Puedes cambiarlo por tu broker MQTT
MQTT_CLIENT_ID = "ESP32_KY013"
MQTT_TOPIC = "sensor/TempAnaloga"
MQTT_PORT = 1883

# Configuración del sensor KY-013
PIN_SENSOR = 35  # GPIO35 (entrada ADC en ESP32)
sensor = machine.ADC(machine.Pin(PIN_SENSOR))
sensor.atten(machine.ADC.ATTN_11DB)  # Configurar para leer hasta 3.3V

# Función para conectar a WiFi
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print("Conectado a WiFi:", wlan.ifconfig())

# Función para conectar a MQTT
def conectar_mqtt():
    cliente = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, keepalive=30)  # Ajustar keepalive
    cliente.connect()
    print("Conectado al broker MQTT:", MQTT_BROKER)
    return cliente

# Función para leer temperatura (estimación basada en el voltaje del sensor)
def leer_temperatura():
    valor_adc = sensor.read()  # Leer el valor analógico (0 - 4095)
    voltaje = valor_adc * (3.3 / 4095)  # Convertir a voltaje (0 - 3.3V)
    
    # Fórmula ajustada para el sensor KY-013
    # El valor de 0.5V corresponde a 0°C, y el sensor tiene una sensibilidad de aproximadamente 100mV por grado Celsius.
    # La fórmula general es: temperatura (°C) = (voltaje - 0.5) * 100
    temperatura = (voltaje - 0.5) * 100  # Convertir voltaje a temperatura

    return round(temperatura, 2)

# Función para verificar la conexión WiFi
def verificar_wifi():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("Reconectando WiFi...")
        conectar_wifi()

# Función para publicar mensajes en MQTT con manejo de reconexión
def publicar_mensaje(cliente, mensaje):
    try:
        cliente.publish(MQTT_TOPIC, mensaje)
    except OSError:
        print("Error de conexión MQTT. Reintentando...")
        cliente = conectar_mqtt()  # Reconectar
        cliente.publish(MQTT_TOPIC, mensaje)  # Volver a publicar el mensaje

# Configurar WiFi y MQTT
conectar_wifi()
cliente_mqtt = conectar_mqtt()

while True:
    temperatura = leer_temperatura()
    mensaje = f"{temperatura}°C"
    print("Temperatura:", mensaje)

    verificar_wifi()  # Asegurar WiFi activo
    publicar_mensaje(cliente_mqtt, mensaje)  # Manejar error MQTT

    time.sleep(5)  # Publicar cada 5 segundos
