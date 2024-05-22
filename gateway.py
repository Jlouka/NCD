#!/usr/bin/python3

import config_demo as config   #copy config-example.py to config.py and set values
import paho.mqtt.client as mqtt
import json
import smiputils
import math
import time
from datetime import datetime

mqtt_broker = config.mqtt["broker"]
mqtt_clientid = config.mqtt["clientprefix"] + "GW"
mqtt_topic = ""			#This should be enumerated, not hard coded
#print (f"Listening for MQTT messages on topic: {mqtt_topic} ...")

sensor_dict ={}
attr_id_value = {}

sm_utils = smiputils.utils(config.smip["authenticator"], config.smip["password"], config.smip["name"], config.smip["role"], config.smip["url"], config.smip["verbose"])

def on_message(client, userdata, message):
	msg = str(message.payload.decode("utf-8"))
	#print("Received MQTT message: " + msg)
	mcid,dcmsg =get_mac(msg)

	if new_snsr(mcid):
		#dcmsg = json.loads(msg)
		sensor_dict[mcid] =dcmsg[mcid]
		sns_type = snsr_type(msg,mcid)
		sns_type_nm =config.smip["machine_type_dict"][str(sns_type)]
		sns_nm =config.smip["machine_name_dict"][str(sns_type)]
		exists = check_type_profile_instances(msg,mcid,sns_type,sns_type_nm)
		#print(exists[0])
		if exists[0]==0:
			new_mach =create_type_profile_instances(msg,mcid,sns_type,sns_nm)
			get_att(new_mach, mcid)
			print("new mach added")
		else:
			get_att(exists[2], mcid)
			#print("not new sensor to local dict")
	else:

		print("Machine Updated at" + str(time.localtime()))
		#dcmsg = json.loads(msg)
		sensor_dict[mcid] =dcmsg[mcid]
		update_smip_hack (sensor_dict,attr_id_value, mcid)

def snsr_type(msg,mcid):
	#print (sensor_dict[mcid]['type'])
	return sensor_dict[mcid]['type']

def update_smip_hack (sensor_dict,attr_id_value, mcid):
			#common attr for ncd
	
	fbatch = ["rssi","battery_level", "transmission_count"]
	fbop = 0
	alias_mutates = ""
	for i in fbatch:
		fbop +=1
		alias_mutates += sm_utils.build_alias_ts_mutation(str(fbop), attr_id_value[mcid][i], sensor_dict[mcid][i]) + "\n"
	sm_utils.multi_tsmutate_aliases(alias_mutates)
		



	if sensor_dict[mcid]['type'] == 1:
		#print ("temp is " + str(sensor_dict[mcid]['temperature']) )
		#print ("humidity is " + str(sensor_dict[mcid]['humidity']) )

		fbatch2 = ["temperature","humidity"]
		fbop2 = 0
		alias_mutates2 = ""
		for i in fbatch2:
			fbop2 +=1
			alias_mutates2 += sm_utils.build_alias_ts_mutation(str(fbop2), attr_id_value[mcid][i], sensor_dict[mcid][i]) + "\n"
		sm_utils.multi_tsmutate_aliases(alias_mutates2)


		
	if sensor_dict[mcid]['type'] == 50:

		fbatch4 = ["vibrationxrms","vibrationyrms","vibrationzrms"]
		fbatch44= ["rms_x","rms_y","rms_z"]
		fbop4 = 0
		alias_mutates4 = ""
		for i,j in zip(fbatch4,fbatch44):
			fbop4 +=1
			alias_mutates4 += sm_utils.build_alias_ts_mutation(str(fbop4), attr_id_value[mcid][i], sensor_dict[mcid][j]) + "\n"
		sm_utils.multi_tsmutate_aliases(alias_mutates4)

		
		
		write_attribute_id=attr_id_value[mcid]["current"]
		value_send=math.sqrt(sensor_dict[mcid]['rms_y'])
		sm_utils.update_smip(write_attribute_id,value_send)

	if sensor_dict[mcid]['type'] == 9:

		fbatch3 = ["proximity","lux"]
		fbop3 = 0
		alias_mutates3 = ""
		for i in fbatch3:
			fbop3 +=1
			alias_mutates3 += sm_utils.build_alias_ts_mutation(str(fbop3), attr_id_value[mcid][i], sensor_dict[mcid][i]) + "\n"
		sm_utils.multi_tsmutate_aliases(alias_mutates3)
		

	if sensor_dict[mcid]['type'] == 2:
		#print ("door 1 is " + str(sensor_dict[mcid]['input_1']) )
		print ("door 2 is " + str(sensor_dict[mcid]['input_2']) )

		if sensor_dict[mcid]['input_2']==0:
			write_attribute_id=attr_id_value[mcid]["door_2"]
			value_send="False"
			sm_utils.update_smip(write_attribute_id,value_send)
			
		if sensor_dict[mcid]['input_1']==0:
			write_attribute_id=attr_id_value[mcid]["door_1"]
			value_send="False"
			sm_utils.update_smip(write_attribute_id,value_send)

		if sensor_dict[mcid]['input_2']==1:
			write_attribute_id=attr_id_value[mcid]["door_2"]
			value_send="True"
			sm_utils.update_smip(write_attribute_id,value_send)
			
		if sensor_dict[mcid]['input_1']==1:
			write_attribute_id=attr_id_value[mcid]["door_1"]
			value_send="True"
			sm_utils.update_smip(write_attribute_id,value_send)

def get_mac(msg):
	dcmsg = json.loads(msg) #msg is dict with MAC as key
	key = list(dcmsg.keys())  #getting the key
	#print (key[0])			#accessing the key element
	inr_msg_key =str(key[0])
	return inr_msg_key, dcmsg

#check if sensor exists in local dictionary 
def new_snsr(mcid):
	if mcid not in sensor_dict:
		#print("Adding new sensor")
		return 1
	else :
		return 0

#sensor type used here with name command
def check_type_profile_instances(msg,mcid,sns_type,sns_type_nm):
	machine_exists=0

	machines = sm_utils.find_smip_equipment_of_type(sns_type_nm)
	#print("printing machines")
	#print(machines)
	existing_machine_id = 0
	if not machines:
		machine_exists=0
	else:
		print("found some of this type")
		machine_exists=1
		#get single id, needs to update for multiple
		existing_machine_id = machines[0]['id']

	return machine_exists, machines, existing_machine_id

#sensor type used here again with name command
def create_type_profile_instances(msg,mcid,sns_type,sns_type_nm):
	
	sns_type_id =config.smip["machine_id_dict"][str(sns_type)]
	parent= config.smip["parent_equipment_id"]

	new_machine = sm_utils.create_smip_equipment_of_typeid(parent, sns_type_id, sns_type_nm )

	mcid_smip_attr =""
	mcid_smip=""

	smip_attribs = sm_utils.find_attributes_of_equipment_id(new_machine)
	for attr in smip_attribs:
		#print(attr)
		if attr["relativeName"]=="macid":
			if attr["stringValue"] ==None:
				mcid_smip_attr = attr["id"]
				#print(mcid_smip_attr)
				print (mcid)
				sm_utils.update_cnfg_smip(mcid_smip_attr,str(mcid))
			if attr["stringValue"] != None:
				#print ("it aint none")
				mcid_smip = attr["stringValue"]
		else:
			continue
	#machines = sm_utils.find_smip_equipment_of_type(sns_type_nm)
	return new_machine

#nested dict to hold MACID, attr value and attr id ?

def get_att(new_machine, mcid):
	smip_attribs = sm_utils.find_attributes_of_equipment_id(new_machine)
	attr_id_value[mcid] = {}
	for att in smip_attribs:
		if att["relativeName"]== "lux":
			attr_id_value[mcid]["lux"] =att["id"]
		if att["relativeName"]== "proximity":
			attr_id_value[mcid]["proximity"] =att["id"]
		if att["relativeName"]== "temperature":
			attr_id_value[mcid]["temperature"] =att["id"]
		if att["relativeName"]== "humidity": #_10298
			attr_id_value[mcid]["humidity"] =att["id"]
		if att["relativeName"]== "door_1":
			attr_id_value[mcid]["door_1"] =att["id"]
		if att["relativeName"]== "door_2":
			attr_id_value[mcid]["door_2"] =att["id"]

		if att["relativeName"]== "vibrationxrms":
			attr_id_value[mcid]["vibrationxrms"] =att["id"]
		if att["relativeName"]== "vibrationyrms":
			attr_id_value[mcid]["vibrationyrms"] =att["id"]
		if att["relativeName"]== "vibrationzrms":
			attr_id_value[mcid]["vibrationzrms"] =att["id"]
		if att["relativeName"]== "current":
			attr_id_value[mcid]["current"] =att["id"]

		if att["relativeName"]== "rssi": #_10298
			attr_id_value[mcid]["rssi"] =att["id"]
		if att["relativeName"]== "batterylevel":
			attr_id_value[mcid]["battery_level"] =att["id"]
		if att["relativeName"]== "transmissioncount":
			attr_id_value[mcid]["transmission_count"] =att["id"]
		else:
			continue
	
mqtt_client = mqtt.Client(mqtt_clientid)
mqtt_client.connect(mqtt_broker)

mqtt_client.subscribe('gateway/#')
mqtt_client.on_message=on_message
mqtt_client.loop_forever()


