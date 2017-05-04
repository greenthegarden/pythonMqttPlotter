#!/usr/bin/env python3

#---------------------------------------------------------------------------------------
# Load configuration values
#
#---------------------------------------------------------------------------------------

# see https://wiki.python.org/moin/ConfigParserShootout
from configobj import ConfigObj
config = ConfigObj('/home/philip/Development/projects/python/pythonMqttPlotter/pythonMqttPlotter.cfg')

print("{0}".format("Python MQTT Track Plotter"))


import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.animation as animation

# fig1 = plt.figure()
# ax1 = fig.add_subplot(1,1,1)
#
# plt.xlim(0, 1)
# plt.ylim(0, 1)
# plt.xlabel('time')
# plt.ylabel('speed')
# plt.title('Speed')

# fig, ax = plt.subplots(1, 1)
# xdata, ydata = [], []
# ln, = plt.plot([], [], 'ro', animated=True)

# fig.plt.figure()
# ax = fig.add_subplot111
#
# def init():
#     ax.set_xlim(0, 1000)
#     ax.set_ylim(0, 200)
#     return ln,
#
# def update(ln):
# #	ln.set_xdata(numpy.append(h1.get_xdata(), new_data)
# #    xdata.append(frame)
# #    ydata.append(np.sin(frame))
#     ln.set_data(xdata, ydata)
#     return ln,
#
#
# h1, = plt.plot([], [], 'ro', animated=True)
#
# def update_line(h1, new_data) :
# 	print(new_data)
# 	h1.set_xdata(np.append(h1.get_xdata(), new_data))
# 	h1.set_ydata(np.append(h1.get_ydata(), new_data))
# #	plt.draw()
# 	fig.canvas.draw()

# creat arrays for altitude, speed and heading
#altitude = np.array([]).
#speed = np.array([])
#heading = np.array([])

xdata = []
ydata = []

plt.show()

#from math import pi

time = 0

axes = plt.gca()
#axes.autoscale(enable=True, axis='both', tight=None)
#axes.set_xlim(0, 100)
#axes.set_ylim(0, 1)
line, = axes.plot(xdata, ydata, 'r-')

def plot_update(data) :
	# data is an float
	print(data)
	global time
	time = time+1
	xdata.append(time)
	ydata.append(data)
	line.set_xdata(xdata)
	line.set_ydata(ydata)
	axes.relim()
	axes.autoscale_view(True,True,True)
	plt.draw()
	plt.pause(1e-17)

import sys
import getopt

#---------------------------------------------------------------------------------------
# Modules and methods to support MQTT
#
#---------------------------------------------------------------------------------------

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
	if (message.topic == "relayshield/measurement/current") :
		plot_update(float(message.payload.decode(encoding='UTF-8',errors='strict')))

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
