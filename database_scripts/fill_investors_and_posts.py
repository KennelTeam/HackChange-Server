import json
import requests
from tqdm import tqdm
import sys

host_address = sys.argv[1]
BASE_URL = 'http://{}/register?nickname={}&password={}'

tokens = []

with open('filling_investors.json') as f:
    investors = json.loads(f.read())

for nickname, password in tqdm(investors.items()):
    target_url = BASE_URL.format(
        host_address, nickname, password)
    resp = requests.get(BASE_URL.format(
        host_address, nickname, password)).json()
    tokens.append(resp['access_token'])


BASE_URL = 'http://{}/addPost?topic_id={}&text={}&access_token={}'
TOTAL_TOPICS = 91
DEFAULT_TEXT = "This is empty thread. Go to Shares/Tesla or Shares/Apple for demostraion of posts functionality."

with open('filling_posts.json') as f:
    posts_input = json.loads(f.read())

to_request = []

for topic in posts_input:
    topic_id = topic['topic_id']
    for post in topic['posts']:
        text = post['text']
        author_id = post['investor_id']
        to_request.append([topic_id, text, tokens[author_id]])


for r in tqdm(to_request):
    resp = requests.get(BASE_URL.format(host_address, *r)).json()

for t_id in tqdm(range(3, TOTAL_TOPICS+1)):
    resp = requests.get(BASE_URL.format(
        host_address, t_id, DEFAULT_TEXT, tokens[1])).json()
