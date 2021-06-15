import time
from http.client import HTTPSConnection
from base64 import b64encode
import requests
from requests.auth import HTTPBasicAuth

response = requests.get('http://0.0.0.0:8000',
auth = HTTPBasicAuth('root', 'L'))
# COM ISTO JA CONSEGUE CORRER O SLAVE E ENONTRAR A PASS, NO SEGUNDO ARG DE HTTPBASICAUTH

print(response)

while True:
    print("all your base are belong to us")
    time.sleep(1)
