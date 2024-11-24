# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-bme280-micropython/
from machine import Pin, I2C
from time import sleep
from umqtt.simple import MQTTClient
import BME280
import ssd1306
import network
import config
import time

# Constants for MQTT
# Estas constantes nos sirven para publicar los datos en los campos correspondientes
# del canal de ThingSpeak que hemos creado.
MQTT_TOPIC_TEMP = f"channels/{config.mqtt_channerId}/publish/fields/field1"
MQTT_TOPIC_HUMI = f"channels/{config.mqtt_channerId}/publish/fields/field2"
MQTT_TOPIC_PRES = f"channels/{config.mqtt_channerId}/publish/fields/field3"

# MQTT parameters
# Son constantes que nos sirven para conectarnos al servidor MQTT de ThingSpeak.
# Estos datos los hemos obtenido al crear el canal de ThingSpeak.
MQTT_SERVER = config.mqtt_server
MQTT_PORT = config.mqtt_port
MQTT_USER = config.mqtt_username
MQTT_PASS = config.mqtt_password
MQTT_CLIENT_ID = config.mqtt_clientId
MQTT_KEEPALIVE = 7200
MQTT_SSL = False

# Initialize I2C communication
# Crear un objetos de la clase I2C para comunicarnos con el sensor BME280 y con la pantalla OLED.
i2c = I2C(id=0, scl=Pin(5), sda=Pin(4))

# init oled display 64x128
display = ssd1306.SSD1306_I2C(128, 64, i2c)

# init BME280 sensor
bme = BME280.BME280(i2c=i2c)


def get_sensor_readings():
    tempC = bme.temperature
    hum = bme.humidity
    pres = bme.pressure

    return tempC, hum, pres


def init_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("waiting for connection...")
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError("network connection failed")
    else:
        print("connected")
        status = wlan.ifconfig()
        print("ip = " + status[0])


def connect_mqtt():
    try:
        client = MQTTClient(
            MQTT_CLIENT_ID,
            MQTT_SERVER,
            port=MQTT_PORT,
            user=MQTT_USER,
            password=MQTT_PASS,
            ssl=MQTT_SSL,
            ssl_params={},
        )

        client.connect()
        return client
    except Exception as e:
        print("An error occurred while connecting to MQTT:", e)
        # return None
        raise


def publish_mqtt(topic, message):
    try:
        client.publish(topic, message)
        print("Published to MQTT", topic, message)
    except Exception as e:
        print("An error occurred while publishing to MQTT:", e)
        # return None
        raise


if __name__ == "__main__":
    display.fill(0)

    init_wifi(config.wifi_ssid, config.wofi_password)
    display.text("Connected to WiFi", 0, 0)
    display.text("IP: " + str(wlan.ifconfig()[0]), 0, 10)
    display.show()

    sleep(1)

    client = connect_mqtt()
    display.text("Connected to MQTT", 0, 20)
    display.text("Server: " + str(MQTT_SERVER), 0, 30)
    display.show()

    sleep(1)

    display.fill(0)

    while True:
        try:
            # primero obtenemos los datos
            temperature, humidity, pressure = get_sensor_readings()

            # despues los publicamos en los campos correspondientes del canal de ThingSpeak
            publish_mqtt(topic=MQTT_TOPIC_TEMP, message=str(temperature))
            publish_mqtt(topic=MQTT_TOPIC_HUMI, message=str(humidity))
            publish_mqtt(topic=MQTT_TOPIC_PRES, message=str(pressure))

            # mostramos los datos en la pantalla OLED
            display.text("Data sent to MQTT", 0, 0)
            display.text("Temp: " + str(temperature), 0, 20)
            display.text("Humi: " + str(humidity), 0, 30)
            display.text("Pres: " + str(pressure), 0, 40)

            display.show()
        except Exception as e:
            print("An error occurred:", e)

        sleep(60 * 5)
        display.fill(0)
