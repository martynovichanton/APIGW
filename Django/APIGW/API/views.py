from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

import requests
import json
import time
import os
import sys
from .F5 import F5
from .Forti import Forti
from .Crypto import Crypto
from getpass import getpass
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from concurrent.futures import ThreadPoolExecutor, as_completed

from .update_f5_commands import f5_site1_update_commands, f5_site2_update_commands


f = open('API/config.py','r')
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

class IndexF5(View):
    def get(self, request):
        index = {
            "Options":[
                "/f5api/F5_SITE1_GET_TOKEN GET -H password -H user",
                "/f5api/F5_SITE2_GET_TOKEN GET -H password -H user",
                "/f5api/F5_SITE1_TEST_SWITCH_SITE1_TO_SITE2 PATCH -H token",
                "/f5api/F5_SITE1_TEST_SWITCH_SITE2_TO_SITE1 PATCH -H token",
                "/f5api/F5_SITE1_TEST_ENABLE_SITE1 PATCH -H token",
                "/f5api/F5_SITE1_TEST_ENABLE_SITE2 PATCH -H token",
                "/f5api/F5_SITE1_TEST_FORCEOFFLINE_SITE1 PATCH -H token",
                "/f5api/F5_SITE1_TEST_FORCEOFFLINE_SITE2 PATCH -H token",
                "/f5api/F5_SITE1_ADD_TO_POOL PATCH -H token",
                "/f5api/F5_SITE1_REMOVE_FROM_POOL PATCH -H token",
                "/f5api/F5_SITE1_show_stats GET -H token",
                "/f5api/F5_SITE1_show_config GET -H token",
                "/f5api/F5_SITE2_TEST_SWITCH_SITE1_TO_SITE2 PATCH -H token",
                "/f5api/F5_SITE2_TEST_SWITCH_SITE2_TO_SITE1 PATCH -H token",
                "/f5api/F5_SITE2_TEST_ENABLE_SITE1 PATCH -H token",
                "/f5api/F5_SITE2_TEST_ENABLE_SITE2 PATCH -H token",
                "/f5api/F5_SITE2_TEST_FORCEOFFLINE_SITE1 PATCH -H token",
                "/f5api/F5_SITE2_TEST_FORCEOFFLINE_SITE2 PATCH -H token",
                "/f5api/F5_SITE2_ADD_TO_POOL PATCH -H token",
                "/f5api/F5_SITE2_REMOVE_FROM_POOL PATCH -H token"
                "/f5api/F5_SITE2_show_stats GET -H token",
                "/f5api/F5_SITE2_show_config GET -H token"
            ]
        }
        return JsonResponse(index)

class IndexForti(View):
    def get(self, request):
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
        return JsonResponse(index)

class F5Site1GetToken(View):
    def get(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'user' in request.headers and 'password' in request.headers:
            try:
                f5 = F5(config["site1"]["lb_site1_f502"], port, "")
                data = f5.token(request.headers['user'], request.headers['password'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

class F5Site2GetToken(View):
    def get(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'user' in request.headers and 'password' in request.headers:
            try:
                f5 = F5(config["site2"]["lb_site2_f502"], port, "")
                data = f5.token(request.headers['user'], request.headers['password'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class F5Commands(View):
    def get(self, request, command):
        allowed_commands = [
            "F5_SITE1_show_stats",
            "F5_SITE1_show_config",
            "F5_SITE2_show_stats",
            "F5_SITE2_show_config"
        ]

        if command not in allowed_commands:
            return JsonResponse({"Error":"Bad URL"}, status=400)

        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                data = iterate(f"API/Actions/{command}", request.headers['token'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)
    
    def patch(self, request, command):
        allowed_commands = [
            "F5_SITE1_TEST_SWITCH_SITE1_TO_SITE2",
            "F5_SITE1_TEST_SWITCH_SITE2_TO_SITE1",
            "F5_SITE1_TEST_ENABLE_SITE1",
            "F5_SITE1_TEST_ENABLE_SITE2",
            "F5_SITE1_TEST_FORCEOFFLINE_SITE1",
            "F5_SITE1_TEST_FORCEOFFLINE_SITE2",
            "F5_SITE1_ADD_TO_POOL",
            "F5_SITE1_REMOVE_FROM_POOL",
            "F5_SITE2_TEST_SWITCH_SITE1_TO_SITE2",
            "F5_SITE2_TEST_SWITCH_SITE2_TO_SITE1",
            "F5_SITE2_TEST_ENABLE_SITE1",
            "F5_SITE2_TEST_ENABLE_SITE2",
            "F5_SITE2_TEST_FORCEOFFLINE_SITE1",
            "F5_SITE2_TEST_FORCEOFFLINE_SITE2",
            "F5_SITE2_ADD_TO_POOL",
            "F5_SITE2_REMOVE_FROM_POOL"
        ]

        if command not in allowed_commands:
            return JsonResponse({"Error":"Bad URL"}, status=400)

        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                data = iterate(f"API/Actions/{command}", request.headers['token'], RUN_MULTITHREADING=True)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

class F5Site1Pools(View):
    def get(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                f5 = F5(config["site1"]["lb_site1_f502"], port, request.headers['token'])
                data = f5.pools()
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

class F5Site1PoolMembers(View):
    def get(self, request, pool_name):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                f5 = F5(config["site1"]["lb_site1_f502"], port, request.headers['token'])
                data = f5.pool_members(pool_name)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)
        
class F5Site1PoolMembersStats(View):
    def get(self, request, pool_name):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                f5 = F5(config["site1"]["lb_site1_f502"], port, request.headers['token'])
                data = f5.pool_members_stats(pool_name)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class F5Site1DisablePoolMember(View):
    def patch(self, request, pool_name, member_name):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                f5 = F5(config["site1"]["lb_site1_f502"], port, request.headers['token'])
                data = f5.disable_pool_member(pool_name, member_name)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)
        
@method_decorator(csrf_exempt, name='dispatch')
class F5Site1EnablePoolMember(View):
    def patch(self, request, pool_name, member_name):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                f5 = F5(config["site1"]["lb_site1_f502"], port, request.headers['token'])
                data = f5.enable_pool_member(pool_name, member_name)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class F5Site1AddToPool(View):
    def patch(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers and 'memberlist' in json.loads(request.body) and 'pools' in json.loads(request.body):
            try:
                if len(json.loads(request.body)['memberlist']) == 0 or len(json.loads(request.body)['pools']) == 0:
                    return JsonResponse({"Error":"Incorrect data"}, status=200)
                actions_dir = "API/Actions/F5_SITE1_ADD_TO_POOL"
                f5 = F5(config["site1"]["lb_site1_f502"], port, request.headers['token'])
                data = f5.add_to_pools(json.loads(request.body)['memberlist'], json.loads(request.body)['pools'], actions_dir)
                data = iterate(actions_dir, request.headers['token'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class F5Site1RemoveFromPool(View):
    def patch(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers and 'memberlist' in json.loads(request.body) and 'pools' in json.loads(request.body):
            try:
                if len(json.loads(request.body)['memberlist']) == 0 or len(json.loads(request.body)['pools']) == 0:
                    return JsonResponse({"Error":"Incorrect data"}, status=200)
                actions_dir = "API/Actions/F5_SITE1_REMOVE_FROM_POOL"
                f5 = F5(config["site1"]["lb_site1_f502"], port, request.headers['token'])
                data = f5.remove_from_pools(json.loads(request.body)['memberlist'], json.loads(request.body)['pools'], actions_dir)
                data = iterate(actions_dir, request.headers['token'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)
        
class F5Site2Pools(View):
    def get(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                f5 = F5(config["site2"]["lb_site2_f502"], port, request.headers['token'])
                data = f5.pools()
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

class F5Site2PoolMembers(View):
    def get(self, request, pool_name):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                f5 = F5(config["site2"]["lb_site2_f502"], port, request.headers['token'])
                data = f5.pool_members(pool_name)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)
        
class F5Site2PoolMembersStats(View):
    def get(self, request, pool_name):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                f5 = F5(config["site2"]["lb_site2_f502"], port, request.headers['token'])
                data = f5.pool_members_stats(pool_name)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class F5Site2DisablePoolMember(View):
    def patch(self, request, pool_name, member_name):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                f5 = F5(config["site2"]["lb_site2_f502"], port, request.headers['token'])
                data = f5.disable_pool_member(pool_name, member_name)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)
        
@method_decorator(csrf_exempt, name='dispatch')
class F5Site2EnablePoolMember(View):
    def patch(self, request, pool_name, member_name):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                f5 = F5(config["site2"]["lb_site2_f502"], port, request.headers['token'])
                data = f5.enable_pool_member(pool_name, member_name)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class F5Site2AddToPool(View):
    def patch(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers and 'memberlist' in json.loads(request.body) and 'pools' in json.loads(request.body):
            try:
                if len(json.loads(request.body)['memberlist']) == 0 or len(json.loads(request.body)['pools']) == 0:
                    return JsonResponse({"Error":"Incorrect data"}, status=200)
                actions_dir = "API/Actions/F5_SITE2_ADD_TO_POOL"
                f5 = F5(config["site2"]["lb_site2_f502"], port, request.headers['token'])
                data = f5.add_to_pools(json.loads(request.body)['memberlist'], json.loads(request.body)['pools'], actions_dir)
                data = iterate(actions_dir, request.headers['token'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class F5Site2RemoveFromPool(View):
    def patch(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers and 'memberlist' in json.loads(request.body) and 'pools' in json.loads(request.body):
            try:
                if len(json.loads(request.body)['memberlist']) == 0 or len(json.loads(request.body)['pools']) == 0:
                    return JsonResponse({"Error":"Incorrect data"}, status=200)
                actions_dir = "API/Actions/F5_SITE2_REMOVE_FROM_POOL"
                f5 = F5(config["site2"]["lb_site2_f502"], port, request.headers['token'])
                data = f5.remove_from_pools(json.loads(request.body)['memberlist'], json.loads(request.body)['pools'], actions_dir)
                data = iterate(actions_dir, request.headers['token'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

        
#########################################################################################
######## Update F5 commands
#########################################################################################

@method_decorator(csrf_exempt, name='dispatch')
class F5Site1UpdateCommands(View):
    def patch(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                f5 = F5(config["site1"]["lb_site1_f502"], port, request.headers['token'])
                data = f5_site1_update_commands(f5)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class F5Site2UpdateCommands(View):
    def patch(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in request.headers:
            try:
                f5 = F5(config["site2"]["lb_site2_f502"], port, request.headers['token'])
                data = f5_site2_update_commands(f5)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

#########################################################################################
######## Forti
#########################################################################################

@method_decorator(csrf_exempt, name='dispatch')
class FortiSite1GetToken(View):
    def post(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'user' in json.loads(request.body) and 'password' in json.loads(request.body):
            try:
                forti = Forti(config["site1"]["srv_site1_fwmgmt1"], port, "")
                data = forti.token(json.loads(request.body)['user'], json.loads(request.body)['password'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class FortiSite2GetToken(View):
    def post(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'user' in json.loads(request.body) and 'password' in json.loads(request.body):
            try:
                forti = Forti(config["site2"]["srv_site2_fwmgmt1"], port, "")
                data = forti.token(json.loads(request.body)['user'], json.loads(request.body)['password'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class FortiSite1AddToWhitelist(View):
    def post(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in json.loads(request.body) and 'memberlist' in json.loads(request.body) and 'whitelist' in json.loads(request.body) and 'nameprefix' in json.loads(request.body):
            try:
                if len(json.loads(request.body)['token']) == 0 or len(json.loads(request.body)['memberlist']) == 0 or len(json.loads(request.body)['whitelist']) == 0:
                    return JsonResponse({"Error":"Incorrect data"}, status=200)
                adom = "root"
                actions_dir = "API/Actions/FORTI_SITE1_ADD_TO_WHITELIST"
                forti = Forti(config["site1"]["srv_site1_fwmgmt1"], port, json.loads(request.body)['token'])
                data = forti.whitelist(json.loads(request.body)['memberlist'], json.loads(request.body)['whitelist'], json.loads(request.body)['nameprefix'], adom, actions_dir)
                data = iterate(actions_dir, json.loads(request.body)['token'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class FortiSite1RemoveFromWhitelist(View):
    def post(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in json.loads(request.body) and 'memberlist' in json.loads(request.body) and 'whitelist' in json.loads(request.body):
            try:
                if len(json.loads(request.body)['token']) == 0 or len(json.loads(request.body)['memberlist']) == 0 or len(json.loads(request.body)['whitelist']) == 0:
                    return JsonResponse({"Error":"Incorrect data"}, status=200)
                adom = "root"
                actions_dir = "API/Actions/FORTI_SITE1_REMOVE_FROM_WHITELIST"
                forti = Forti(config["site1"]["srv_site1_fwmgmt1"], port, json.loads(request.body)['token'])
                data = forti.remove_from_whitelist(json.loads(request.body)['memberlist'], json.loads(request.body)['whitelist'], adom, actions_dir)
                data = iterate(actions_dir, json.loads(request.body)['token'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class FortiSite1GetPolicyPkgStatus(View):
    def post(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in json.loads(request.body):
            try:
                adom = "root"
                forti = Forti(config["site1"]["srv_site1_fwmgmt1"], port, json.loads(request.body)['token'])
                data = forti.get_policy_pkg_status(adom)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class FortiSite1GetInstallPreview(View):
    def post(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in json.loads(request.body):
            try:
                adom = "root"
                forti = Forti(config["site1"]["srv_site1_fwmgmt1"], port, json.loads(request.body)['token'])
                data = forti.get_install_preview(adom)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class FortiSite1InstallPolicyAll(View):
    def post(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in json.loads(request.body):
            try:
                adom = "root"
                forti = Forti(config["site1"]["srv_site1_fwmgmt1"], port, json.loads(request.body)['token'])
                data = forti.install_policy_all(adom)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

##############################################################################################

@method_decorator(csrf_exempt, name='dispatch')
class FortiSite2AddToWhitelist(View):
    def post(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in json.loads(request.body) and 'memberlist' in json.loads(request.body) and 'whitelist' in json.loads(request.body) and 'nameprefix' in json.loads(request.body):
            try:
                if len(json.loads(request.body)['token']) == 0 or len(json.loads(request.body)['memberlist']) == 0 or len(json.loads(request.body)['whitelist']) == 0:
                    return JsonResponse({"Error":"Incorrect data"}, status=200)
                adom = "root"
                actions_dir = "API/Actions/FORTI_SITE2_ADD_TO_WHITELIST"
                forti = Forti(config["site2"]["srv_site2_fwmgmt1"], port, json.loads(request.body)['token'])
                data = forti.whitelist(json.loads(request.body)['memberlist'], json.loads(request.body)['whitelist'], json.loads(request.body)['nameprefix'], adom, actions_dir)
                data = iterate(actions_dir, json.loads(request.body)['token'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class FortiSite2RemoveFromWhitelist(View):
    def post(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in json.loads(request.body) and 'memberlist' in json.loads(request.body) and 'whitelist' in json.loads(request.body):
            try:
                if len(json.loads(request.body)['token']) == 0 or len(json.loads(request.body)['memberlist']) == 0 or len(json.loads(request.body)['whitelist']) == 0:
                    return JsonResponse({"Error":"Incorrect data"}, status=200)
                adom = "root"
                actions_dir = "API/Actions/FORTI_SITE2_REMOVE_FROM_WHITELIST"
                forti = Forti(config["site2"]["srv_site2_fwmgmt1"], port, json.loads(request.body)['token'])
                data = forti.remove_from_whitelist(json.loads(request.body)['memberlist'], json.loads(request.body)['whitelist'], adom, actions_dir)
                data = iterate(actions_dir, json.loads(request.body)['token'])
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class FortiSite2GetPolicyPkgStatus(View):
    def post(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in json.loads(request.body):
            try:
                adom = "root"
                forti = Forti(config["site2"]["srv_site2_fwmgmt1"], port, json.loads(request.body)['token'])
                data = forti.get_policy_pkg_status(adom)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class FortiSite2GetInstallPreview(View):
    def post(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in json.loads(request.body):
            try:
                adom = "root"
                forti = Forti(config["site2"]["srv_site2_fwmgmt1"], port, json.loads(request.body)['token'])
                data = forti.get_install_preview(adom)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class FortiSite2InstallPolicyAll(View):
    def post(self, request):
        if request.headers['Content-Type'] == 'application/json' and 'token' in json.loads(request.body):
            try:
                adom = "root"
                forti = Forti(config["site2"]["srv_site2_fwmgmt1"], port, json.loads(request.body)['token'])
                data = forti.install_policy_all(adom)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return JsonResponse({"Error":"Bad request"}, status=400)
            return JsonResponse(data)
        else:
            return JsonResponse({"Error":"Bad request"}, status=400)
