# Wiznet2022Contest
Predict rain using various parameter such the atmospheric pressure, Altitude, and temperature. along with the help of rain sensor to notify user regarding the weather outdoor such as raining and not raining. The User can take necessary action 

Components : 
The following components are used in this project 
WizFi360-EVB-Pico : 

WizFi360-EVB-Pico is based on Raspberry Pi RP2040 and adds Wi-Fi connectivity using WizFi360. It is pin compatible with Raspberry Pi Pico board and can be used for IoT Solution development. 

BMP280 :  

The BMP280 is an absolute barometric pressure sensor  

Rain Drop Sensor: 

Raindrop Sensor is a tool used for sensing rain. It consists of two modules, a rain board that detects the rain and a control module, which compares the analog value, and converts it to a digital value. 

PCF8591 :

The PCF8591 is a single-chip device with four analog inputs, one analog output and a serial I2C-bus interface. 

Libraries used: 
All libraries used in this project are from adafruit. 

digitalio – For the purpose of using io pins  
adafruit_pcf8591 – support for pcf8591 module lib 
adafruit_bmp280 – support for bmp280 sensor lib 
adafruit_espatcontrol – support for wifi management lib 
adafruit_minimqtt.adafruit_minimqtt – mqtt server loib 
adafruit_io.adafruit_io – adafruit mqtt server lib 

Working of Project: 
The BMp280 sensor is used the measure the pressure , temperature and altitude of the environment. 
The raindrop sensor is used to deduct rain  

Since the rain drop sensor is a digital and analog based sensor to suppprt the analog data. 
We have used the PCF8591 to convert from analog to digital data via i2c interface. 
The collected data is sent to adarfruit IO MQTT server for the user to monitor . 
 
