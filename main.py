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
MQTT_TOPIC_TEMP = f"channels/{config.mqtt_channerId}/publish/fields/field1"
MQTT_TOPIC_HUM = "pico/humidity"
MQTT_TOPIC_PRES = "pico/pressure"

# MQTT parameters
MQTT_SERVER = config.mqtt_server
MQTT_PORT = config.mqtt_port
MQTT_USER = config.mqtt_username
MQTT_PASS = config.mqtt_password
MQTT_CLIENT_ID = config.mqtt_clientId
MQTT_KEEPALIVE = 7200
MQTT_SSL = False

# Initialize I2C communication
i2c = I2C(id=0, scl=Pin(5), sda=Pin(4))

# init oled
display = ssd1306.SSD1306_I2C(128, 64, i2c)

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
    display.show()
    sleep(1)
    client = connect_mqtt()
    display.text("Connected to MQTT", 0, 10)
    display.show()
    sleep(1)
    display.fill(0)

    while True:
        try:
            temerature, humidity, pressure = get_sensor_readings()

            publish_mqtt(MQTT_TOPIC_TEMP, str(temerature))
            display.text("Temp: " + str(temerature), 0, 0)
            display.show()
        except Exception as e:
            print("An error occurred:", e)

        sleep(60 * 5)
        display.fill(0)
