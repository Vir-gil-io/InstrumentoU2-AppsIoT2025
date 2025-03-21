import network
from umqtt.simple import MQTTClient
from machine import Pin
from time import sleep

# Configuración del KY-003 (sensor de efecto Hall)
sensor_hall = Pin(14, Pin.IN)  # Conectar el KY-003 al pin 14

# Configuración de WiFi
WIFI_SSID = "DESKTOP-LU8P09G 2015"
WIFI_PASSWORD = "39w2F61?"

# Configuración de MQTT
MQTT_BROKER = "192.168.137.69"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = ""
MQTT_TOPIC = "sensor/Hall"  # Tópico para publicar el estado del sensor

# Variable para almacenar el último estado enviado
ultimo_estado = None

# Función para conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    while not sta_if.isconnected():
        print(".", end="")
        sleep(0.3)
    print("\nWiFi Conectada!")

# Función para conectar al broker MQTT
def conectar_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    print("Conectado al broker MQTT")
    return client

# Conectar a WiFi
conectar_wifi()

# Conectar al broker MQTT
client = conectar_mqtt()

# Bucle principal
while True:
    # Leer el estado actual del sensor
    estado_actual = "Campo magnético no detectado" if sensor_hall.value() == 0 else "Campo magnético detectado"
    
    # Solo publicar si el estado actual es diferente al último estado enviado
    if estado_actual != ultimo_estado:
        client.publish(MQTT_TOPIC, estado_actual)
        print(f"Publicado: {estado_actual}")
        ultimo_estado = estado_actual  # Actualizar el último estado enviado
    
    sleep(0.1)  # Pequeña pausa para evitar saturación