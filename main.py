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
MQTT_TOPIC_TEMPERATURE = f"channels/{config.mqtt_channel_id}/publish/fields/field1"
# MQTT_TOPIC_HUMIDITY = f"channels/{config.mqtt_channel_id}/publish/fields/field2"
# MQTT_TOPIC_PRESSURE = f"channels/{config.mqtt_channel_id}/publish/fields/field3"
# MQTT_PUBLISH = f"channels/{config.mqtt_channel_id}/publish/{config.mqtt_write_api_key}"

# MQTT parameters
# Son constantes que nos sirven para conectarnos al servidor MQTT de ThingSpeak.
# Estos datos los hemos obtenido al crear el canal de ThingSpeak.
MQTT_SERVER = config.mqtt_server
MQTT_PORT = config.mqtt_port
MQTT_USER = config.mqtt_username
MQTT_PASS = config.mqtt_password
MQTT_CLIENT_ID = config.mqtt_clientId
MQTT_KEEP_ALIVE = 7200
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
            keepalive=MQTT_KEEP_ALIVE,
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

    display.text("Initializing...", 0, 0)
    display.show()

    init_wifi(config.wifi_ssid, config.wifi_password)
    display.text("WiFi connected", 0, 10)
    display.show()

    client = connect_mqtt()
    display.text("MQTT connected", 0, 30)
    display.show()

    display.fill(0)
    display.text("Waiting...", 0, 0)
    display.show()

    sleep(2)

    while True:
        try:
            # primero obtenemos los datos
            temperature, humidity, pressure = get_sensor_readings()

            # despues los publicamos en los campos correspondientes del canal de ThingSpeak
            publish_mqtt(topic=MQTT_TOPIC_TEMPERATURE, message=str(temperature))
            # publish_mqtt(topic=MQTT_TOPIC_HUMIDITY, message=str(humidity))
            # publish_mqtt(topic=MQTT_TOPIC_PRESSURE, message=str(pressure))
            # publish_mqtt(
            #     topic=MQTT_PUBLISH,
            #     message=f"field1={temperature}&field2={humidity}&field3={pressure}&status=MQTTPUBLISH",
            # )

            display.fill(0)
        except Exception as e:
            print("An error occurred:", e)

        # mostramos los datos en la pantalla OLED
        display.text("Sensor data:", 0, 0)
        display.text("Temp: " + str(temperature), 0, 20)
        display.text("Humi: " + str(humidity), 0, 30)
        display.text("Pres: " + str(pressure), 0, 40)

        display.show()

        sleep(60 * 5)
