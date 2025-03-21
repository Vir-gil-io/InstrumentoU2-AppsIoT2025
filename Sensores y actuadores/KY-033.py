from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración WiFi
WIFI_SSID = "DESKTOP-LU8P09G 2015"
WIFI_PASSWORD = "39w2F61?"

# Configuración MQTT
MQTT_BROKER = "192.168.137.69"
MQTT_CLIENT_ID = ""
MQTT_TOPIC = "sensor/Linea"
MQTT_PORT = 1883

# Configuración del KY-033 (Sensor de Línea)
pin_ky033 = Pin(4, Pin.IN, Pin.PULL_UP)  # Conectar el KY-033 al GPIO4

# Variable para almacenar el último estado
ultimo_estado = None

# Función para conectar a WiFi
def conectar_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    
    for _ in range(30):  # Esperar 9 segundos máximo
        if sta_if.isconnected():
            print("WiFi conectada")
            return
        time.sleep(0.3)
    
    print("Error: No se pudo conectar a WiFi")
    raise Exception("No se pudo conectar a WiFi")

# Función para conectar al broker MQTT
def conectar_broker():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print("Conectado a MQTT")
        return client
    except Exception as e:
        print("Error al conectar con MQTT:", e)
        return None

# Función para leer el estado del KY-033
def leer_estado():
    return pin_ky033.value()  # Leer el valor del pin (0 o 1)

# Conectar a WiFi
conectar_wifi()

# Conectar al broker MQTT
client = conectar_broker()

# Bucle principal
while True:
   
        estado_actual = leer_estado()  # Obtener el estado actual
        
        # Determinar si se detectó una línea
        if estado_actual == 0:  # 0 indica que se detectó una línea (superficie oscura)
            mensaje = "Línea detectada"
        else:
            mensaje = "No se detectó línea"
        
        # Solo enviar un mensaje si el estado ha cambiado
        if mensaje != ultimo_estado:
            print(mensaje)  # Imprimir en la consola
            
            if client:  # Si hay conexión MQTT
                try:
                    client.publish(MQTT_TOPIC, mensaje)  # Enviar mensaje al broker MQTT
                except Exception as e:
                    print("Error al enviar MQTT:", e)
                    client = conectar_broker()  # Intentar reconectar
            
            ultimo_estado = mensaje  # Actualizar el último estado
        
        time.sleep(0.1)  # Esperar 0.1 segundos entre lecturas
        
   
