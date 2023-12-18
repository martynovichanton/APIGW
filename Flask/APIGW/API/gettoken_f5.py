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
    url = "https://" + device_ip + "/mgmt/shared/authn/login"
    crypto = Crypto()
    payload = crypto.encrypt_random_key("{\n    \"username\":" + user + ",\n    \"password\":" + password + ",\n    \"loginProviderName\": \"tmos\"\n}")
    headers = {
        'Content-Type': "application/json",
        'cache-control': "no-cache",
        }
    response = session.request("POST", url, data=crypto.decrypt_random_key(payload), headers=headers, verify = False)
    if response.status_code != 200:
        return {"Error":response.text}
    token = crypto.encrypt_random_key(response.json()['token']['token'])
    del response
    gc.collect()


    url = "https://" + device_ip + "/mgmt/shared/authz/tokens"
    payload = ""
    headers = crypto.encrypt_random_key(json.dumps({
        'X-F5-Auth-Token': crypto.decrypt_random_key(token),
        'cache-control': "no-cache"
    }))
    response = session.request("GET", url, data=payload, headers=json.loads(crypto.decrypt_random_key(headers)), verify = False)
    if response.status_code != 200:
        return {"Error":response.text}
    del response
    gc.collect()


    url = "https://" + device_ip + "/mgmt/shared/authz/tokens/" + crypto.decrypt_random_key(token)
    payload = "{\n    \"timeout\":\"3600\"\n}"
    headers = crypto.encrypt_random_key(json.dumps({
        'Content-Type': "application/json",
        'X-F5-Auth-Token': crypto.decrypt_random_key(token),
        'cache-control': "no-cache"
    }))
    response = session.request("PATCH", url, data=payload, headers=json.loads(crypto.decrypt_random_key(headers)), verify = False)
    if response.status_code != 200:
        return {"Error":response.text}
    token = crypto.encrypt_random_key(response.json()['token'])  
    timeout = response.json()['timeout']
    del response
    gc.collect()
    return {"token":crypto.decrypt_random_key(token), "timeout":timeout}

main_crypto = Crypto()
user = main_crypto.encrypt_random_key(getpass("User"))
password = main_crypto.encrypt_random_key(getpass("Password"))
print(token(main_crypto.decrypt_random_key(user), main_crypto.decrypt_random_key(password)))