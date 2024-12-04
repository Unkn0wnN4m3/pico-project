from machine import I2C, Pin
from time import sleep
from utils import init_wifi, get_sensor_readings
from umqtt.simple import MQTTClient, MQTTException

import bme280_float as bme280
import config
import ssd1306

# servers constants
MQTT_SERVER = config.mqtt_server
MQTT_PORT = config.mqtt_port
MQTT_USER = config.mqtt_username
MQTT_PASS = config.mqtt_password
MQTT_CLIENT_ID = config.mqtt_clientId

# Topics
MQTT_TOPIC_TEMPERATURE = f"channels/{config.mqtt_channel_id}/publish/fields/field1"
# MQTT_TOPIC_HUMIDITY = f"channels/{config.mqtt_channel_id}/publish/fields/field2"
# MQTT_TOPIC_PRESSURE = f"channels/{config.mqtt_channel_id}/publish/fields/field3"

def btn_callback(pin):
    status_led.toggle()
    display.poweron()
    display.fill(0)

    display.text("Sensor data:", 0, 0, 1)
    display.text("Temp: " + str(bme.values[0]), 0, 20, 1)
    display.text("Pres: " + str(bme.values[1]), 0, 30, 1)
    display.text("Humi: " + str(bme.values[2]), 0, 40, 1)
    
    display.show()
    sleep(5)
  
    display.poweroff()
    status_led.toggle()


if __name__ == "__main__":
    # interrupt button
    btn = Pin(11, Pin.IN, Pin.PULL_UP)
    status_led = Pin("LED", Pin.OUT, value=1)

    # init i2c communication
    i2c = I2C(id=0, scl=Pin(5), sda=Pin(4))

    # init oled display 64x128
    display = ssd1306.SSD1306_I2C(128, 64, i2c)

    # init bme280
    bme = bme280.BME280(i2c=i2c)

    # init wifi
    init_wifi(config.wifi_ssid, config.wifi_password)
    
    # making client object
    client = MQTTClient(
        MQTT_CLIENT_ID,
        MQTT_SERVER,
        port = MQTT_PORT,
        user = MQTT_USER,
        password = MQTT_PASS,
    )

    btn.irq(trigger=Pin.IRQ_FALLING, handler=btn_callback)

    while True:
        try:
            temperature, humidity, pressure = get_sensor_readings(bme)
            
            client.connect()
            
            client.publish(MQTT_TOPIC_TEMPERATURE, str(temperature))
            print("published:", MQTT_TOPIC_TEMPERATURE, temperature)
        except MQTTException as e:
            print("MQTT error:", e)
        except Exception as e:
            print("Something went wrong:", e)
        finally:
            client.disconnect()

        sleep(60 * 5)
