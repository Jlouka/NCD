import json
import config_demo as config
from NCD_Definitions import NCDBase, Environmental, ThreeChannel, Predictive
import smiputils
master_sensor_dict = {}

sm_utils = smiputils.utils(config.smip["authenticator"], config.smip["password"],
                           config.smip["name"], config.smip["role"], config.smip["url"], config.smip["verbose"])


def get_init_info(msg):
    dcmsg = json.loads(msg)  # msg is dict with MAC as key
    macid = list(dcmsg.keys())[0]  # getting the key
    sntype = dcmsg[macid].get("type")
    sntypenm = config.smip["machine_type_dict"][str(sntype)]
    # print(type(dcmsg))
    return macid, sntype, sntypenm, dcmsg[macid]


def create_type_profile_instances(mcid, sntypeid, equipname):

    sns_type_id = sntypeid
    parent = config.smip["parent_equipment_id"]
    #create if statements here if I want to place sensors in a diffetrent area
    # 
    # you can probably either Strip the colons out of the MCID or only use the last two numbers.
    #  



    new_machine = sm_utils.create_smip_equipment_of_typeid(
        parent, sns_type_id, equipname)

    mcid_smip_attr = ""
    mcid_smip = ""

    smip_attribs = sm_utils.find_attributes_of_equipment_id(new_machine)
    for attr in smip_attribs:
        # print(attr)
        if attr["relativeName"] == "macid":
            if attr["stringValue"] == None:
                mcid_smip_attr = attr["id"]
                # print(mcid_smip_attr)
                # print (mcid)
                sm_utils.update_cnfg_smip(mcid_smip_attr, str(mcid))
            if attr["stringValue"] != None:
                # print ("it aint none")
                mcid_smip = attr["stringValue"]
        else:
            continue
    # machines = sm_utils.find_smip_equipment_of_type(sns_type_nm)
    return new_machine


def get_att(new_machine, mcid, snsobj):
    smip_attribs = sm_utils.find_attributes_of_equipment_id(new_machine)

    for att in smip_attribs:

        if att["relativeName"] == "temperature":
            master_sensor_dict[mcid].temperature["id"] = att["id"]
        if att["relativeName"] == "humidity":  # _10298
            master_sensor_dict[mcid].humidity["id"] = att["id"]

        if att["relativeName"] == "channel_1_current":
            master_sensor_dict[mcid].channel_1_milliamps["id"] = att["id"]
        if att["relativeName"] == "channel_2_current":  # _10298
            master_sensor_dict[mcid].channel_2_milliamps["id"] = att["id"]
        if att["relativeName"] == "channel_3_current":  # _10298
            master_sensor_dict[mcid].channel_3_milliamps["id"] = att["id"]

        if att["relativeName"] == "vibrationxrms":
            master_sensor_dict[mcid].rms_x["id"] = att["id"]
        if att["relativeName"] == "vibrationyrms":  # _10298
            master_sensor_dict[mcid].rms_y["id"] = att["id"]
        if att["relativeName"] == "vibrationzrms":  # _10298
            master_sensor_dict[mcid].rms_z["id"] = att["id"]
        if att["relativeName"] == "current":  # _10298
            master_sensor_dict[mcid].Current["id"] = att["id"]

        if att["relativeName"] == "rssi":  # _10298
            master_sensor_dict[mcid].rssi["id"] = att["id"]
        if att["relativeName"] == "batterylevel":
            master_sensor_dict[mcid].battery_level["id"] = att["id"]
        if att["relativeName"] == "transmissioncount":
            master_sensor_dict[mcid].transmission_count["id"] = att["id"]
        else:
            continue


def update_smip_hack(obj):
    # common attr for ncd
    attributes = vars(obj)
    fbop = 0
    alias_mutates = ""
    for var_name, var_value in attributes.items():
        if var_name == "macid":
            continue
        fbop += 1
        alias_mutates += sm_utils.build_alias_ts_mutation(str(fbop), getattr(
            obj, var_name)["id"], getattr(obj, var_name)["value"]) + "\n"
    sm_utils.multi_tsmutate_aliases(alias_mutates)


def update_sns_obj(obj, payload):
    attributes = vars(obj)
    for var_name, var_value in attributes.items():
        if var_name == "macid":
            continue

        setattr(obj, var_name, {
                "value": payload[var_name], "id": var_value["id"]})

        # print(var_name)
        # print(f"payload value is {payload[var_name]}")
        # print (getattr(obj, var_name)["value"])


def local_smip_update(machines, mcid, sntype):
    global master_sensor_dict
    for machine in machines:
        if mcid ==machine["attributes"][0]["stringValue"]:
            get_att(new_mach, mcid, master_sensor_dict[mcid])
            print("added online vars to local")
        else:
            print("sensor not in dict")
            # print(machine["displayName"])
            # print(machine["id"])
            # print(machine["attributes"][0]["stringValue"])
            master_sensor_dict[mcid] = Environmental(mcid)
            new_mach = create_type_profile_instances(
                mcid, config.smip["machine_id_dict"][str(sntype)], mcid)
            get_att(new_mach, mcid, master_sensor_dict[mcid])


def new_snsr(mcid, payload, sntype):
    global master_sensor_list
    if mcid in master_sensor_dict:
        print("already exists")
        return 0
    else:
        if sntype == 1:
            master_sensor_dict[mcid] = Environmental(mcid)
            print("created new sensor")
        if sntype == 28:
            master_sensor_dict[mcid] = ThreeChannel(mcid)
            print("created new sensor")
        if sntype == 50:
            master_sensor_dict[mcid] = Predictive(mcid)
            print("created new sensor")
        return 1
