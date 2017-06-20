#!/usr/bin/python
# -*- coding: utf-8 -*-
from OpenWebNet import OpenWebNet
from pprint import pprint
import time

f454 = OpenWebNet("192.168.201.122","20000")

# extinction de la zone 4
# f454.setTemperatureSensorSetOffMode("4")
# time.sleep(5)
# f454.setTemperatureSensorSetAntiFreezeMode("4")
# time.sleep(5)

# si la centrale est compatible avec une selection piece par piece de la temperature ... (pas possible avec les centrales 4 zones)
# on chauffe à 23.4° la zone 4
# f454.setTemperatureSensorSetPointIn99ZonesMainUnit("4","0234")


print "-------------------------------------------------------"
print "recherche tous les thermostats"
list_temperature_sensor_ids = f454.findTemperatureSensors(range(1,5))
print "found theses temperature sensors ids within range = "
pprint(list_temperature_sensor_ids)
print ""
for sensor in list_temperature_sensor_ids:
    temperature_status = f454.getTemperaturesSensorStatus(sensor)
    pprint(temperature_status)


print "-------------------------------------------------------"
print "mise à jour à 18,5 degres de la zone 4"
f454.setTemperatureSensorSetPoint("4",18.5)


print "-------------------------------------------------------"
print "recherche tous les thermostats"
list_temperature_sensor_ids = f454.findTemperatureSensors(range(1,5))
print "found = "
pprint(list_temperature_sensor_ids)
print ""
for sensor in list_temperature_sensor_ids:
    temperature_status = f454.getTemperaturesSensorStatus(sensor)
    pprint(temperature_status)


print "-------------------------------------------------------"
print "recherche tous les interrupteurs de lumiere présents"
list_light_sensor_ids = f454.findLightSensors(range(10,12)) # ici, on cherche les ids 10 à 15
print "found = "
pprint(list_light_sensor_ids)
print ""
for sensor in list_light_sensor_ids:
    print "switch off sensor #" + str(sensor)
    f454.setLightSensorStatus(sensor,0)
    time.sleep(1)
    light_status = f454.getLightSensorStatus(sensor)
    pprint(light_status)

    time.sleep(3)
    print "switch on sensor #" + str(sensor)
    f454.setLightSensorStatus(sensor,1)
    time.sleep(1)
    light_status = f454.getLightSensorStatus(sensor)
    pprint(light_status)


