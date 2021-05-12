#!/usr/bin/env python3

##############################################################################

# Your tabun credentials
username = 'your username on tabun'
password = 'your password on tabun'

# Proxy. Set to '' (not None!) for direct connection.
proxy = ''
# Or use something like 'http://user:passwd@httpsproxy.net:8080'

# Derpibooru mirror to use
mirror = 'https://www.trixiebooru.org' # the only Derpibooru mirror available in RU w/o proxy
apitype = 'derpibooru' # derpibooru or twibooru

# Post properties (use three underscores to substitute pack number in title)
title = 'Пак имени лучшей музыкальной пони №___'
tags = ['Лира Харстрингс', 'Лира', 'Lyra Heartstrings', 'Lyra', 'пак', 'картинки']
blog_id = 'Heartstrings' # integer ID or string from URL; 0 = your personal blog

# Tags to sort and search on Derpibooru
pony = 'lyra heartstrings'
bonuspony = 'bon-bon'
also = 'safe, -webm, -exploitable meme, -meme, -irl, -comic, -screencap, -meta, -text only'
sort = 'wilson_score' # 'score' looks like not so suitable

# Post template (__OP_PIC__ and __PIC_BLOCK__ are placeholders)
# ___ will also be changed to pack number, as in title
tmpl_body = """
Пришло время для ___-го пака имени Лиры Харстрингс.
__OP_PIC__
<cut name="Больше мятности и музыкальности! →">
__PIC_BLOCK__
Да пребудет с вами Лира!
"""

# Other templates
# Placeholders regognized:
# ___ : spoiler number (not in op_pic),
# __PIC__ : URL of spoilerpic/resized picture (not in text_spoiler_header_*)
# __FULL__ : <img> tag of full-resolution picture (not in *_spoiler_header)
# __DESC__ : Derpibooru picture description
# __NAME__ : Derpibooru picture name
# __AUTHOR__ : Derpibooru picture artist (or uploader, if no artist tag is given)
# __SOURCE__ : Derpibooru picture source URL
# __ID__ : Derpibooru picture ID
# __DB_URL__ : Derpibooru URL of picture page
tmpl_text_spoiler_header = 'Спойлер ___'
tmpl_text_spoiler_header_bonus = 'Бонус'
tmpl_pic_spoiler_header = '<img src = "__PIC__" >'
tmpl_pic_spoiler_header_bonus = '<img src = "__PIC__" >'
tmpl_op_pic = '<a href="__PIC__" target="_blank">__FULL__</a>'
tmpl_alttext = '__DESC__'
tmpl_spoiler_contents = """№ <a href="__DB_URL__" target="_blank">___</a>
<a href="__PIC__" target="_blank">__FULL__</a>"""
tmpl_spoiler_contents_bonus = """<a href="__DB_URL__" target="_blank">***</a>
<a href="__PIC__" target="_blank">__FULL__</a>"""
# Example: If you wish to link picture preview to derpibooru page
# instead of pic fullsize, replace __PIC__ with __DB_URL__
# in tmpl_spoiler_contents, tmpl_spoiler_contents_bonus, and tmpl_op_pic.

# Default values for placeholders
defaults = {
    'description':'',
    'name':'Без названия',
    'author':'неизвестный автор',
    'source_url':'неизвестен',
}

# Pics for spoiler headers (like those you see in Celestia and Luna packs):
# use None or empty array for generic text spoilers
# or an array of tabun-hosted pics URLs, like this:
spoilerpics = [
#    'https://cdn.everypony.ru/storage/06/08/97/2020/11/16/a784622ba4.png',
#    'https://cdn.everypony.ru/storage/06/08/97/2020/11/16/8c7b62a1e9.png',
#    'https://cdn.everypony.ru/storage/06/08/97/2020/11/16/51a0ceb200.png',
#    'https://cdn.everypony.ru/storage/06/08/97/2020/11/16/1451bf0db5.png',
#    'https://cdn.everypony.ru/storage/06/08/97/2020/11/16/27f426ebe2.png',
#    'https://cdn.everypony.ru/storage/06/08/97/2020/11/16/cbf5de99a4.png',
#    'https://cdn.everypony.ru/storage/06/08/97/2020/11/16/c26d9e76e1.png',
#    'https://cdn.everypony.ru/storage/06/08/97/2020/11/16/a198701934.png',
#    'https://cdn.everypony.ru/storage/06/08/97/2020/11/16/de350c0e28.png',
#    'https://cdn.everypony.ru/storage/06/08/97/2020/11/16/72f506e5df.png',
]
# If less items than requested, remaining spoilers will be text ones

# Pic for bonus block (None or '' for no picture)
bonuspic = '' # 'https://cdn.everypony.ru/storage/06/08/97/2020/11/24/21df10c0b9.png'

# Other config
timezone = '+03:00' # Timezone for searching images on Derpibooru
config = '.tabun-pack/number' # Where to store pack number (relative to '~')
pick = '.tabun_pack/test.html' # Where to create cherry-pick html (relative to '~')
period = 7 # How many days to get pics from

##############################################################################

import sys
import datetime
import json
import requests
from pathlib import Path

# tabun_api might be missing, so let user know about it
try:
    import tabun_api
except ImportError as e:
    print('Install Tabun API: pip install git+https://github.com/andreymal/tabun_api.git#egg=tabun_api[full]')
    sys.exit(1)

# A function to replace placeholders in picture block
def db_replace(string, picture, mirror, defaults):
    author = defaults['author']
    if picture['uploader'] != None:
        author = picture['uploader']
    for tag in picture['tags']:
        if 'artist:' in tag:
            author = tag.replace('artist:','')
    string = string.replace('__DESC__', picture['description'] if picture['description'] != None else defaults['description'])
    string = string.replace('__NAME__', picture['name'] if picture['name'] != None else defaults['name'])
    string = string.replace('__AUTHOR__', author)
    string = string.replace('__SOURCE__', picture['source_url'] if picture['source_url'] != None else defaults['source_url'])
    string = string.replace('__ID__', str(picture['id']))
    string = string.replace('__DB_URL__', mirror + '/images/' + str(picture['id']))
    return string

api = {
    'derpibooru': {'path': '/api/v1/json/search/images', 'jsonarray': 'images', 'jsontotal': 'total'},
    'twibooru':   {'path': '/search.json',               'jsonarray': 'search', 'jsontotal': 'total'}
}

# First, get pictures from chosen booru
def booru_get(ponytags, limit):
    date = datetime.date.today() - datetime.timedelta(days=period)
    also_fixed = also.strip()
    if also_fixed[0] != ',':
        also_fixed = ', ' + also_fixed
    dbtags = ponytags + also_fixed + ', created_at.gte:' + date.strftime('%Y-%m-%d') + timezone
    params = [('sf', sort), ('per_page', limit), ('q', dbtags)]
    proxies = {} if proxy == '' else {'https': proxy}
    print('Retrieving from', mirror, 'by tags:', dbtags)
    try:
        response = requests.get(mirror + api[apitype]['path'], params=params, proxies=proxies)
    except requests.exceptions.RequestException as e:
        print('HTTPS request error:', e)
        sys.exit(2)
    try:
        json = response.json();
    except json.JSONDecodeError as e:
        print('JSON decode error:', e)
        sys.exit(3)
    print('Retrieved', len(json[api[apitype]['jsonarray']]), 'images of', str(json[api[apitype]['jsontotal']]) + '.')
    return json

json_main = booru_get(pony, 50)
if bonuspony != '':
    json_bonus = booru_get(bonuspony + ", -" + pony, 50)

# Form a cherry-pick html data
def cherrypick_line(json):
    data = ''
    for num, picture in enumerate(json[api[apitype]['jsonarray']]):
        data += '<tr><td>' + str(num) + '</td><td><img src="' + picture['representations']['medium'] + '"></td>'
    return data

pickdata = '<html><body><h1>Main pack:</h1><table>' + cherrypick_line(json_main)
if bonuspony != '':
    pickdata += '</table><h1>Bonus pack:</h1><table>' + cherrypick_line(json_bonus)
pickdata += '</table></body></html>'

# Create a cherry-pick html
pickfile = Path(str(Path.home()) + '/' + pick)
pickfile.parent.mkdir(parents=True, exist_ok=True)
pickfile.write_text(pickdata)
print('Now open', pickfile.as_uri(), 'and choose the best pictures.')

# Get a list of pictures to put there
def cherry_pick(prompt, json):
    data = []
    numbers = input(prompt)
    if numbers != '':
        numbers = numbers.replace(';', ',').replace(',', ' ').split()
        for num in numbers:
            try:
                n = int(num)
            except ValueError:
                print('Note:', num, 'is not a number, skipped.')
                continue
            try:
                data.append(json[api[apitype]['jsonarray']][n])
            except IndexError:
                print('Note:', n, 'is out of range; maximum is', len(json[api[apitype]['jsonarray']]))
                continue
    return data

data_main = cherry_pick('Pictures for main pack: ', json_main)
if bonuspony != '':
    data_bonus = cherry_pick('Pictures for bonus pack: ', json_bonus)
if data_bonus == []:
    bonuspony = ''

# Login to Tabun
print('Logging in...')
try:
    tabun = tabun_api.User(login=username, passwd=password, proxy=proxy);
except tabun_api.TabunResultError as e:
    print('Tabun login error:', e)
    sys.exit(4)

# Upload pictures and put links into a template body
def upload_pics(data, is_bonus):
    if is_bonus:
        current_pic = 1
        caption = 'Bonus'
    else:
        current_pic = 0 # current_pic = 0 indicates OP picture
        caption = 'Main '
    block = ''
    op_pic = ''
    for picture in data:
        desc = picture['description'].replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
        if len(desc) > 50:
            desc = desc[0:50] + '(...)'
        progress = 'OP picture  ' if current_pic == 0 else caption + ' [' + str(current_pic) + ']'
        print('Uploading ' + progress + ' (' + mirror + '/images/' + str(picture['id']) + '):', desc)
        link_rep = picture['representations']['medium'] if current_pic == 0 else picture['representations']['large']
        try:
            alttext = db_replace(tmpl_alttext, picture, mirror, defaults)
            img_link = tabun.upload_image_link(link_rep, title=alttext, parse_link=False)
            img_url = tabun.upload_image_link(picture['representations']['full'], parse_link=True)
        except tabun_api.TabunError as e:
            print('Tabun upload error:', e)
            sys.exit(5)
        if current_pic == 0:
            op_pic = tmpl_op_pic.replace('__PIC__', img_url).replace('__FULL__', img_link)
            op_pic = db_replace(op_pic, picture, mirror, defaults)
        else:
            if is_bonus:
                spoiler_contents = tmpl_spoiler_contents_bonus
                if bonuspic == None or bonuspic == '':
                    spoiler_header = tmpl_text_spoiler_header_bonus
                else:
                    spoiler_header = tmpl_pic_spoiler_header_bonus.replace('__PIC__', bonuspic)
            else:
                spoiler_contents = tmpl_spoiler_contents
                if spoilerpics == None or len(spoilerpics) < current_pic:
                    spoiler_header = tmpl_text_spoiler_header
                else:
                    spoiler_header = tmpl_pic_spoiler_header.replace('__PIC__', spoilerpics[current_pic - 1])
            spoiler_header = spoiler_header.replace('___', str(current_pic))
            spoiler_contents = spoiler_contents.replace('__PIC__', img_url).replace('__FULL__', img_link).replace('___', str(current_pic))
            block += '<span class="spoiler"><span class="spoiler-title">' + spoiler_header + '</span><span class="spoiler-body">' + spoiler_contents + '</span></span>'
            block = db_replace(block, picture, mirror, defaults)
        current_pic += 1
    return block, op_pic

pic_block, op_block = upload_pics(data_main, is_bonus=False)
if bonuspony != '':
    bonus_block = upload_pics(data_bonus, is_bonus=True)[0]
else:
    bonus_block = ''
body = tmpl_body.replace('__OP_PIC__', op_block).replace('__PIC_BLOCK__', pic_block + bonus_block)

# Check pack number and set title and body placeholders
configfile = Path(str(Path.home()) + '/' + config)
if configfile.is_file():
    pack_number = int(configfile.read_text()) + 1
else:
    configfile.parent.mkdir(parents=True, exist_ok=True)
    pack_number = 1
configfile.write_text(str(pack_number))
title = title.replace('___', str(pack_number))
body = body.replace('___', str(pack_number))

# Add a post!
print('Adding a draft post:', title)
if type(blog_id) == str:
    try:
        blog_id = tabun.get_blog(blog_id).blog_id
    except tabun_api.TabunError as e:
        print('Tabun blog search error:', e)
        sys.exit(9)
try:
    blog, post_id = tabun.add_post(blog_id, title, body, tags, forbid_comment=False, draft=True)
except tabun_api.TabunError as e:
    print('Tabun posting error:', e)
    sys.exit(10)

print('New post added successfully! Link: https://tabun.everypony.ru/blog/' + str(post_id) + '.html')
# If you forgot a link, you may find it here: https://tabun.everypony.ru/topic/saved/
