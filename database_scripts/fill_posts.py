import json
import requests
from tqdm import tqdm

BASE_URL = 'http://localhost:5000/addPost?topic_id={}&text={}&access_token={}'
TOTAL_TOPICS = 91
DEFAULT_TEXT = "This is empty thread. Go to Shares/Tesla or Shares/Apple for demostraion of posts functionality."

investors = {
    1: "1.iiwjcnZlcASRWCFqTuGNoIVYmXpoEz",
    2: "2.FicMfxcCPLabVeAcOgnjbFiawiEqar",
    3: "3.ftGvdpYUYAGHMpKgNQdZGCOSnsxRpx",
    4: "4.EsURlOqAKdLnjtnOyCjKwdUtGCndvG",
    5: "5.RnnBwEXZcEchxmGbCIQJsvtptzxLUe",
    6: "6.dvPXtSKPzmHNJjyEwPmXRLhHLogqmq",
    7: "7.ONPWVoywXeCAytcHcSoKHCirbWZsTa",
    8: "8.zIIGyMFXLXPwVwDMAXhxpQwboNGnMp",
    9: "9.fvZnMEnMdjJfBYmSpmHUVfOPyiYSKS",
    10: "10.kpwGHLrhEFCIFcymvhPHfITyFUuyA",
    11: "11.xqDLTLQuJNchUCqHvUGpCVksTBYaw",
    12: "12.vnZREywUIHwporHWfBCNjocZKclfI",
}

with open('filling_posts.json') as f:
    posts_input = json.loads(f.read())

to_request = []

for topic in posts_input:
    topic_id = topic['topic_id']
    for post in topic['posts']:
        text = post['text']
        author_id = post['investor_id']
        to_request.append([topic_id, text, investors[author_id]])


for r in tqdm(to_request):
    resp = requests.get(BASE_URL.format(*r)).json()

for t_id in tqdm(range(3, TOTAL_TOPICS+1)):
    resp = requests.get(BASE_URL.format(
        t_id, DEFAULT_TEXT, investors[1])).json()
