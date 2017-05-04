#!/usr/bin/env python3


# config file creator


from configobj import ConfigObj


config = ConfigObj()
config.filename = 'pythonMqttPlotter.cfg'


mqtt_configuration = {
	'MQTT_BROKER_IP'           : "192.168.1.52",
	'MQTT_BROKER_PORT'         : "1883",
	'MQTT_BROKER_PORT_TIMEOUT' : "60",
	}
config['mqtt_configuration'] = mqtt_configuration

config['mqtt_topics'] = {}
config['mqtt_topics']['TRACK_TOPICS'] = ['relaysheild/measurement/current', 'relaysheild/measurement/current']


config.write()
