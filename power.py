import config_demo as config
import paho.mqtt.client as mqtt
from NCD_Definitions import NCDBase, Environmental
from gatewayutils import get_init_info, new_snsr,create_type_profile_instances, get_att, update_sns_obj, update_smip_hack, local_smip_update
import gatewayutils
import smiputils

mqtt_broker = config.mqtt["broker"]
mqtt_clientid = config.mqtt["clientprefix"] + "GW"
mqtt_topic = ""
master_sensor_dict ={}

sm_utils = smiputils.utils(config.smip["authenticator"], config.smip["password"], config.smip["name"], config.smip["role"], config.smip["url"], config.smip["verbose"])

def on_message(client, userdata, message):
	global master_sensor_dict
	msg = str(message.payload.decode("utf-8"))
	# print("Received MQTT message: " + msg)
	mcid, sntype, sntypenm, payload= get_init_info(msg)
	print(mcid)

	if new_snsr(mcid, payload,sntype):
		machinelist ={}
		
		machines = sm_utils.find_smip_equipment_of_type(config.smip["machine_id_dict"][str(sntype)])	
		if machines:
			for machine in machines:
				machinelist[machine["attributes"][0]["stringValue"]]=machine["id"]
				print (machine)

			if mcid in machinelist:
				print (mcid)
				get_att(machinelist[mcid], mcid, gatewayutils.master_sensor_dict[mcid])
				print("added online vars to local")
			else:
				new_mach =create_type_profile_instances(mcid,config.smip["machine_id_dict"][str(sntype)],mcid)
				get_att(new_mach,mcid,gatewayutils.master_sensor_dict[mcid])


		else:
		
			new_mach =create_type_profile_instances(mcid,config.smip["machine_id_dict"][str(sntype)],mcid)
			get_att(new_mach,mcid,gatewayutils.master_sensor_dict[mcid])
			#print(vars(gatewayutils.master_sensor_dict[mcid]))
	else:
		print("not new")
		print(mcid)
		#gatewayutils.master_sensor_dict[mcid] =payload
		update_sns_obj(gatewayutils.master_sensor_dict[mcid],payload)
		update_smip_hack(gatewayutils.master_sensor_dict[mcid])


# Starting MQTT
mqtt_client = mqtt.Client(mqtt_clientid)
mqtt_client.connect(mqtt_broker)
mqtt_client.subscribe('gateway/#')
mqtt_client.on_message = on_message
mqtt_client.loop_forever()
