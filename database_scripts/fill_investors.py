import json
import requests

BASE_URL = 'http://localhost:5000/login?nickname={}&password={}'

with open('filling_investors.json') as f:
    investors = json.loads(f.read())

for nickname, password in investors.items():
    resp = requests.get(BASE_URL.format(nickname, password)).json()
    print(resp['ok'])
