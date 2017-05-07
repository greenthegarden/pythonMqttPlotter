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

imu_figure = plt.figure(1)
#imu_fig, ((temp_ax), (pres_ax)) = plt.subplots(nrows=2, ncols=1)


temp_axes = imu_figure.add_subplot(211)
temp_axes.set_title('IMU Temperature')
#temp_ax.xaxis_date()
temp_axes.set_xlabel('time')
temp_axes.set_ylabel('temperature')
temp_xdata = []
temp_ydata = []
temp_line, = temp_axes.plot(temp_xdata, temp_ydata, 'r-')

pres_axes = imu_figure.add_subplot(212)
pres_axes.set_title('IMU Pressure')
#pres_ax.xaxis_date()
pres_axes.set_xlabel('time')
pres_axes.set_ylabel('pressure')
pres_xdata = []
pres_ydata = []
pres_line, = pres_axes.plot(pres_xdata, pres_ydata, 'r-')

plt.tight_layout()

curr_figure = plt.figure(2)

# rotate and align the tick labels so they look better
curr_figure.autofmt_xdate()
# use a more precise date string for the x axis locations in the
# toolbar
import matplotlib.dates as mdates

curr_axes = curr_figure.add_subplot(111)
curr_axes.set_title('Current')
curr_axes.xaxis_date()
#curr_ax.fmt_xdata = mdates.DateFormatter('%H:%M:%S')
curr_axes.set_xlabel('time')
curr_axes.set_ylabel('current')
curr_xdata = []
curr_ydata = []
curr_line, = curr_axes.plot(curr_xdata, curr_ydata, 'r-')
#plt.show()

plt.tight_layout()

import time
import datetime

def plot_current(data) :
	# data is a float
	print(data)
	plt.figure(2)
	curr_axes = plt.subplot(111)
#	timestamp = int(time.time())
#	datestamp = datetime.datetime.fromtimestamp(timestamp)
#	currxdata.append(int(time.time()))
	curr_xdata.append(datetime.datetime.now())
	curr_ydata.append(data)
	curr_line.set_xdata(curr_xdata)
	curr_line.set_ydata(curr_ydata)
	curr_axes.relim()
	curr_axes.autoscale_view(False,True,True)
	plt.draw()
	plt.pause(1e-17)

def plot_update(data) :
	# data is an json object
	print(data)
	timestamp = int(time.time())
	datestamp = datetime.datetime.fromtimestamp(timestamp)
	plt.figure(1)
	plt.subplot(211)
	temp_xdata.append(datestamp)
	temp_ydata.append(float(data['temperature']))
	temp_line.set_xdata(temp_xdata)
	temp_line.set_ydata(temp_ydata)
	temp_axes.relim()
	temp_axes.autoscale_view(False,True,True)
#	plt.draw()
	plt.subplot(212)
	pres_xdata.append(timestamp)
	pres_ydata.append(float(data['pressure']))
	pres_line.set_xdata(pres_xdata)
	pres_line.set_ydata(pres_ydata)
	pres_axes.relim()
	pres_axes.autoscale_view(False,True,True)
	plt.draw()
	plt.pause(1e-17)


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
#	plt.show()
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
