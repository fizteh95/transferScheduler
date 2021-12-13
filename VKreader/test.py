import json
import pprint
import re
from typing import List
from typing import Optional

import requests
from pydantic import BaseModel
# from vkaudiotoken import get_kate_token
# from vkaudiotoken import get_vk_official_token
# login = '+79827156751'  # your vk login, e-mail or phone number
# password = '$$$Порапопарам2021'  # your vk password
#
# # print tokens and corresponding user-agent headers
# print(get_kate_token(login, password))
# print(get_vk_official_token(login, password))

'''
{'token': '4d1144c1bab10b9958916dd5b90dc1a9c4cf91a8932799f681e1a80b3986e1d56f731adb67951991355b3',
'user_agent': 'KateMobileAndroid/56 lite-460 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en)'}
{'token': 'bcbb4913d290a7a52b8e1458bda46b14fc51aca6cc500cf6a73f59cf97ef341eb55200ebbfbecb80391e5',
'user_agent':
    'VKAndroidApp/5.52-4543 (Android 5.1.1; SDK 22; x86_64; unknown Android SDK built for x86_64; en; 320x240)'}
'''

token = '4d1144c1bab10b9958916dd5b90dc1a9c4cf91a8932799f681e1a80b3986e1d56f731adb67951991355b3'
user_agent = 'KateMobileAndroid/56 lite-460 (Android 4.4.2; SDK 19; x86; unknown Android SDK built for x86; en)'

sess = requests.session()
sess.headers.update({'User-Agent': user_agent})

a = sess.get(
    'https://api.vk.com/method/audio.getById',
    params=[
        ('access_token', token),
        ('audios', '371745461_456289486'),
        ('v', '5.95'),
    ],
)

b = sess.get(
    'https://api.vk.com/method/wall.get',
    params=[
        ('access_token', token),
        ('domain', 'artelec'),
        ('offset', '0'),
        ('count', '1'),
        ('v', '5.95'),
    ],
)

# print(json.loads(a.content.decode()))
# print(json.loads(b.content.decode()))

posts = json.loads(b.content.decode())['response']['items']
post = posts[0]
t = post['attachments']
del post['attachments']

pp = pprint.PrettyPrinter()


class VkAudio(BaseModel):
    id: int
    url: str
    artist: str
    title: str


class VkPhoto(BaseModel):
    id: int
    url: str
    text: str


class RawPost(BaseModel):
    text: str
    timestamp: int
    marked_as_ads: int
    audios: Optional[List[VkAudio]] = []
    photos: Optional[List[VkPhoto]] = []


r = RawPost(text=post.get('text'), timestamp=post['date'], marked_as_ads=post.get('marked_as_ads'))


def get_biggest_size(sizes: List) -> str:
    biggest = 0
    url = ''
    for s in sizes:
        if s['height'] > biggest:
            biggest = s['height']
            url = s['url']
    return url


def preprocess_text(text: str) -> str:
    inplaces = re.findall(r'\[.*?\]', text)
    for i in inplaces:
        club = i.split('[')[1].split('|')[0]
        name = i.split('|')[1].split(']')[0]
        text = text.replace(i, f'<a href="http://vk.com/{club}">{name}</a>')
    return text


for a in t:
    if a.get('type') == 'photo':
        p = a['photo']
        vk_p = VkPhoto(id=p['id'], text=p['text'], url=get_biggest_size(p['sizes']))
        r.photos.append(vk_p)
    elif a.get('type') == 'audio':
        m = a['audio']
        vk_m = VkAudio(id=m['id'], url=m['url'], title=m['title'], artist=m['artist'])
        r.audios.append(vk_m)

r.text = preprocess_text(r.text)

pp.pprint(r.dict())
