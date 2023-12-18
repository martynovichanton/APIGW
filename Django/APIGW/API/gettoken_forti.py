from getpass import getpass
import requests
import gc
import json
from Crypto import Crypto
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

device_ip = "10.1.1.1"

def token(user, password):
    session = requests.Session()
    crypto = Crypto()
    url = f"https://" + device_ip + "/jsonrpc"
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

    response = session.request("POST", url, data=crypto.decrypt_random_key(payload), headers=headers, verify = False)
    #print(response.json())
    return {"token": response.json()["session"]}

main_crypto = Crypto()
user = main_crypto.encrypt_random_key(getpass("User"))
password = main_crypto.encrypt_random_key(getpass("Password"))
print(token(main_crypto.decrypt_random_key(user), main_crypto.decrypt_random_key(password)))