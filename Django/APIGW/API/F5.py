import os
import sys
import paramiko
import time
from getpass import getpass
from datetime import datetime
import requests
import json
from .Crypto import Crypto
import time
import gc
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class F5():
    def __init__(self, ip, port, token):
        self.session = requests.Session()
        self.crypto = Crypto()
        self.ip = ip
        self.port = port
        self.sleepTimeCommand = 0.1
        #self.token = self.crypto.encrypt_random_key(token)
        self.headers = self.crypto.encrypt_random_key(json.dumps({
                    'Content-Type':"application/json",
                    'X-F5-Auth-Token':token,
                    'cache-control':"no-cache"
                }))

    def runCommand(self, command):
        method = command.split('---')[0]
        #url = "https://" + self.ip + ":" + str(self.port) + command.split('---')[1]
        url = f"https://{self.ip}:{str(self.port)}{command.split('---')[1]}"
        payload = command.split('---')[2]  
        response = self.session.request(method, url, data=payload, headers=json.loads(self.crypto.decrypt_random_key(self.headers)), verify = False)
        return response.json()

    def pools(self):
        pool_members = self.runCommand(f'get---/mgmt/tm/ltm/pool---')
        return {"pools":pool_members}
    
    def pool_members(self, pool_name):
        pool_members = self.runCommand(f'get---/mgmt/tm/ltm/pool/{pool_name}/members---')
        return {"pool_members":pool_members}
    
    def pool_members_stats(self, pool_name):
        pool_members_stats = self.runCommand(f'get---/mgmt/tm/ltm/pool/{pool_name}/members/stats---')
        return {"pool_members_stats":pool_members_stats}
    
    def disable_pool_member(self, pool_name, member_name):
        response = self.runCommand(f'patch---/mgmt/tm/ltm/pool/{pool_name}/members/{member_name}---{json.dumps({"session":"user-disabled"})}')
        return {"response":response}
    
    def enable_pool_member(self, pool_name, member_name):
        response = self.runCommand(f'patch---/mgmt/tm/ltm/pool/{pool_name}/members/{member_name}---{json.dumps({"session":"user-enabled"})}')
        return {"response":response}

    def token(self, user, password):
        url = "https://" + self.ip + "/mgmt/shared/authn/login"
        #self.payload = self.crypto.encrypt_random_key("{\n    \"username\":" + user + ",\n    \"password\":" + password + ",\n    \"loginProviderName\": \"tmos\"\n}")
        self.payload = self.crypto.encrypt_random_key(json.dumps({"username":user, "password":password, "loginProviderName":"tmos"}))
        self.headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache",
            }
        response = self.session.request("POST", url, data=self.crypto.decrypt_random_key(self.payload), headers=self.headers, verify = False)
        if response.status_code != 200:
            return {"Error":response.text}
        token = self.crypto.encrypt_random_key(response.json()['token']['token'])
        del response
        gc.collect()


        url = "https://" + self.ip + "/mgmt/shared/authz/tokens"
        self.payload = ""
        self.headers = self.crypto.encrypt_random_key(json.dumps({
            'X-F5-Auth-Token': self.crypto.decrypt_random_key(token),
            'cache-control': "no-cache"
        }))
        response = self.session.request("GET", url, data=self.payload, headers=json.loads(self.crypto.decrypt_random_key(self.headers)), verify = False)
        if response.status_code != 200:
            return {"Error":response.text}
        del response
        gc.collect()


        url = "https://" + self.ip + "/mgmt/shared/authz/tokens/" + self.crypto.decrypt_random_key(token)
        self.payload = "{\n    \"timeout\":\"3600\"\n}"
        self.headers = self.crypto.encrypt_random_key(json.dumps({
            'Content-Type': "application/json",
            'X-F5-Auth-Token': self.crypto.decrypt_random_key(token),
            'cache-control': "no-cache"
        }))
        response = self.session.request("PATCH", url, data=self.payload, headers=json.loads(self.crypto.decrypt_random_key(self.headers)), verify = False)
        if response.status_code != 200:
            return {"Error":response.text}
        token = self.crypto.encrypt_random_key(response.json()['token'])  
        timeout = response.json()['timeout']
        del response
        gc.collect()
        return {"token":self.crypto.decrypt_random_key(token), "timeout":timeout}
    
###############################################################
###############################################################
###############################################################

    def get_nodes_all(self):
        nodes = self.runCommand(f'get---/mgmt/tm/ltm/node---')
        return nodes

    def get_pools_all(self):
        pools = self.runCommand(f'get---/mgmt/tm/ltm/pool---')
        return pools
    
    def check_exists(self, nodes, member):
        #returns the node object if exists in the F5

        node_exists = {}
        for node in nodes:
            if member["address"] == node["address"].split("%")[0]:
                node_exists = node

        return node_exists
    
    def check_is_inside_pool(self, node, port, pool):
        #check if the node:port is inside pool
        node_is_inside_pool = False
        pool_members = self.runCommand(f'get---/mgmt/tm/ltm/pool/{pool}/members---')

        #pool exists and the response has data
        if "items" in pool_members:
            for member in pool_members["items"]:
                if f'{node["name"]}:{port}' == member["name"]:
                    node_is_inside_pool = True
        
        return node_is_inside_pool
    

    def create_node(self, partition, name, address):
        # remove port from name
        name = name.split(":")[0]
        self.commandsFile.write(f'post---/mgmt/tm/ltm/node---{{"partition":"{partition}", "name":"{name}", "address":"{address}"}}\n')

    def add_member_to_pool(self, partition, name, address, port, priorityGroup, pool):
        # remove ~Partition from pool name
        pool = pool.split("~")[2]
        self.commandsFile.write('post---/mgmt/tm/util/bash---{"command":"run", "utilCmdArgs": "-c \'echo \\"cd /' + partition + '; modify ltm pool ' + pool + ' members add { ' + name + ':' + port + ' { priority-group ' + str(priorityGroup) + ' } }\\" | tmsh | bash\'"}\n')

    def remove_member_from_pool(self, partition, name, address, port, pool):
        # remove ~Partition from pool name
        pool = pool.split("~")[2]
        self.commandsFile.write('post---/mgmt/tm/util/bash---{"command":"run", "utilCmdArgs": "-c \'echo \\"cd /' + partition + '; modify ltm pool ' + pool + ' members delete { ' + name + ':' + port + '}\\" | tmsh | bash\'"}\n')

    def add_to_pools(self, memberlist, pools, dir):
        # generate commands file for pool addition

        node_exists = ""
        node_is_inside_pool = False

        nodes = self.get_nodes_all()["items"]
        # pools = self.get_pools_all()["items"]

        self.commandsFile = open(f"{dir}/api/f5/commands.txt", 'w')
        self.commandsFile.truncate(0)

        for member in memberlist:
            partition = member["name"].split("~")[1]
            name = member["name"].split("~")[2].split(":")[0]
            address = member["address"]
            port = member["name"].split("~")[2].split(":")[1]
            priorityGroup = member["priorityGroup"]

            node_exists = self.check_exists(nodes, member)
            if not node_exists:
                self.create_node(partition, name, address)
            for pool in pools:
                if node_exists:
                    name = node_exists["name"]
                    address = node_exists["address"].split("%")[0] #remove %partition from ip
                    node_is_inside_pool = self.check_is_inside_pool(node_exists, port, pool)
                    # print(node_is_inside_pool, pool, member)
                    if not node_is_inside_pool:
                        self.add_member_to_pool(partition, name, address, port, priorityGroup, pool)
                else:
                    self.add_member_to_pool(partition, name, address, port, priorityGroup, pool)

        self.commandsFile.close()

        return {"result":"added to pool"}
    
    def remove_from_pools(self, memberlist, pools, dir):
        # generate commands file for pool addition

        node_exists = ""
        node_is_inside_pool = False

        nodes = self.get_nodes_all()["items"]
        # pools = self.get_pools_all()["items"]

        self.commandsFile = open(f"{dir}/api/f5/commands.txt", 'w')
        self.commandsFile.truncate(0)

        for member in memberlist:
            partition = member["name"].split("~")[1]
            name = member["name"].split("~")[2].split(":")[0]
            address = member["address"]
            port = member["name"].split("~")[2].split(":")[1]

            node_exists = self.check_exists(nodes, member)
            if node_exists:
                for pool in pools:
                    name = node_exists["name"]
                    address = node_exists["address"].split("%")[0] #remove %partition from ip
                    node_is_inside_pool = self.check_is_inside_pool(node_exists, port, pool)
                    # print(node_is_inside_pool, pool, member)
                    if node_is_inside_pool:
                        self.remove_member_from_pool(partition, name, address, port, pool)

        self.commandsFile.close()

        return {"result":"removed from pool"}
    