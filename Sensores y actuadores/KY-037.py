#import para acceso a red
import network
#Para usar protocolo MQTT
from umqtt.simple import MQTTClient

#Importamos modulos necesarios
from machine import Pin, ADC
from time import sleep

#Propiedades para conectar a un cliente MQTT
MQTT_BROKER = "192.168.137.69"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = ""
MQTT_TOPIC = "sensor/MicrofonoSensible"
# MQTT_TOPIC_PUBLISH = "CAMBIAR_POR_TU_TOPICO"

MQTT_PORT = 1883

#Creo el objeto que me controlará el sensor
adc = ADC(Pin(34))  # Entrada analógica en GPIO 34
adc.atten(ADC.ATTN_11DB)  # Rango de 0 a 3.3V
digital_mic = Pin(17, Pin.IN)  # Entrada digital en GPIO 1

#Función para conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('DESKTOP-LU8P09G 2015', '39w2F61?')
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.3)
    print("\nWiFi Conectada!")



#Funcion para subscribir al broker, topic
def conecta_broker():
    client = MQTTClient(MQTT_CLIENT_ID,
    MQTT_BROKER, port=MQTT_PORT,
    user=MQTT_USER,
    password=MQTT_PASSWORD,
    keepalive=0)
    #client.set_callback(llegada_mensaje)
    client.connect()
    #client.subscribe(MQTT_TOPIC)
    print("Conectado a %s, en el topico %s"%(MQTT_BROKER, MQTT_TOPIC))
    return client

#Funcion encargada de encender un led cuando un mensaje se lo diga
def llegada_mensaje(topic, msg):
    """print("Mensaje:", msg)
    if msg == b'true':
        led.value(1)
    if msg == b'false':
        led.value(0)
"""

#Conectar a wifi
conectar_wifi()
#Conectando a un broker mqtt
client = conecta_broker()

#Ciclo infinito
while True:
    #client.check_msg()
    valor_analogico = adc.read()  # Rango 0 - 4095
    valor_digital = digital_mic.value()  # 0 o 1

    # Publicar en MQTT
    mensaje = f"Analogico: {valor_analogico}, Digital: {valor_digital}"
    print(mensaje)
    client.publish(MQTT_TOPIC, f"{mensaje}")
    
    sleep(1)