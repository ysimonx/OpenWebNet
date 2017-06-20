# OpenWebNet
API pour Domotique Legrand/BtiCino

Cette API permet la consultation et la modification de capteurs et d'actionneurs sur reseau OpenWebNet de Legrand

Il s'agit de déclarer un objet Python, qui est la passerelle TCP/IP - Bus Legrand, et de l'utiliser pour accéder aux différents composants du réseau Legrand



f454 = OpenWebNet("192.168.201.122","20000")

Ici pour consulter la température du sensor numero 4 et son réglage à 18.5 °

temperature_status = f454.getTemperaturesSensorStatus(4)
f454.setTemperatureSensorSetPoint("4",18.5)

Ici pour éteindre et allumer un interrupteur

f454.setLightSensorStatus(sensor,0)
f454.setLightSensorStatus(sensor,1)
