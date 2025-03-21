from machine import Pin, ADC
import network
import time
from umqtt.simple import MQTTClient

# 🔹 CONFIGURACIÓN WiFi y MQTT 🔹
SSID = "DESKTOP-LU8P09G 2015"  # Tu red WiFi
PASSWORD = "39w2F61?"  # Tu contraseña WiFi
MQTT_BROKER = "192.168.137.69"  # IP del broker MQTT (Node-RED)
MQTT_CLIENT_ID = "ESP32_Joystick"
MQTT_TOPIC = "sensor/Joystick"  # Solo un tópico

# 🔹 FUNCIÓN PARA CONECTARSE A WIFI 🔹
def conectar_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID, PASSWORD)

    timeout = 10  # Esperar hasta 10 segundos
    while not wifi.isconnected() and timeout > 0:
        print(f"⏳ Intentando conectar... ({10 - timeout}/10)")
        time.sleep(1)
        timeout -= 1

    if wifi.isconnected():
        print(f"✅ Conectado a WiFi! IP: {wifi.ifconfig()[0]}")
        return True
    else:
        print("❌ No se pudo conectar a WiFi.")
        return False

# 🔹 FUNCIÓN PARA CONECTARSE A MQTT 🔹
def conectar_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("✅ Conectado a MQTT!")
        return client
    except Exception as e:
        print(f"❌ Error conectando a MQTT: {e}")
        return None

# 🔹 CONFIGURAR EL MÓDULO JOYSTICK KY-023 🔹
x_pin = ADC(Pin(34))  # Eje X en GPIO34
y_pin = ADC(Pin(35))  # Eje Y en GPIO35
btn_pin = Pin(32, Pin.IN, Pin.PULL_UP)  # Botón en GPIO32 con pull-up

x_pin.atten(ADC.ATTN_11DB)  # Configurar para leer valores de 0 a 4095
y_pin.atten(ADC.ATTN_11DB)

# 🔹 INICIO DEL PROGRAMA 🔹
if conectar_wifi():
    client = conectar_mqtt()
else:
    print("⛔ No se puede continuar sin WiFi.")
    client = None

# 🔹 FUNCIÓN PARA DETERMINAR EL ESTADO DEL JOYSTICK 🔹
def obtener_estado_joystick(x_value, y_value, btn_value):
    # Si el botón está presionado
    if btn_value == 0:
        return "Presionado"
    
    # Verificar las direcciones con más precisión:
    # Eje X (izquierda/derecha):
    if x_value < 1024:
        return "Izquierda"
    elif x_value > 3072:
        return "Derecha"
    
    # Eje Y (arriba/abajo):
    if y_value < 1024:
        return "Arriba"
    elif y_value > 3072:
        return "Abajo"
    
    # Si no está movido (centro):
    return "Sin mover"

# 🔹 BUCLE PRINCIPAL 🔹
while True:
    x_value = x_pin.read()  # Leer valor X (0-4095)
    y_value = y_pin.read()  # Leer valor Y (0-4095)
    btn_value = btn_pin.value()  # Leer botón (0 = presionado, 1 = sin presionar)

    # Obtener el estado del joystick (dirección o presionado)
    estado = obtener_estado_joystick(x_value, y_value, btn_value)

    print(f"📡 Estado del joystick: {estado} (X: {x_value}, Y: {y_value}, Btn: {btn_value})")

    if client:  # Si MQTT está conectado
        try:
            # Publicar el estado del joystick
            client.publish(MQTT_TOPIC, estado)
        except Exception as e:
            print(f"⚠ Error enviando a MQTT: {e}")
            client = conectar_mqtt()  # Intentar reconectar

    time.sleep(0.5)  # Enviar datos cada 500ms
