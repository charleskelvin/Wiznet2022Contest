
import time
from microcontroller import cpu
import board
import busio
from digitalio import DigitalInOut
import adafruit_pcf8591.pcf8591 as PCF
from adafruit_pcf8591.analog_in import AnalogIn
from adafruit_pcf8591.analog_out import AnalogOut
# bmp280
import adafruit_bmp280
from digitalio import DigitalInOut, Direction, Pull
# ESP32 AT
from adafruit_espatcontrol import (
    adafruit_espatcontrol,
    adafruit_espatcontrol_wifimanager,
)
import adafruit_espatcontrol.adafruit_espatcontrol_socket as socket
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Debug Level
# Change the Debug Flag if you have issues with AT commands
debugflag = False
# i2c setup
i2c = busio.I2C(board.GP1, board.GP0)

#bme280 sensor
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c,118)
bmp280.sea_level_pressure = 1013.25
print('Temperature: {} degrees C'.format(bmp280.temperature))
print('Pressure: {}hPa'.format(bmp280.pressure))
print('altitude: {}'.format(bmp280.altitude))

#rain drop sensor with converter
pcf = PCF.PCF8591(i2c)
## Analog data
pcf_in_2 = AnalogIn(pcf, PCF.A2)
## Digital data
switch = DigitalInOut(board.GP2)
switch.direction = Direction.INPUT
raw_value = pcf_in_2.value
scaled_value = (raw_value / 65535) * pcf_in_2.reference_voltage
print("Pin 2: %0.2fV" % (scaled_value))
print("")
if switch.value is False:
    print("not raining")
elif switch.value is True:
    print("Raining")

### WiFi ###
RX = board.GP5
TX = board.GP4
resetpin = DigitalInOut(board.GP20)
rtspin = False
uart = busio.UART(TX, RX, baudrate=11520, receiver_buffer_size=2048)
status_light = None

print("ESP AT commands")
esp = adafruit_espatcontrol.ESP_ATcontrol(
    uart, 115200, reset_pin=resetpin, rts_pin=rtspin, debug=debugflag
)
esp.hard_reset()
wifi = adafruit_espatcontrol_wifimanager.ESPAT_WiFiManager(esp, secrets, status_light,attempts=5)

# Configure the RP2040 Pico LED Pin as an output
led_pin = DigitalInOut(board.LED)
led_pin.switch_to_output()

# Define callback functions which will be called when certain events happen.
# pylint: disable=unused-argument
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    print("Connected to Adafruit IO! ")


def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


# pylint: disable=unused-argument
def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print("Disconnected from Adafruit IO!")

# Connect to WiFi
print("Connecting to WiFi...")
wifi.connect()
print("Connected!")

# Initialize MQTT interface with the esp interface
MQTT.set_socket(socket, esp)

# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    port=1883,
    username=secrets["aio_username"],
    password=secrets["aio_key"],
)

# Initialize an Adafruit IO MQTT Client
io = IO_MQTT(mqtt_client)

# Connect the callback methods defined above to Adafruit IO
io.on_connect = connected
io.on_disconnect = disconnected
io.on_subscribe = subscribe

# Connect to Adafruit IO
print("Connecting to Adafruit IO...")
io.connect()
rainStatus = switch.value
while True:
    # Poll for incoming messages
    try:
        io.loop()
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        wifi.connect()
        io.reconnect()
        continue
    # send Presure and temperature for every 5 seconds
    temp = bmp280.temperature
    # truncate to two decimal points
    temp = str(temp)[:5]
    print("temperature is %s degrees C" % temp)
    # publish it to io
    print("Publishing %s to temperature feed..." % temp)
    io.publish("temperature", temp)
    # send pressure data
    pressure = bmp280.pressure
    # truncate to two decimal points
    pressure = str(pressure)[:5]
    print("pressure is %s hPa" % pressure)
    # publish it to io
    print("Publishing %s to pressure feed..." % pressure)
    io.publish("pressure", pressure)
    currentRainStatus = switch.value
    if currentRainStatus is False:
        print("not raining")
        io.publish("rainalert", 1)
    elif switch.value is True:
        print("Raining")
        io.publish("rainalert", 0)
    time.sleep(3);