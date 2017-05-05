#!/usr/bin/env python3

#---------------------------------------------------------------------------------------
# Load configuration values
#
#---------------------------------------------------------------------------------------

# see https://wiki.python.org/moin/ConfigParserShootout
from configobj import ConfigObj
config = ConfigObj('/home/philip/Development/projects/python/pythonMqttPlotter/pythonMqttPlotter.cfg')

print("{0}".format("Python MQTT Json Plotter"))


import numpy as np
import matplotlib.pyplot as plt

# based on code at http://block.arch.ethz.ch/blog/2016/08/dynamic-plotting-with-matplotlib/

imu_fig = plt.figure(1)

#temp = plt.subplot(211)
temp_ax = imu_fig.add_subplot(211)
temp_ax.set_title('IMU Temperature')
tempxdata = []
tempydata = []
tempaxes = plt.gca()
temp_ax.set_xlabel=('time')
temp_ax.set_ylabel=('temperature')
templine, = tempaxes.plot(tempxdata, tempydata, 'r-')

#plt.subplot(212)
pres_ax = imu_fig.add_subplot(212)
pres_ax.set_title('IMU Pressure')
presxdata = []
presydata = []
presaxes = plt.gca()
plt.xlabel='time'
plt.ylabel='pressure'
presline, = presaxes.plot(presxdata, presydata, 'r-')

curr_fig = plt.figure(2)

curr_ax = curr_fig.add_subplot(111)
currxdata = []
currydata = []
curraxes = plt.gca()
curr_ax.set_title('Current')
curr_ax.set_xlabel='time'
curr_ax.set_ylabel='current'
currline, = curraxes.plot(currxdata, currydata, 'r-')
#plt.show()

import time

def plot_current(data) :
	# data is a float
	print(data)
	plt.figure(2)
	plt.subplot(111)
	currxdata.append(int(time.time()))
	currydata.append(data)
	currline.set_xdata(currxdata)
	currline.set_ydata(currydata)
	curraxes.relim()
	curraxes.autoscale_view(False,True,True)
	plt.draw()
	plt.pause(0)

def plot_update(data) :
	# data is an float
	print(data)
	timestamp = int(time.time())
	plt.figure(1)
	plt.subplot(211)
	tempxdata.append(timestamp)
	tempydata.append(float(data['temperature']))
	templine.set_xdata(tempxdata)
	templine.set_ydata(tempydata)
	tempaxes.relim()
	tempaxes.autoscale_view(False,True,True)
#	plt.draw()
	plt.subplot(212)
	presxdata.append(timestamp)
	presydata.append(float(data['pressure']))
	presline.set_xdata(presxdata)
	presline.set_ydata(presydata)
	presaxes.relim()
	presaxes.autoscale_view(False,True,True)
	plt.draw()
	plt.pause(0)


#---------------------------------------------------------------------------------------
# Modules and methods to support MQTT
#
#---------------------------------------------------------------------------------------

import json

import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc) :
	print("Connected with result code "+str(rc))
	# Subscribing in on_connect() means that if the connection is lost
	# the subscriptions will be renewed when reconnecting.
	print("Subscribing to topics ...")
	for topic in config['mqtt_topics']['TOPICS'] :
		client.subscribe(topic)
		print("{0}".format(topic))

def on_subscribe(client, userdata, mid, granted_qos) :
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, message) :
	print("message received:\n{0}: {1}".format(message.topic, message.payload))
	if (message.topic == "sensor/berryimu/measurements") :
		data = json.loads(message.payload.decode('utf-8'));
		plot_update(data)
	elif (message.topic == "relayshield/measurement/current") :
		plot_current(float(message.payload.decode(encoding='UTF-8',errors='strict')))

def on_publish(client, userdata, mid) :
    print("mid: {0}".format(str(mid)))

def on_disconnect(client, userdata, rc) :
	print("Disconnect returned:")
	print("client: {0}".format(str(client)))
	print("userdata: {0}".format(str(userdata)))
	print("result: {0}".format(str(rc)))

def on_log(client, userdata, level, buf) :
    print("{0}".format(buf))

mqttc               = mqtt.Client()
mqttc.on_connect    = on_connect
mqttc.on_subscribe  = on_subscribe
mqttc.on_message    = on_message
mqttc.on_publish    = on_publish
mqttc.on_disconnect = on_disconnect
# Uncomment to enable debug messages
#client.on_log       = on_log

mqttc.connect(
               config['mqtt_configuration']['MQTT_BROKER_IP'],
               int(config['mqtt_configuration']['MQTT_BROKER_PORT']),
               int(config['mqtt_configuration']['MQTT_BROKER_PORT_TIMEOUT']),
               )

#mqttc.loop_start()


#---------------------------------------------------------------------------------------
# Main program methods
#
#---------------------------------------------------------------------------------------

import sys
import getopt

def tidyupAndExit() :
	running = False       #Stop thread1
	# Disconnect mqtt client			mqttc.loop_stop()
	mqttc.disconnect()
	plt.show()
	print("Bye")
	sys.exit(0)

def main(argv) :
	try :
		opts, args = getopt.getopt(argv,"ht:",["track="])
	except getopt.GetoptEror :
		print("pythonMqttPlotter -h")
		tidyupAndExit()
	for opt, arg in opts :
		if opt == '-h' :
			print("pythonMqttPlotter -h")
		if opt == '-t' :
			trackNumber = arg
	# Loop continuously
	while True :
		try :
			mqttc.loop()
		except KeyboardInterrupt :      #Triggered by pressing Ctrl+C
			tidyupAndExit()

if __name__ == "__main__" :
	main(sys.argv[1:])
