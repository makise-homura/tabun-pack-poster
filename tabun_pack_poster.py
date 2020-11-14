#!/usr/bin/env python3

##############################################################################

# Your tabun credentials
username = 'your username on tabun'
password = 'your password on tabun'

# Proxy. Set to '' (not None!) for direct connection.
proxy = ''
# Or use something like 'http://user:passwd@httpsproxy.net:8080'

# Derpibooru mirror to use
mirror = 'https://www.trixiebooru.org' # the only available in RU w/o proxy

# Post properties (use three underscores to substitute pack number in title)
title = 'Пак имени лучшей музыкальной пони №___'
tags = ['Лира Харстрингс', 'пак', 'картинки']
blog_id = 0 # 0 = your personal blog

# Tags to search on Derpibooru
pony = 'lyra heartstrings'
also = ', safe, -webm' # May be empty; otherwise first comma is mandatory

# Post template (__OP_PIC__ and __PIC_BLOCK__ are placeholders)
body = """
__OP_PIC__
<cut name="Больше мятности и музыкальности! →">
__PIC_BLOCK__
Да пребудет с вами Лира!
"""

# Pics for spoilers (like those you see in Celestia and Luna packs)
spoilerpics = None # use None for generic text spoilers
# Or array of tabun-hosted pics URLs (no less than `piclimit`), like this:
# spoilerpics = [
#     'https://cdn.everypony.ru/storage/06/15/73/2020/09/15/b415d211d9.png',
#     'https://cdn.everypony.ru/storage/06/15/73/2020/09/15/ab1e77be91.png',
#     'https://cdn.everypony.ru/storage/06/15/73/2020/09/15/d0d39e2e1d.png',
# ]

# Other config
timezone = '+03:00' # Timezone for searching images on Derpibooru
config = '.tabun-pack/number' # Where to store pack number (relative to '~')
period = 7 # How many days to get pics from
piclimit = 15 # How many pictures to retrieve (not including OP pic, max 49)

##############################################################################

# Install Tabun API, if you don't have one:
# pip install git+https://github.com/andreymal/tabun_api.git#egg=tabun_api[full]

import tabun_api
import datetime
import json
import requests
from pathlib import Path

# First, get pictures from Derpibooru
date = datetime.date.today() - datetime.timedelta(days=period)
dbtags = pony + also + ', created_at.gte:' + date.strftime('%Y-%m-%d') + timezone
params = [('sf', 'score'), ('per_page', piclimit + 1), ('q', dbtags)]
proxies = {} if proxy == '' else {'https': proxy}
print('Retrieving from derpibooru by tags:', dbtags)
try:
    response = requests.get(mirror + '/api/v1/json/search/images', params=params, proxies=proxies)
except requests.exceptions.RequestException as e:
    print('HTTPS request error:', e)
    raise SystemExit(e)
try:
    json = response.json();
except json.JSONDecodeError as e:
    print('JSON decode error:', e)
    raise SystemExit(e)
total = len(json['images'])
print('Retrieved', total, 'images of', str(json['total']) + '.')

# Login to Tabun
print('Logging in...')
tabun = tabun_api.User(login=username, passwd=password, proxy=proxy);

# Upload pictures and put links into a template body
current_pic = 0
pic_block = ''
for picture in json['images']:
    desc = picture['description'].replace('\r\n', ' ')
    if len(desc) > 50:
        desc = desc[0:50] + '(...)'
    print('Uploading [' + str(current_pic) + '/' + str(total) + ']:', desc)
    link_rep = picture['representations']['medium'] if current_pic == 0 else picture['representations']['large']
    img_link = tabun.upload_image_link(link_rep, title=picture['description'], parse_link=False)
    img_url = tabun.upload_image_link(picture['representations']['full'], parse_link=True)
    if current_pic == 0:
        op_pic = '<a href="' + img_url + '" target="_blank">' +img_link + '</a></span></span>'
    else:
        if spoilerpics == None:
            spoilerpic = 'Спойлер ' + str(current_pic)
        else:
            spoilerpic = '<img src = "' + spoilerpics[current_pic - 1] + '" >'
        pic_block += '<span class="spoiler"><span class="spoiler-title">' + spoilerpic + '</span><span class="spoiler-body"><a href="' + img_url + '" target="_blank">' +img_link + '</a></span></span>'
    current_pic += 1
body = body.replace('__OP_PIC__', op_pic).replace('__PIC_BLOCK__', pic_block)

# Check pack number and set title
configfile = Path(str(Path.home()) + '/' + config)
if configfile.is_file():
    pack_number = int(configfile.read_text()) + 1
else:
    configfile.parent.mkdir(parents=True, exist_ok=True)
    pack_number = 1
configfile.write_text(str(pack_number))
title = title.replace('___', str(pack_number))

# Add a post!
print('Adding a draft post:', title)
try:
    blog, post_id = tabun.add_post(blog_id, title, body, tags, forbid_comment=False, draft=True)
except tabun_api.TabunError as e:
    print('Tabun error:', e)
    raise SystemExit(e)

print('New post added successfully! Link: https://tabun.everypony.ru/blog/' + str(post_id) + '.html')
# If you forgot a link, you may find it here: https://tabun.everypony.ru/topic/saved/
