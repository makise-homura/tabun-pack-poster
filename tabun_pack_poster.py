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
# If less items than piclimit, remaining spoilers will be text ones

# Pic for bonus block (None or '' for no picture)
bonuspic = '' # 'https://cdn.everypony.ru/storage/06/08/97/2020/11/24/21df10c0b9.png'

# Other config
timezone = '+03:00' # Timezone for searching images on Derpibooru
config = '.tabun-pack/number' # Where to store pack number (relative to '~')
period = 7 # How many days to get pics from
piclimit = 15 # How many pictures to retrieve (not including OP pic, max 49)
bonuslimit = 3 # How many pictures to retrieve for bonus section

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

# First, get pictures from Derpibooru
def derpibooru_get(ponytags, limit):
    date = datetime.date.today() - datetime.timedelta(days=period)
    also_fixed = also.strip()
    if also_fixed[0] != ',':
        also_fixed = ', ' + also_fixed
    dbtags = ponytags + also_fixed + ', created_at.gte:' + date.strftime('%Y-%m-%d') + timezone
    params = [('sf', sort), ('per_page', limit), ('q', dbtags)]
    proxies = {} if proxy == '' else {'https': proxy}
    print('Retrieving from derpibooru by tags:', dbtags)
    try:
        response = requests.get(mirror + '/api/v1/json/search/images', params=params, proxies=proxies)
    except requests.exceptions.RequestException as e:
        print('HTTPS request error:', e)
        sys.exit(2)
    try:
        json = response.json();
    except json.JSONDecodeError as e:
        print('JSON decode error:', e)
        sys.exit(3)
    total = len(json['images'])
    print('Retrieved', total, 'images of', str(json['total']) + '.')
    return json, total

json_main, total_main = derpibooru_get(pony, piclimit + 1)
if bonuslimit > 0:
    json_bonus, total_bonus = derpibooru_get(bonuspony + ", -" + pony, bonuslimit)

# Login to Tabun
print('Logging in...')
try:
    tabun = tabun_api.User(login=username, passwd=password, proxy=proxy);
except tabun_api.TabunResultError as e:
    print('Tabun login error:', e)
    sys.exit(4)

# Upload pictures and put links into a template body
def upload_pics(json, total, is_bonus):
    if is_bonus:
        current_pic = 1
        caption = 'Bonus'
    else:
        current_pic = 0 # current_pic = 0 indicates OP picture
        total -= 1 # Skip OP pic from counting
        caption = 'Main '
    block = ''
    op_pic = ''
    for picture in json['images']:
        desc = picture['description'].replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
        if len(desc) > 50:
            desc = desc[0:50] + '(...)'
        progress = 'OP picture  ' if current_pic == 0 else caption + ' [' + str(current_pic) + '/' + str(total) + ']'
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

pic_block, op_block = upload_pics(json_main, total_main, is_bonus=False)
if bonuslimit > 0:
    bonus_block = upload_pics(json_bonus, total_bonus, is_bonus=True)[0]
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
