#!/usr/bin/env python3

#---------------------------------------------------------------------------------------
# Load configuration values
#
#---------------------------------------------------------------------------------------

# see https://wiki.python.org/moin/ConfigParserShootout
from configobj import ConfigObj
config = ConfigObj('/home/philip/Development/projects/python/pythonMqttPlotter/pythonMqttPlotter.cfg')

print("{0}".format("Python MQTT Json Plotter"))


#---------------------------------------------------------------------------------------
# Configure plots
#
#---------------------------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.ticker import FormatStrFormatter

import matplotlib.dates as mdates
DateFmt = mdates.DateFormatter('%H:%M')

# based on code at http://block.arch.ethz.ch/blog/2016/08/dynamic-plotting-with-matplotlib/

imu_figure, imu_axes = plt.subplots(nrows=2, ncols=1, sharex=True)
imu_figure.autofmt_xdate()

temp_idx = 0
pres_idx = 1

idx = temp_idx
imu_axes[idx].set_title('IMU Temperature')
imu_axes[idx].xaxis_date()
imu_axes[idx].xaxis.set_major_formatter(DateFmt)
#temp_axes.set_xlabel('time')
imu_axes[idx].yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
imu_axes[idx].set_ylabel('Temperature (oC)')
temp_xdata = []
temp_ydata = []
temp_line, = imu_axes[temp_idx].plot(temp_xdata, temp_ydata, 'b-o')

idx = pres_idx
imu_axes[idx].set_title('IMU Pressure')
imu_axes[idx].xaxis_date()
imu_axes[idx].xaxis.set_major_formatter(DateFmt)
imu_axes[idx].set_xlabel('Time')
imu_axes[idx].yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
imu_axes[idx].set_ylabel('Pressure (hPa)')
pres_xdata = []
pres_ydata = []
pres_line, = imu_axes[idx].plot(pres_xdata, pres_ydata, 'r-*')

plt.tight_layout()

# curr_figure, curr_axes = plt.subplots()
#
# # rotate and align the tick labels so they look better
# curr_figure.autofmt_xdate()
#
# curr_axes.set_title('ACS712 Current Sensor Measurements')
# curr_axes.xaxis_date()
# curr_axes.xaxis.set_major_formatter(myFmt)
# curr_axes.set_xlabel('Time')
# curr_axes.set_ylabel('Current (A)')
# curr_xdata = []
# curr_ydata = []
# curr_line, = curr_axes.plot(curr_xdata, curr_ydata, 'r-')

pow_figure, pow_axes = plt.subplots(nrows=2, ncols=1, sharex=True)
pow_figure.autofmt_xdate()

curr_idx = 0
volt_idx = 1

idx = curr_idx
pow_axes[idx].set_title('ACS712 Current Sensor Measurements')
pow_axes[idx].xaxis_date()
pow_axes[idx].xaxis.set_major_formatter(DateFmt)
#pow_axes[idx].set_xlabel('Time')
pow_axes[idx].yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
pow_axes[idx].set_ylabel('Current (A)')
curr_xdata = []
curr_ydata = []
curr_line, = pow_axes[idx].plot(curr_xdata, curr_ydata, 'b-*')

idx = volt_idx
pow_axes[idx].set_title('Voltage Divider Measurements')
pow_axes[idx].xaxis_date()
pow_axes[idx].xaxis.set_major_formatter(DateFmt)
pow_axes[idx].set_xlabel('Time')
pow_axes[idx].yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
pow_axes[idx].set_ylabel('Voltage (V)')
volt_xdata = []
volt_ydata = []
volt_line, = pow_axes[idx].plot(volt_xdata, volt_ydata, 'r-o')

plt.tight_layout()

#import time
import datetime

def plot_current(data) :
	# data is a float
	idx = curr_idx
	curr_xdata.append(datetime.datetime.now())
	curr_ydata.append(data)
	curr_line.set_xdata(curr_xdata)
	curr_line.set_ydata(curr_ydata)
	pow_axes[curr_idx].relim()
	pow_axes[curr_idx].autoscale_view(False,True,True)
	plt.draw()
	plt.pause(1e-17)

def plot_voltage(data) :
	# data is a float
	idx = volt_idx
	volt_xdata.append(datetime.datetime.now())
	volt_ydata.append(data)
	volt_line.set_xdata(volt_xdata)
	volt_line.set_ydata(volt_ydata)
	pow_axes[idx].relim()
	pow_axes[idx].autoscale_view(False,True,True)
	plt.draw()
	plt.pause(1e-17)

def plot_update(data) :
	# data is an json object
	datestamp = datetime.datetime.now()
	idx = temp_idx
	temp_xdata.append(datestamp)
	temp_ydata.append(float(data['temperature']))
	temp_line.set_xdata(temp_xdata)
	temp_line.set_ydata(temp_ydata)
	imu_axes[idx].relim()
	imu_axes[idx].autoscale_view(False,True,True)
	idx = pres_idx
	pres_xdata.append(datestamp)
	pres_ydata.append(float(data['pressure']))
	pres_line.set_xdata(pres_xdata)
	pres_line.set_ydata(pres_ydata)
	imu_axes[idx].relim()
	imu_axes[idx].autoscale_view(False,True,True)
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
	elif (message.topic == "relayshield/measurement/voltage") :
		plot_voltage(float(message.payload.decode(encoding='UTF-8',errors='strict')))

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
