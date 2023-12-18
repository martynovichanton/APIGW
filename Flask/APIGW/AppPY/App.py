from flask import Flask, render_template
from flask import json
import requests
import getpass
from Crypto import Crypto
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
crypto = Crypto()
token = crypto.encrypt_random_key(getpass.getpass('token '))

@app.route('/')
def index():
    global token
    headers = crypto.encrypt_random_key(json.dumps({
            'Content-Type': "application/json",
            'token': crypto.decrypt_random_key(token),
            'cache-control': "no-cache"
    }))
    payload = ""
    stats = requests.get("http://localhost:5000/f5api/F5_SITE1_show_stats", data=payload, headers=json.loads(crypto.decrypt_random_key(headers)), verify=False)
    config = requests.get("http://localhost:5000/f5api/F5_SITE1_show_config", data=payload, headers=json.loads(crypto.decrypt_random_key(headers)), verify=False)
    dataset = [stats.json(), config.json()]
 
    return render_template('index.html', dataset=dataset)


@app.route('/json')
def j():
    return render_template('json.html')




if __name__ == '__main__':
    app.run(port=5001)
