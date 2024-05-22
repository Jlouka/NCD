class NCDBase:
    def __init__(self, macid):
        self.macid = {"value":macid, "id":879}
        self.battery_level = {"value": 3.2 , "id": 234}
        #self.firmare_version = {"value": 10 , "id": 234}
        self.transmission_count = {"value": 10 , "id": 234}
        #self.type = {"value": 10 , "id": 234}
        #self.node_id= {"value": 10 , "id": 234}
        self.rssi= {"value": 10 , "id": 234}

    
    def update(self):
        print ("updated")
        
        
class Environmental(NCDBase):
    def __init__(self, macid):
        NCDBase.__init__(self,macid)
        #self.type["value"]= type
        self.temperature = {"value": 10 , "id": 234}
        self.humidity = {"value": 10 , "id": 234}

    
class ThreeChannel(NCDBase):
    def __init__(self, macid):
        NCDBase.__init__(self,macid)
        self.type= type
        self.channel_1_milliamps = {"value": 10 , "id": 234}
        self.channel_2_milliamps = {"value": 10 , "id": 234}
        self.channel_3_milliamps = {"value": 10 , "id": 234}

class Predictive(NCDBase):
    def __init__(self, macid):
        NCDBase.__init__(self, macid)
        self.type= type
        self.rms_x = {"value": 10 , "id": 234}
        self.rms_y = {"value": 10 , "id": 234}
        self.rms_z = {"value": 10 , "id": 234}
        self.Current = {"value": 10 , "id": 234}
        

class Predictivev3(NCDBase):
    def __init__(self, macid):
        NCDBase.__init__(self, macid)
        self.type= type
        self.x_rms_ACC_mg = {"value": 10 , "id": 234}
        self.y_rms_ACC_mg = {"value": 10 , "id": 234}
        self.z_rms_ACC_mg = {"value": 10 , "id": 234}
        self.Current = {"value": 10 , "id": 234}
        
      