import network
from umqtt.simple import MQTTClient
from machine import Pin
import time

# Configuración WiFi
WIFI_SSID = "DESKTOP-LU8P09G 2015"
WIFI_PASSWORD = "39w2F61?"

# Configuración MQTT
MQTT_BROKER = "192.168.137.69"
MQTT_CLIENT_ID = "ESP32_LED"
MQTT_TOPIC = "sensor/LedBiColor"
MQTT_PORT = 1883

# Configurar el pin del LED
led_pin = Pin(4, Pin.OUT)  # LED conectado al pin 2

# Conectar a WiFi
def conectar_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(30):  # Esperar hasta 9 segundos
        if sta_if.isconnected():
            print("WiFi conectada!")
            return
        time.sleep(0.3)
    print("Error: No se pudo conectar a WiFi")
    return

# Conectar a MQTT
def conectar_broker():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"Conectado a MQTT Broker: {MQTT_BROKER}, Topic: {MQTT_TOPIC}")
        return client
    except Exception as e:
        print(f"Error al conectar con MQTT: {e}")
        return None

# Iniciar conexiones
conectar_wifi()
client = conectar_broker()

# Bucle infinito para controlar el LED
while True:
    led_pin.on()  # Encender el LED
    print("LED Amarillo")
    if client:
        client.publish(MQTT_TOPIC, "1")
    time.sleep(5)  # Mantener encendido por 5 segundos

    led_pin.off()  # Apagar el LED
    print("LED Rojo")
    if client:
        client.publish(MQTT_TOPIC, "0")
    time.sleep(5)  # Mantener apagado por 5 segundos