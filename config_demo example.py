#!/usr/bin/env python
mqtt = {
    #"broker": "192.168.1.72",
    "broker":"127.0.0.1",
    "clientprefix": "CLIENT_PREFIX"
}


#parent you want the sensor to come show up under
#change dict values to match your instances


smip = {
    "authenticator": "",
    "password": "",
    "name": "",
    "role": "",
    "url": "https://yourinstance.cesmii.thinkiq.net/graphql",
    "machine_type": "ncd_env_sensor",
    
    "parent_equipment_id2": "72868",
    "parent_equipment_id": "72868",
    "verbose": False,
    
    "machine_name_dict":{"9":"NCD Light and Proximity Sensor","1":"NCD Temperature and Humidity Sensor", "2":"NCD Door Contact Sensor", "50":"NCD Predictive Maintenance Sensor"},
    "machine_type_dict":{"9":"ncd_light_prox_sensor","1":"ncd_temp_humid_sensor", "2":"ncd_door_sensor", "50":"ncd_predictive_maintenance_sensor","28":"ncd_3_channel_current_sensor"},
    "machine_id_dict":{"9":"72678","1":"72655", "2":"72671", "50":"72662", "28":"78517"}
}
