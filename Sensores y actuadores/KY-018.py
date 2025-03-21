import network
from umqtt.simple import MQTTClient
from machine import Pin, ADC
import time
import math

# 📶 Configuración WiFi
WIFI_SSID = "DESKTOP-LU8P09G 2015"
WIFI_PASSWORD = "39w2F61?"

# 📡 Configuración MQTT
MQTT_BROKER = "192.168.137.69"  # IP del broker MQTT (cambia según tu red)
MQTT_CLIENT_ID = "ESP32_LightSensor"
MQTT_TOPIC = "sensor/Fotorresistencia"  # Topic donde se publicarán los datos
MQTT_PORT = 1883

# 📌 Configuración de constantes del sensor
GAMMA = 0.7
RL10 = 50  # Resistencia del LDR

# 📍 Pines en ESP32
LDR_PIN = 34  # Pin ADC donde está conectado el LDR

# 🛠️ Configuración del LDR (Fotoresistencia)
ldr = ADC(Pin(LDR_PIN))  
ldr.atten(ADC.ATTN_11DB)  # Rango completo (0-3.3V)
ldr.width(ADC.WIDTH_12BIT)  # Rango de 0 a 4095

# 🚀 Función para conectar a WiFi con reintentos
def conectar_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    
    if not sta_if.isconnected():
        print("Conectando a WiFi...")
        sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
        
        for _ in range(30):  # Esperar hasta 9 segundos
            if sta_if.isconnected():
                print("✅ WiFi Conectado:", sta_if.ifconfig())
                return True
            time.sleep(0.3)

        print("⚠️ Error: No se pudo conectar a WiFi")
        return False
    
    print("✅ WiFi ya conectado:", sta_if.ifconfig())
    return True

# 🔌 Función para conectar a MQTT con reintentos
def conectar_broker():
    global client
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"✅ Conectado a MQTT Broker: {MQTT_BROKER}, Topic: {MQTT_TOPIC}")
        return True
    except Exception as e:
        print(f"⚠️ Error al conectar con MQTT: {e}")
        return False



# 🔄 Bucle principal: verifica WiFi antes de MQTT y envía los datos
while True:
    try:
        # ✅ Verificar si WiFi sigue conectado
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print("⚠️ WiFi desconectado. Intentando reconectar...")
            while not conectar_wifi():
                print("⏳ Reintentando WiFi en 5 segundos...")
                time.sleep(5)
            
            # Tras reconectar WiFi, reconectar MQTT
            while not conectar_broker():
                print("⏳ Reintentando conexión MQTT en 5 segundos...")
                time.sleep(5)

        # 🔆 Leer el valor de la fotoresistencia
        analog_value = ldr.read()
        voltage = analog_value / 4095.0 * 3.3
        
        if voltage > 0:  # Evitar división por 0
            resistance = 2000 * voltage / (1 - voltage / 3.3)
            lux = math.pow(RL10 * 1e3 * math.pow(10, GAMMA) / resistance, (1 / GAMMA))
        else:
            lux = 0  # Si el voltaje es 0, asumimos oscuridad total

        # 📌 Mostrar valores en la consola
        print(f"🔆 Lux: {lux:.2f}")

        # 📤 Enviar datos a MQTT para Node-RED
        if client:
            client.publish(MQTT_TOPIC, str(lux))
            print(f"📡 Publicado en MQTT: {lux:.2f}")

        time.sleep(3)  # Leer cada 3 segundos

    except OSError as e:
        print(f"⚠️ Error en el bucle principal: {e}")
        print("🔄 Intentando reconectar MQTT en 5 segundos...")
        time.sleep(5)
        conectar_broker()
