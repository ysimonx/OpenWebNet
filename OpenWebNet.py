#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import sys
import pprint
import re
import time

class OpenWebNet: # Définition de notre classe OpenWebNet
    """
    OpenWebNet class Connector .
    """

    REQUEST_MODE                  = "*99*9##"

    ACK_OK                        = "*#*1##"
    ACK_NOK                       = "*#*0##"

    LIGHT_SENSOR_WHO              = "1"
    TEMPERATURE_SENSOR_WHO        = "4"

    SENSOR_TYPE_LIGHT             = "light"
    SENSOR_TYPE_TEMPERATURE       = "temperature"

    DIALOG_TEMPO                  = 0.1

    def __init__(self, host, port):
    	"""
        OpenWebNet class constructor .
        please provwheree :
        host : tcp-ip host to connect to F454 Legrand gateway (usually 192.168.1.35)
        port : tcp-ip port to connect to F454 Legrand gateway (usually 20000)
        """

        self.host = host
        self.port = int(port)
        self.gateway_addr_port = host, int(port)

    def dump(self):
    	"""
        Dumps host and port informations for debug.
        """
        print "host = " + self.host
        print "port = " + str(self.port)


    def connect(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)   # 5 seconds

            sock.connect(self.gateway_addr_port)
            connect_ack = sock.recv(1024)

            # print "connect : " + connect_ack

            if (connect_ack == self.ACK_OK):
                # print "send request = " + s
                sock.send(self.REQUEST_MODE)
                # print "send request mode "
                connect_ack = sock.recv(1024)
                # print "result send request mode : " + connect_ack
                if (connect_ack == self.ACK_OK):
                    return sock

        except socket.error as msg:
            print "Caught exception socket.error : %s" % msg
            sock.close()
            return False

        return False





    def findLightSensors(self, range):
        """
        Lists the Temperature Sensors within provwhereed range (for example range(0,10))
        """
        result = []
        for i in range :
            response = self.sendRequestStatus(self.LIGHT_SENSOR_WHO, i)
            if (response != self.ACK_NOK):
                result.append(i)
        return result



    def getLightSensorStatus(self, where):
        """
        returns the data in a structured dict for a given light where sensor 
        """
        response = self.sendRequestStatus(self.LIGHT_SENSOR_WHO, where)
        result =   self.analyze_response_for_LightSensorData(where, response)
        return result

    def setLightSensorStatus(self, where, value):
        """
            syntax : *1*where*T*##
            exemple for 
                switch on light 11 :   *1*1*11##
                switch off light 11 :  *1*0*11##
        """

        response = self.sendRequestSetStatus(self.LIGHT_SENSOR_WHO, where, value, "*{who}*{value}*{where}##")
        return response




    def findTemperatureSensors(self, range):
    	"""
        Lists the Temperature Sensors within provwhereed range (for example range(0,10))
        """
    	resultat = []
        for i in range :
            response = self.sendRequestStatus(self.TEMPERATURE_SENSOR_WHO, i)
            if (response != self.ACK_NOK):
                resultat.append(i)
        return resultat


    def getTemperaturesSensorStatus(self, where):
    	"""
        returns the data in a structured dict for a given temperature where sensor 
        """
        response = self.sendRequestStatus(self.TEMPERATURE_SENSOR_WHO, where)
        result =   self.analyze_response_for_TemperatureSensorData(where, response)
        return result


    def setTemperatureSensorSetPointIn99ZonesMainUnit(self, where, value):
        """
            Example:
            You set up 10 zone at 21.5°C in heating mode with a 99Zones main unit : example : *#4*#0#10*#14*0215*1## (99 zones main unit: 0, zone 10 at 21.5 heating mode)
            call function with paramaters : where = 10, value = 0215
        
        	how to change centrale temperature : *#4*#0#1*#14*0225*3## (#0 is for centrale, #1 is for centrale 1 (za et zb), 0225 is for 22.5 °
                                                       must force centrale on manual) 
        """
        dim = self.convert_temperature_to_dim(value)
        response = self.sendRequestSetStatus(self.TEMPERATURE_SENSOR_WHO, where, dim, "*#{who}*#0#{where}*#14*{value}*1##")
        return response

    def setTemperatureSensorSetPoint(self, where, value):
        """
            The Temperature can be changed directly ony if the sensor/probe is declared as a "external probe" in my Home Suite
        """

        dim = self.convert_temperature_to_dim(value)
        response = self.sendRequestSetStatus(self.TEMPERATURE_SENSOR_WHO, where, dim, "*#{who}*{where}*#14*{value}*3##")
        return response

    def setTemperatureSensorSetOffMode(self, where):
        """
            Syntax : *4*303*where##
            Example:
                                                          *4*303*4##
        """
        value = ""
        response = self.sendRequestSetStatus(self.TEMPERATURE_SENSOR_WHO, where, value, "*4*303*{where}##")
        return response


    def setTemperatureSensorSetAntiFreezeMode(self, where):
        """
            Syntax : *4*303*where##
            Example:
                                                          *4*303*4##
        """
        value = ""
        response = self.sendRequestSetStatus(self.TEMPERATURE_SENSOR_WHO, where, value, "*4*102*{where}##")
        return response


        
    def sendRequestStatus(self, who, where):
        """
        Connect to gateway
        send request
        readresponse (a long string)
        """
        global_result = {}

        s = "*#"+str(who)+"*"+str(where)+"##"
        scrap_succeeded = False
        must_read = True
        response = ""
    
        try:
            sock = self.connect()
            if (sock != False):
                sock.send(s)
                while (must_read):
                    next = sock.recv(1024)  # now read data from MyHome BUS
                    response = response + next
                    eom  = response.find(self.ACK_OK)
                    eom2 = response.find(self.ACK_NOK)
                    if (eom >=0 or  eom2 >=0):                                   # read until next "##"
                        scrap_succeeded = True
                        must_read = False
                sock.close()

        except socket.error as msg:
            print "Caught exception socket.error : %s" % msg
            sock.close()
            return ""

        time.sleep(self.DIALOG_TEMPO)
        return response



    def sendRequestSetStatus(self, who, where, value, pattern):
        """
        Connect to gateway
        send request
        readresponse (a long string)
        """
        global_result = {}

        s = str(pattern)
        s = s.replace("{who}", str(who))
        s = s.replace("{where}", str(where))
        s = s.replace("{value}", str(value))
        # s = "*"+str(who)+"*"+str(value)+"*"+str(where)+"##"
        scrap_succeeded = False
        must_read = True
        response = ""
 
        try:
            sock = self.connect()
            if (sock != False):
                # print "send request = " + s
                sock.send(s)
                while (must_read):
                    next = sock.recv(1024)  # now read data from MyHome BUS
                    response = response + next
                    eom  = response.find(self.ACK_OK)
                    eom2 = response.find(self.ACK_NOK)
                    if (eom >=0 or  eom2 >=0):                                   # read until next "##"
                        scrap_succeeded = True
                        must_read = False
                sock.close()

        except socket.error as msg:
            print "Caught exception socket.error : %s" % msg
            sock.close()
            return ""

        # print "response set status " + response
        time.sleep(self.DIALOG_TEMPO)
        return response


    def analyze_response_for_LightSensorData(self, where, response):
        """
        extracts informations for a given where sensor and a response from sendRequestStatus function
        """
        result = {}
        sensor_light   = 0
        sensor_ack = ""

        while (response.find("##") >= 0):
            eom = response.find("##")
            msg = response[0:eom+2]     # message is from position 0 until end of ##
            response = response[eom+2:]     # next message starts after ##

            sensor_light_search = re.search('\*'+self.LIGHT_SENSOR_WHO+'\*([0-9]*)\*[0-9]*##', msg)
            if sensor_light_search:
                sensor_light = sensor_light_search.group(1)
                # print "sensor_light = " + sensor_light


            sensor_ack_search = re.search('(\*#\*[0-1]##)', msg)
            if sensor_ack_search:
                sensor_ack = sensor_ack_search.group(1)
                if (sensor_ack == self.ACK_OK):
                    sensor_ack = "ok"
                if (sensor_ack == self.ACK_NOK):
                    sensor_ack = "nok"

        result['SENSOR-WHERE'] = where
        result['SENSOR-TYPE'] = self.SENSOR_TYPE_LIGHT
        result['LIGHT'] = sensor_light
        result['ACK'] = sensor_ack

        return result


    def analyze_response_for_TemperatureSensorData(self, where, response):
    	"""
        extracts informations for a given where sensor and a response from sendRequest function
        """
        result = {}
        sensor_temperature   = 0
        consigne_temperature = 0
        sensor_ack = ""

        while (response.find("##") >= 0):
            eom = response.find("##")
            msg = response[0:eom+2]     # message is from position 0 until end of ##
            response = response[eom+2:]     # next message starts after ##

            sensor_temperature_search = re.search('\*#'+self.TEMPERATURE_SENSOR_WHO+'\*[0-9]\*0\*([0-9]*)##', msg)
            if sensor_temperature_search:
                sensor_temperature = sensor_temperature_search.group(1)
                # print "sensor_temperature = " + sensor_temperature


            sensor_temperature_consigne = re.search('\*#4\*[0-9]\*12\*([0-9]*).*##', msg)
            if sensor_temperature_consigne:
                consigne_temperature = sensor_temperature_consigne.group(1)
                # print "consigne_temperature = " + consigne_temperature

            sensor_ack_search = re.search('(\*#\*[0-1]##)', msg)
            if sensor_ack_search:
                sensor_ack = sensor_ack_search.group(1)
                if (sensor_ack == self.ACK_OK):
                    sensor_ack = "ok"
                if (sensor_ack == self.ACK_NOK):
                    sensor_ack = "nok"

        result['SENSOR-WHERE'] = where
        result['SENSOR-TYPE'] = self.SENSOR_TYPE_TEMPERATURE
        result['TEMPERATURE'] = float(sensor_temperature) / 10
        result['TEMPERATURE-SET-POINT'] = float(consigne_temperature) / 10
        result['ACK'] = sensor_ack

        return result


    def convert_temperature_to_dim(self, temperature):
        """
        convert 21.5 to "0215"
        """
        result = temperature * 10
        result = '%04d' % result
        return result