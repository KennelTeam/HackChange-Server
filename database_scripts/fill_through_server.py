import json
import os
import requests
from tqdm import tqdm
import sys
import random

#
#
# This script fills: investors data, posts data, avatars, comments
#
#

host_address = sys.argv[1]
BASE_URL = 'http://{}/register?nickname={}&password={}'
AVATAR_URL = 'http://{}/uploadAvatar?access_token={}'

comment_texts = ['Wow! This is impressive!',
                 'Oh no, why??',
                 'Oh, I like this', 'Looks like a good signal',
                 'This for me :)',
                 'This is bad...',
                 'Oups, loks dangerous']

tokens = []

with open('filling_investors.json') as f:
    investors = json.loads(f.read())

for nickname, password in tqdm(investors.items()):
    target_url = BASE_URL.format(
        host_address, nickname, password)
    resp = requests.get(BASE_URL.format(
        host_address, nickname, password)).json()
    cur_token = resp['access_token']
    tokens.append(cur_token)
    if os.path.isfile(f'avatars/{nickname}.png'):
        requests.post(AVATAR_URL.format(host_address, cur_token),
                      files={'file': open(f'avatars/{nickname}.png', 'rb')})


BASE_URL = 'http://{}/addPost?topic_id={}&text={}&access_token={}'
COMMENTS_URL = 'http://{}/addComment?post_id={}&text={}&access_token={}'
TOTAL_TOPICS = 91
DEFAULT_TEXT = "This is empty thread. Go to Shares/Tesla or Shares/Apple for demostraion of posts functionality."

with open('filling_posts.json') as f:
    posts_input = json.loads(f.read())

to_request_posts = []

for topic in posts_input:
    topic_id = topic['topic_id']
    for post in topic['posts']:
        text = post['text']
        author_id = post['investor_id']
        to_request_posts.append([topic_id, text, tokens[author_id]])


for r in tqdm(to_request_posts):
    resp = requests.get(BASE_URL.format(host_address, *r)).json()
    idxs = list(range(5))
    random.shuffle(idxs)
    for i in idxs:
        url = COMMENTS_URL.format(
            host_address, resp['post_id'], random.choice(comment_texts), tokens[i])
        requests.get(url)

for t_id in tqdm(range(3, TOTAL_TOPICS+1)):
    resp = requests.get(BASE_URL.format(
        host_address, t_id, DEFAULT_TEXT, tokens[-1])).json()
