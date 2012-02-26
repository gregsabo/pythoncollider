import time
import os, sys
import subprocess
import OSC

class SCLoader(object):

    def __init__(self):
        self.process = None
        
    def load(self): 
        path = os.path.dirname(sys.argv[0])
        path = os.path.dirname(__file__)

        os.system("/Applications/SuperCollider/sclang -d /Applications/SuperCollider/ " + path + '/synthdefs.sc')
        os.system("/Applications/SuperCollider/sclang -d /Applications/SuperCollider/ " + path + '/ugensynthdefs.sc')
        
        self.process = subprocess.Popen(["/Applications/SuperCollider/scsynth", "-u", "57110", '-a', '1024'], cwd="/Applications/SuperCollider")

        time.sleep(2)
    
    def stop(self):
        self.process.terminate()

SECONDS_FROM_1900_TO_1970 = 2208988800
def sc_time():
    return float(time.time()) + SECONDS_FROM_1900_TO_1970

sc_loader = SCLoader()
sc_loader.load()

client = OSC.OSCClient()
client.connect(('127.0.0.1', 57110))
