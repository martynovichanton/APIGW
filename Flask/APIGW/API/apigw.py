import requests
from flask import Flask
from flask import json
from flask import request
from flask import jsonify
from flask_cors import CORS
from flask_restful import Resource, Api
import time
import os
import sys
from F5 import F5
from Forti import Forti
from Crypto import Crypto
from getpass import getpass
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)
api = Api(app)
CORS(app)


f = open('config.py','r')
config = json.load(f)
f.close()
print(json.dumps(config, indent=4, sort_keys=False))

port = 443

# multithreading is for each device for all commands
# the commands are multithreaded
def iterate(folder, token, RUN_MULTITHREADING=False):
    mainDir = folder
    print(f"[*] {mainDir}")
    mainCrypto = Crypto()
    port = 443
    device_token = mainCrypto.encrypt_random_key(token)
    
    dataset = []

    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    outputDir = "output" + "-" + now
    if not os.path.exists(f"{mainDir}/{outputDir}"):
        os.mkdir(f"{mainDir}/{outputDir}")
    
    logFile = open(f"{mainDir}/{outputDir}/log.txt", "w")
    logFile.write(f"[*] {mainDir}" + "\n")

    for dir in os.listdir(f"{mainDir}/api"):
        print(f"[*] {dir}")
        logFile.write(f"[*] {dir}" + "\n")
        
        commandsFile = open(f"{mainDir}/api/{dir}/commands.txt", 'r')
        devicesFile = open(f"{mainDir}/api/{dir}/devices.txt", 'r')
        commands = commandsFile.read().splitlines()
        devices = devicesFile.read().splitlines()
        commandsFile.close()
        devicesFile.close()

        print(f"[*] Devices: {devices}")
        print(f"[*] Commands to run: {commands}")
        logFile.write(f"[*] Devices: {devices}" + "\n")
        logFile.write(f"[*] Commands to run: {commands}" + "\n")

        if dir == 'f5' or dir == 'f501' or dir == 'f502':    
            token = device_token

        if dir == 'forti' or dir == 'forti01' or dir == 'forti02':    
            token = device_token

        for device in devices:
            outFilePerDevice = open(f"{mainDir}/{outputDir}/{device}.txt", "w")
            print (f"[*] {device}")
            logFile.write(f"[*] {device}" + "\n")
            
            if dir == 'f5' or dir == 'f501' or dir == 'f502':
                api = F5(device, port, mainCrypto.decrypt_random_key(token))
            
            if dir == 'forti' or dir == 'forti01' or dir == 'forti02':    
                api = Forti(device, port, mainCrypto.decrypt_random_key(token))


            if RUN_MULTITHREADING:
                #parallel threads per device for all commands
                with ThreadPoolExecutor(max_workers=10) as executor:
                    future_list = []
                    for command in commands:
                        time.sleep(api.sleepTimeCommand)
                        future = executor.submit(api.runCommand, command)
                        future_list.append(future)
                    for f in as_completed(future_list):
                        out = f.result()
                        dataset.append(out)

                        print(json.dumps(out))
                        outFilePerDevice.write(json.dumps(out) + "\n")
            else:
                for command in commands:
                    time.sleep(api.sleepTimeCommand)
                    out = api.runCommand(command)

                    dataset.append(out)

                    print(json.dumps(out))
                    outFilePerDevice.write(json.dumps(out) + "\n")

            outFilePerDevice.close()  
                
    print("\n[*] DONE!\n")
    logFile.write("\n[*] DONE!\n")
    logFile.close()
    
    return {"dataset":dataset}


#########################################################################################
######## F5
#########################################################################################

class IndexF5(Resource):
    def get(self):
        index = {
            "Options":[
                "/f5api/F5_SITE1_GET_TOKEN GET -H password -H user",
                "/f5api/F5_SITE2_GET_TOKEN GET -H password -H user",
                "/f5api/F5_SITE3_GET_TOKEN GET -H password -H user",
                "/f5api/F5_SITE1_commands1 PATCH -H token",
                "/f5api/F5_SITE1_commands2 PATCH -H token",
                "/f5api/F5_SITE1_show_stats GET -H token",
                "/f5api/F5_SITE1_show_config GET -H token",
                "/f5api/F5_SITE2_commands1 PATCH -H token",
                "/f5api/F5_SITE2_commands2 PATCH -H token",
                "/f5api/F5_SITE2_show_stats GET -H token",
                "/f5api/F5_SITE2_show_config GET -H token",
                "/f5api/F5_SITE3_commands1 PATCH -H token",
                "/f5api/F5_SITE3_commands2 PATCH -H token",
                "/f5api/F5_SITE3_show_stats GET -H token",
                "/f5api/F5_SITE3_show_config GET -H token",
            ]
        }
        return index

class IndexForti(Resource):
    def get(self):
        index = {
            "Options":[
                "/fortiapi/FORTI_SITE1_GET_TOKEN POST -H password -H user",
                "/fortiapi/FORTI_SITE2_GET_TOKEN POST -H password -H user",
                "/fortiapi/FORTI_SITE1_ADD_TO_WHITELIST POST -H token -H memberlist -H whitelist -H nameprefix",
                "/fortiapi/FORTI_SITE1_REMOVE_FROM_WHITELIST POST -H token -H memberlist -H whitelist",
                "/fortiapi/FORTI_SITE1_GET_POLICY_PKG_STATUS POST -H token",
                "/fortiapi/FORTI_SITE1_GET_INSTALL_PREVIEW POST -H token",
                "/fortiapi/FORTI_SITE1_INSTALL_POLICY_ALL POST -H token",
                "/fortiapi/FORTI_SITE2_ADD_TO_WHITELIST POST -H token -H memberlist -H whitelist -H nameprefix",
                "/fortiapi/FORTI_SITE2_REMOVE_FROM_WHITELIST POST -H token -H memberlist -H whitelist",
                "/fortiapi/FORTI_SITE2_GET_POLICY_PKG_STATUS POST -H token",
                "/fortiapi/FORTI_SITE2_GET_INSTALL_PREVIEW POST -H token",
                "/fortiapi/FORTI_SITE2_INSTALL_POLICY_ALL POST -H token"
            ]
        }
        return index

class F5Site1GetToken(Resource):
    def get(self):
        if request.headers['Content-Type'] == 'application/json' and 'user' in request.headers and 'password' in request.headers:
            try:
                f5 = F5(config["site1"]["lb_site1_f502"], port, "")
                data = f5.token(request.headers['user'], request.headers['password'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400

class F5Site2GetToken(Resource):
    def get(self):
        if request.headers['Content-Type'] == 'application/json' and 'user' in request.headers and 'password' in request.headers:
            try:
                f5 = F5(config["site2"]["lb_site2_f502"], port, "")
                data = f5.token(request.headers['user'], request.headers['password'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400

class F5Site3GetToken(Resource):
    def get(self):
        if request.headers['Content-Type'] == 'application/json' and 'user' in request.headers and 'password' in request.headers:
            try:
                f5 = F5(config["site3"]["lb_site3_f502"], port, "")
                data = f5.token(request.headers['user'], request.headers['password'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400

class F5Commands(Resource):
    def get(self, command):
        allowed_commands = [
            "F5_SITE1_show_stats",
            "F5_SITE1_show_config",
            "F5_SITE2_show_stats",
            "F5_SITE2_show_config",
            "F5_SITE3_show_stats",
            "F5_SITE3_show_config",
        ]

        if command not in allowed_commands:
            return {"Error":"Bad URL"}, 400

        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                data = iterate(f"Actions/{command}", request.headers['token'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400
    
    def patch(self, command):
        allowed_commands = [
            "F5_SITE1_commands1",
            "F5_SITE1_commands2",
            "F5_SITE2_commands1",
            "F5_SITE2_commands2",
            "F5_SITE3_commands1",
            "F5_SITE3_commands2"
        ]

        if command not in allowed_commands:
            return {"Error":"Bad URL"}, 400

        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                data = iterate(f"Actions/{command}", request.headers['token'], RUN_MULTITHREADING=True)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400


api.add_resource(IndexF5, '/f5api/')
api.add_resource(F5Site1GetToken, '/f5api/F5_SITE1_GET_TOKEN')
api.add_resource(F5Site2GetToken, '/f5api/F5_SITE2_GET_TOKEN')
api.add_resource(F5Site3GetToken, '/f5api/F5_SITE3_GET_TOKEN')
api.add_resource(F5Commands, '/f5api/<command>')


#########################################################################################
######## Forti
#########################################################################################

class FortiSite1GetToken(Resource):
    def post(self):
        if request.headers['Content-Type'] == 'application/json' and 'user' in request.json and 'password' in request.json:
            try:
                forti = Forti(config["site1"]["srv_site1_fwmgmt1"], port, "")
                data = forti.token(request.json['user'], request.json['password'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400

class FortiSite2GetToken(Resource):
    def post(self):
        if request.headers['Content-Type'] == 'application/json' and 'user' in request.json and 'password' in request.json:
            try:
                forti = Forti(config["site2"]["srv_site2_fwmgmt1"], port, "")
                data = forti.token(request.json['user'], request.json['password'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400

class FortiSite1AddToWhitelist(Resource):
    def post(self):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.json and 'memberlist' in request.json and 'whitelist' in request.json and 'nameprefix' in request.json:
            try:
                if len(request.json['token']) == 0 or len(request.json['memberlist']) == 0 or len(request.json['whitelist']) == 0:
                    return {"Error":"Incorrect data"}, 200
                adom = "root"
                actions_dir = "Actions/FORTI_SITE1_ADD_TO_WHITELIST"
                forti = Forti(config["site1"]["srv_site1_fwmgmt1"], port, request.json['token'])
                data = forti.whitelist(request.json['memberlist'], request.json['whitelist'], request.json['nameprefix'], adom, actions_dir)
                data = iterate(actions_dir, request.json['token'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400

class FortiSite1RemoveFromWhitelist(Resource):
    def post(self):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.json and 'memberlist' in request.json and 'whitelist' in request.json:
            try:
                if len(request.json['token']) == 0 or len(request.json['memberlist']) == 0 or len(request.json['whitelist']) == 0:
                    return {"Error":"Incorrect data"}, 200
                adom = "root"
                actions_dir = "Actions/FORTI_SITE1_REMOVE_FROM_WHITELIST"
                forti = Forti(config["site1"]["srv_site1_fwmgmt1"], port, request.json['token'])
                data = forti.remove_from_whitelist(request.json['memberlist'], request.json['whitelist'], adom, actions_dir)
                data = iterate(actions_dir, request.json['token'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400

class FortiSite1GetPolicyPkgStatus(Resource):
    def post(self):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.json:
            try:
                adom = "root"
                forti = Forti(config["site1"]["srv_site1_fwmgmt1"], port, request.json['token'])
                data = forti.get_policy_pkg_status(adom)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400
    
class FortiSite1GetInstallPreview(Resource):
    def post(self):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.json:
            try:
                adom = "root"
                forti = Forti(config["site1"]["srv_site1_fwmgmt1"], port, request.json['token'])
                data = forti.get_install_preview(adom)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400

class FortiSite1InstallPolicyAll(Resource):
    def post(self):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.json:
            try:
                adom = "root"
                forti = Forti(config["site1"]["srv_site1_fwmgmt1"], port, request.json['token'])
                data = forti.install_policy_all(adom)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400

##############################################################################################

class FortiSite2AddToWhitelist(Resource):
    def post(self):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.json and 'memberlist' in request.json and 'whitelist' in request.json and 'nameprefix' in request.json:
            try:
                if len(request.json['token']) == 0 or len(request.json['memberlist']) == 0 or len(request.json['whitelist']) == 0:
                    return {"Error":"Incorrect data"}, 200
                adom = "root"
                actions_dir = "Actions/FORTI_SITE2_ADD_TO_WHITELIST"
                forti = Forti(config["site2"]["srv_site2_fwmgmt1"], port, request.json['token'])
                data = forti.whitelist(request.json['memberlist'], request.json['whitelist'], request.json['nameprefix'], adom, actions_dir)
                data = iterate(actions_dir, request.json['token'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400

class FortiSite2RemoveFromWhitelist(Resource):
    def post(self):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.json and 'memberlist' in request.json and 'whitelist' in request.json:
            try:
                if len(request.json['token']) == 0 or len(request.json['memberlist']) == 0 or len(request.json['whitelist']) == 0:
                    return {"Error":"Incorrect data"}, 200
                adom = "root"
                actions_dir = "Actions/FORTI_SITE2_REMOVE_FROM_WHITELIST"
                forti = Forti(config["site2"]["srv_site2_fwmgmt1"], port, request.json['token'])
                data = forti.remove_from_whitelist(request.json['memberlist'], request.json['whitelist'], adom, actions_dir)
                data = iterate(actions_dir, request.json['token'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400

class FortiSite2GetPolicyPkgStatus(Resource):
    def post(self):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.json:
            try:
                adom = "root"
                forti = Forti(config["site2"]["srv_site2_fwmgmt1"], port, request.json['token'])
                data = forti.get_policy_pkg_status(adom)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400

class FortiSite2GetInstallPreview(Resource):
    def post(self):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.json:
            try:
                adom = "root"
                forti = Forti(config["site2"]["srv_site2_fwmgmt1"], port, request.json['token'])
                data = forti.get_install_preview(adom)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400

class FortiSite2InstallPolicyAll(Resource):
    def post(self):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.json:
            try:
                adom = "root"
                forti = Forti(config["site2"]["srv_site2_fwmgmt1"], port, request.json['token'])
                data = forti.install_policy_all(adom)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {"Error":"Bad request"}, 400
            return data
        else:
            return {"Error":"Bad request"}, 400


api.add_resource(IndexForti, '/fortiapi/')
api.add_resource(FortiSite1GetToken, '/fortiapi/FORTI_SITE1_GET_TOKEN')
api.add_resource(FortiSite2GetToken, '/fortiapi/FORTI_SITE2_GET_TOKEN')

api.add_resource(FortiSite1AddToWhitelist, '/fortiapi/FORTI_SITE1_ADD_TO_WHITELIST')
api.add_resource(FortiSite1RemoveFromWhitelist, '/fortiapi/FORTI_SITE1_REMOVE_FROM_WHITELIST')
api.add_resource(FortiSite1GetPolicyPkgStatus, '/fortiapi/FORTI_SITE1_GET_POLICY_PKG_STATUS')
api.add_resource(FortiSite1GetInstallPreview, '/fortiapi/FORTI_SITE1_GET_INSTALL_PREVIEW')
api.add_resource(FortiSite1InstallPolicyAll, '/fortiapi/FORTI_SITE1_INSTALL_POLICY_ALL')

api.add_resource(FortiSite2AddToWhitelist, '/fortiapi/FORTI_SITE2_ADD_TO_WHITELIST')
api.add_resource(FortiSite2RemoveFromWhitelist, '/fortiapi/FORTI_SITE2_REMOVE_FROM_WHITELIST')
api.add_resource(FortiSite2GetPolicyPkgStatus, '/fortiapi/FORTI_SITE2_GET_POLICY_PKG_STATUS')
api.add_resource(FortiSite2GetInstallPreview, '/fortiapi/FORTI_SITE2_GET_INSTALL_PREVIEW')
api.add_resource(FortiSite2InstallPolicyAll, '/fortiapi/FORTI_SITE2_INSTALL_POLICY_ALL')


if __name__ == '__main__':
    app.run()