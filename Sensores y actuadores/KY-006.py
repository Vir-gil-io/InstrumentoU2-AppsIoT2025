#import para acceso a red
import network
#Para usar protocolo MQTT
from umqtt.simple import MQTTClient

#Importamos modulos necesarios
from machine import Pin, PWM
from time import sleep

#Propiedades para conectar a un cliente MQTT
MQTT_BROKER = "192.168.137.69"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = ""
MQTT_TOPIC = "sensor/BuzzPasivo"

MQTT_PORT = 1883

# Configuración del sensor de led
buzzer = PWM(Pin(16))

notas = {
    "Do": 262,
    "Re": 294,
    "Mi": 330,
    "Fa": 349,
    "Sol": 392,
    "La": 440,
    "Si": 494
}

#Función para conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('DESKTOP-LU8P09G 2015', '39w2F61?')
    while not sta_if.isconnected():
        print(".", end="")
        sleep(0.3)
    print("\nWiFi Conectada!")

#Funcion para subscribir al broker, topic
def conecta_broker():
    client = MQTTClient(MQTT_CLIENT_ID,
    MQTT_BROKER, port=MQTT_PORT,
    user=MQTT_USER,
    password=MQTT_PASSWORD,
    keepalive=0)
    client.connect()
    print("Conectado a %s, en el topico %s"%(MQTT_BROKER, MQTT_TOPIC))
    return client

#Conectar a wifi
conectar_wifi()
#Conectando a un broker mqtt
client = conecta_broker()

while True:
    for nota, frecuencia in notas.items():
        buzzer.freq(frecuencia)
        buzzer.duty(512)  # Activar buzzer
        client.publish(MQTT_TOPIC, nota)
        print(nota)
        sleep(1)  # Reproduce cada nota por 1 segundo

    # Apagar el buzzer y enviar "Ninguna nota"
    buzzer.duty(0)
    client.publish(MQTT_TOPIC, "Ninguna nota")
    print("Nada")
    sleep(1)