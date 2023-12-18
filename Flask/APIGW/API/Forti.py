from functools import cmp_to_key
import os
import sys
import paramiko
import time
from getpass import getpass
from datetime import datetime
import requests
import json
from Crypto import Crypto
import time
import gc
from ipaddress import IPv4Network
from ipaddress import IPv4Address
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Forti():
    def __init__(self, ip, port, token):
        self.session = requests.Session()
        self.crypto = Crypto()
        self.ip = ip
        self.port = port
        self.sleepTimeCommand = 0.1
        self.commandsFile = None
        self.headers = {
                    'Content-Type':"application/json",
                    'cache-control':"no-cache"
        }
        self.payload = {
            "method": "",
            "params": [],
            "session": token,
            "id": 0
        }

    def runCommand(self, command):
        method = command.split('---')[0]
        url = f"https://{self.ip}:{str(self.port)}/jsonrpc"
        api_method = command.split('---')[1]
        params = command.split('---')[2]
        self.payload["method"] = api_method
        self.payload["params"] = []
        self.payload["params"].append(json.loads(params)),

        response = self.session.request(method, url, data=json.dumps(self.payload), headers=self.headers, verify = False)
        return response.json()

    def token(self, user, password):
        crypto = Crypto()
        url = f"https://" + self.ip + "/jsonrpc"
        payload = crypto.encrypt_random_key(json.dumps({
            "method": "exec",
            "params": [{
                "url": "/sys/login/user",
                "data": {"user":user,"passwd":password}
            }],
        }))
        headers = {
                    'Content-Type':"application/json",
                    'cache-control':"no-cache"
        }

        response = self.session.request("POST", url, data=crypto.decrypt_random_key(payload), headers=headers, verify = False)
        if not "session" in response.json():
            return {"Error":response.text}
        #print(response.json())
        return {"token": response.json()["session"]}
    

    def validate_ip(self, ip):
        # ip = ip/subnetmask or ip
        try:
            if IPv4Network(ip):
                return True
            else:
                return False
        except ValueError as e:
            return False

    def clasify_member(self, member):
        #ipmask iprange fqdn
        type = ""
        if "/" in member:
            if self.validate_ip(member):
                type = "ipmask"
            else:
                type = "fqdn"
        elif "-" in member:
            start = member.split("-")[0]
            end = member.split("-")[1]
            if self.validate_ip(start) and self.validate_ip(end):
                type = "iprange"
            else:
                type = "fqdn"
        else:
            type = "fqdn"
        return type

    def get_fwaddrs_all(self, adom):
        fwaddrs = self.runCommand(f'post---get---{{"url":"/pm/config/adom/{adom}/obj/firewall/address"}}')
        return fwaddrs

    def get_fwaddrgrps_all(self, adom):
        fwaddrgrps = self.runCommand(f'post---get---{{"url":"/pm/config/adom/{adom}/obj/firewall/addrgrp"}}')
        return fwaddrgrps

    def check_exists(self, fwaddrs, member, adom):
        #returns the name of the obect if exists in the FW
        addr_exists = ""
        #type:0 ipmask type:1 range type:2 fqdn
        type = self.clasify_member(member)
        if type == "ipmask":
            network_address = str(IPv4Network(member).network_address)
            netmask = str(IPv4Network(member).netmask)
            for addr in fwaddrs['result'][0]['data']:
                if addr['type'] == 0:
                    if network_address == addr['subnet'][0] and netmask == addr['subnet'][1]:
                        addr_exists = addr['name']
        elif type == "iprange":
            start = member.split("-")[0]
            end = member.split("-")[1]
            for addr in fwaddrs['result'][0]['data']:
                if addr['type'] == 1:
                    if start == addr['start-ip'] and end == addr['end-ip']:
                        addr_exists = addr['name']
        elif type == "fqdn":
            for addr in fwaddrs['result'][0]['data']:
                if addr['type'] == 2:
                    if member == addr['fqdn']:
                        addr_exists = addr['name']
        return addr_exists

    def check_is_inside_list(self, name, list, adom):
        addr_is_inside_list = False
        addrgrp = self.runCommand(f'post---get---{{"filter": ["name", "==", "{list}"],"url": "/pm/config/adom/{adom}/obj/firewall/addrgrp"}}')
        #print(name)
        #print(addrgrp['result'][0]['data'][0]['member'])

        #addrgrp exists and the response has data
        if len(addrgrp['result'][0]['data']) > 0:
            if name in addrgrp['result'][0]['data'][0]['member']:
                addr_is_inside_list = True
        return addr_is_inside_list

    def generate_name(self, member, nameprefix):
        name = ""
        prefix = nameprefix
        netmask = ""
        type = self.clasify_member(member)
        if type == "ipmask":
            network_address = str(IPv4Network(member).network_address)
            netmask = str(IPv4Network(member).prefixlen)
            name = f"{prefix}{network_address}_{netmask}"
        elif type == "iprange":
            start = member.split("-")[0]
            end = member.split("-")[1]
            name = f"{prefix}{start}_{end}"
        elif type == "fqdn":
            name = f"{prefix}{member}"
        return name

    def create_member(self, name, member, adom):
        # print(member)
        type = self.clasify_member(member)
        # print(type)
        if type == "ipmask":
            self.commandsFile.write(f'post---add---{{"data":{{"name":"{name}","subnet":"{member}","type":"ipmask"}},"url":"/pm/config/adom/{adom}/obj/firewall/address/"}}\n')
        elif type == "iprange":
            start = member.split("-")[0]
            end = member.split("-")[1]
            self.commandsFile.write(f'post---add---{{"data":{{"name":"{name}","start-ip":"{start}","end-ip":"{end}","type":"iprange"}},"url":"/pm/config/adom/{adom}/obj/firewall/address/"}}\n')
        elif type == "fqdn":
            self.commandsFile.write(f'post---add---{{"data":{{"name":"{name}","fqdn":"{member}","type":"fqdn"}},"url":"/pm/config/adom/{adom}/obj/firewall/address/"}}\n')

    def add_member_to_list(self, name, list, adom):
        self.commandsFile.write(f'post---add---{{"data":["{name}"],"url":"/pm/config/adom/{adom}/obj/firewall/addrgrp/{list}/member"}}\n')
    
    def remove_member_from_list(self, name, list, adom):
        self.commandsFile.write(f'post---delete---{{"data":["{name}"],"url":"/pm/config/adom/{adom}/obj/firewall/addrgrp/{list}/member"}}\n')

    def lock(self, adom):
        self.commandsFile.write(f'post---exec---{{"url":"/dvmdb/adom/{adom}/workspace/lock"}}\n')

    def send_lock(self, adom):
        self.runCommand(f'post---exec---{{"url":"/dvmdb/adom/{adom}/workspace/lock"}}')

    def unlock(self, adom):
        self.commandsFile.write(f'post---exec---{{"url":"/dvmdb/adom/{adom}/workspace/unlock"}}\n')

    def send_unlock(self, adom):
        self.runCommand(f'post---exec---{{"url":"/dvmdb/adom/{adom}/workspace/unlock"}}')

    def lockinfo(self, adom):
        self.commandsFile.write(f'post---exec---{{"url": "/dvmdb/adom/{adom}/workspace/lockinfo"}}')

    def is_locked(self, adom):
        locked = False
        lockinfo = self.runCommand(f'post---exec---{{"url": "/dvmdb/adom/{adom}/workspace/lockinfo"}}')
        #adom is locked and the response has data
        if 'data' in lockinfo['result'][0]:
            locked = True
        return locked

    def commit(self, adom):
        self.commandsFile.write(f'post---exec---{{"url":"/dvmdb/adom/{adom}/workspace/commit"}}\n')
    
    def whitelist(self, memberlist, whitelist, nameprefix, adom, dir):
        #generate commands file for whitelist
        addr_exists = ""
        addr_is_inside_list = False
        
        fwaddrs = self.get_fwaddrs_all(adom)
        fwaddrsgrps = self.get_fwaddrgrps_all(adom)
        
        self.commandsFile = open(f"{dir}/api/forti/commands.txt", 'w')
        self.commandsFile.truncate(0)

        if not self.is_locked(adom):
            # adom is not locked
            self.lock(adom)
            for member in memberlist:
                addr_exists = self.check_exists(fwaddrs, member, adom)
                if not addr_exists:
                    object_name = self.generate_name(member, nameprefix)
                    self.create_member(object_name, member, adom)
                for list in whitelist:
                    if addr_exists:
                        addr_is_inside_list = self.check_is_inside_list(addr_exists, list, adom)
                        if not addr_is_inside_list:
                            self.add_member_to_list(addr_exists, list, adom)
                    else:
                        self.add_member_to_list(object_name, list, adom)
            self.commit(adom)
            self.unlock(adom)
        else:
            # adom is locked
            self.lockinfo(adom)
            
        self.commandsFile.close()

        return {"result":"whitelisted"}

    def remove_from_whitelist(self, memberlist, whitelist, adom, dir):
        #generate commands file for whitelist
        addr_exists = ""
        addr_is_inside_list = False
        
        fwaddrs = self.get_fwaddrs_all(adom)
        fwaddrsgrps = self.get_fwaddrgrps_all(adom)
        
        self.commandsFile = open(f"{dir}/api/forti/commands.txt", 'w')
        self.commandsFile.truncate(0)

        if not self.is_locked(adom):
            # adom is not locked
            self.lock(adom)
            for member in memberlist:
                addr_exists = self.check_exists(fwaddrs, member, adom)
                if addr_exists:
                    for list in whitelist:
                        addr_is_inside_list = self.check_is_inside_list(addr_exists, list, adom)
                        if addr_is_inside_list:
                            self.remove_member_from_list(addr_exists, list, adom)
            self.commit(adom)
            self.unlock(adom)
        else:
            # adom is locked
            self.lockinfo(adom)
            
        self.commandsFile.close()

        return {"result":"removed from whitelist"}



    def get_policy_pkg_status(self, adom):
        pkg_status = self.runCommand(f'post---get---{{"url": "/pm/config/adom/{adom}/_package/status"}}')
        return pkg_status

    def get_task(self, id):
        task = self.runCommand(f'post---get---{{"url": "/task/task/{id}"}}')
        return task

    def wait_for_task(self, id):
        count = 0
        max_count = 120
        done = False
        while not done:
            time.sleep(5)
            task = self.get_task(id)
            if task['result'][0]['data']['percent'] == 100 or count == max_count:
                done = True
            count += 1

    def install_package_preview(self, adom, pkg):
        data = self.runCommand(f'post---exec---{{"data":{{"adom":"{adom}", "flags":["preview"], "pkg":"{pkg}"}},"url":"securityconsole/install/package"}}')
        return data
        
    def install_preview(self, adom, dev):
        data = self.runCommand(f'post---exec---{{"data":{{"adom": "{adom}", "device":"{dev}"}},"url":"securityconsole/install/preview"}}')
        return data

    def install_preview_result(self, adom, dev):
        data = self.runCommand(f'post---exec---{{"data":{{"adom": "{adom}", "device":"{dev}"}},"url":"securityconsole/preview/result"}}')
        return data
    
    def get_install_preview(self, adom):
        diff = []
        if not self.is_locked(adom):
            self.send_lock(adom)
            pkg_status = self.get_policy_pkg_status(adom)
            for pkg in pkg_status['result'][0]['data']:
                if pkg['status'] == "modified":
                    pkg_prev = self.install_package_preview(adom, pkg['pkg'])
                    # time.sleep(20)
                    self.wait_for_task(pkg_prev['result'][0]['data']['task'])
                    inst_prev = self.install_preview(adom, pkg['dev'])
                    # time.sleep(20)
                    self.wait_for_task(inst_prev['result'][0]['data']['task'])
                    prev_result = self.install_preview_result(adom, pkg['dev'])
                    diff.append({f"{pkg['pkg']}":prev_result['result'][0]['data']['message']})
            self.send_unlock(adom)
            return {"preview":diff}
        else:
            return {"preview":"device is locked"}
    
    def install_policy(self, adom, pkg, dev, vdom):
        data = self.runCommand(f'post---exec---{{"data":{{"adom": "{adom}","pkg": "{pkg}","scope": [{{"name": "{dev}","vdom": "{vdom}"}}]}},"url":"securityconsole/install/package"}}')
        return data

    def install_policy_all(self, adom):
        install = []
        if not self.is_locked(adom):
            self.send_lock(adom)
            pkg_status = self.get_policy_pkg_status(adom)
            for pkg in pkg_status['result'][0]['data']:
                if pkg['status'] == "modified":
                    inst_result = self.install_policy(adom, pkg['pkg'], pkg['dev'], pkg['vdom'])
                    self.wait_for_task(inst_result['result'][0]['data']['task'])
                    install.append(inst_result)
            self.send_unlock(adom)
            return {"install":install}
        else:
            return {"install":"device is locked"}

