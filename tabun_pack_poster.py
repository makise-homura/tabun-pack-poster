#!/usr/bin/env python3

class defcfg_class():
    # Default values
    tabun_host = 'https://tabun.everypony.ru'
    username = ''
    password = ''
    proxy = ''
    mirror = 'https://www.derpibooru.org'
    apitype = 'derpibooru'
    title = 'Пак №___'
    tags = ['пак', 'картинки']
    blog_id = 0
    pony = ''
    bonuspony = ''
    also = 'safe, -webm, -exploitable meme, -meme, -irl, -comic, -screencap, -meta, -text only'
    sort = 'wilson_score'
    tmpl_body = """
    Пришло время для ___-го пака.
    __OP_PIC__
    <cut name="Картинки здесь →">
    __PIC_BLOCK__
    """
    tmpl_text_spoiler_header = 'Спойлер ___'
    tmpl_text_spoiler_header_bonus = 'Бонус'
    tmpl_pic_spoiler_header = '<img src = "__PIC__" >'
    tmpl_pic_spoiler_header_bonus = '<img src = "__PIC__" >'
    tmpl_op_pic = """<a href="__PIC__" target="_blank">__FULL__</a>
    <a href="__DB_URL__" target="_blank">#</a> (__AUTHOR__)"""
    tmpl_alttext = '__DESC__'
    tmpl_spoiler_contents = """№ <a href="__DB_URL__" target="_blank">___</a> (__AUTHOR__)
    <a href="__PIC__" target="_blank">__FULL__</a>"""
    tmpl_spoiler_contents_bonus = """<a href="__DB_URL__" target="_blank">#</a> (__AUTHOR__)
    <a href="__PIC__" target="_blank">__FULL__</a>"""
    defaults = { 'description':'', 'name':'Без названия', 'author':'неизвестный автор', 'source_url':'неизвестен' }
    spoilerpics = []
    bonuspic = ''
    timezone = '+03:00'
    config = '.tabun-pack/number'
    backup = '.tabun-pack/post_backup.txt'
    pick = '.tabun-pack/test.html'
    period = 7
    offset = None
    pagelimit = 0
    pressenter = False

if __name__ == "main":
    from config import cfg_class
    cfg = cfg_class()
else:
    cfg = defcfg_class()

import sys
import time
import datetime
import json
import requests
import emoji
import atexit
from pathlib import Path
import http.cookiejar
import urllib.parse
import urllib.request
from http.cookies import SimpleCookie
from dateutil.relativedelta import relativedelta

# Urllib client for rentry
class UrllibClient:
    """Simple HTTP Session Client, keeps cookies."""

    def __init__(self):
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        urllib.request.install_opener(self.opener)

    def get(self, url, headers={}):
        request = urllib.request.Request(url, headers=headers)
        return self._request(request)

    def post(self, url, data=None, headers={}):
        postdata = urllib.parse.urlencode(data).encode()
        request = urllib.request.Request(url, postdata, headers)
        return self._request(request)

    def _request(self, request):
        response = self.opener.open(request)
        response.status_code = response.getcode()
        response.data = response.read().decode('utf-8')
        return response

# Register anykey handler if needed
def enterhandler():
    input('Press ENTER to continue')
if cfg.pressenter:
    atexit.register(enterhandler)

# tabun_api might be missing, so let user know about it
try:
    import tabun_api
except ImportError as e:
    print('Install Tabun API: pip install git+https://github.com/andreymal/tabun_api.git#egg=tabun_api[full]')
    sys.exit(1)

# Login to Tabun
while True:
    try:
        print('Logging in...')
        tabun = tabun_api.User(login=cfg.username, passwd=cfg.password, proxy=cfg.proxy, http_host=cfg.tabun_host)
    except tabun_api.TabunResultError as e:
        print('Tabun login error:', e)
        cont = input('Retry? [y/N]: ')
        if cont.lower() == 'y':
            print('Retrying...')
            continue
        sys.exit(4)
    except tabun_api.TabunError as e:
        print('Tabun connection error:', e)
        cont = input('Retry? [y/N]: ')
        if cont.lower() == 'y':
            print('Retrying...')
            continue
        sys.exit(4)
    break

# Check if the blog exists (and find ID for it)
blog_id = cfg.blog_id
if type(blog_id) == str:
    while True:
        try:
            print('Determining ID for blog', blog_id)
            blog_id = tabun.get_blog(blog_id).blog_id
        except tabun_api.TabunError as e:
            print('Tabun blog search error:', e)
            cont = input('Retry? [y/N]: ')
            if cont.lower() == 'y':
                print('Retrying...')
                continue
            sys.exit(9)
        break

api = {
    'derpibooru': {'path': '/api/v1/json/search/images', 'jsonarray': 'images', 'jsontotal': 'total', 'jsonname': 'name',      'imgpath': '/images/', 'addpath': False },
    'ponerpics':  {'path': '/api/v1/json/search/images', 'jsonarray': 'images', 'jsontotal': 'total', 'jsonname': 'name',      'imgpath': '/images/', 'addpath': True  },
    'twibooru':   {'path': '/search.json',               'jsonarray': 'search', 'jsontotal': 'total', 'jsonname': 'file_name', 'imgpath': '/',        'addpath': False }
}

# A function to replace placeholders in picture block
def db_replace(string, picture, mirror, defaults):
    author = defaults['author']
    if picture['uploader'] != None:
        author = picture['uploader']
    for tag in picture['tags']:
        if 'artist:' in tag:
            author = tag.replace('artist:','')
    string = string.replace('__DESC__', picture['description'] if picture['description'] != None else defaults['description'])
    string = string.replace('__NAME__', picture[api[cfg.apitype]['jsonname']] if picture[api[cfg.apitype]['jsonname']] != None else defaults['name'])
    string = string.replace('__AUTHOR__', author)
    string = string.replace('__SOURCE__', picture['source_url'] if picture['source_url'] != None else defaults['source_url'])
    string = string.replace('__ID__', str(picture['id']))
    string = string.replace('__DB_URL__', mirror + api[cfg.apitype]['imgpath'] + str(picture['id']))
    return string

# First, get pictures from chosen booru
def booru_get(ponytags):
    if (cfg.offset):
        y = cfg.offset['years'] if 'years' in cfg.offset else 0
        m = cfg.offset['months'] if 'months' in cfg.offset else 0
        d = cfg.offset['days'] if 'days' in cfg.offset else 0
        hdate = datetime.date.today() - relativedelta(years = y, months = m, days = d)
        ldate = hdate - datetime.timedelta(days=cfg.period)
        datetags = ', created_at.gte:' + ldate.strftime('%Y-%m-%d') + cfg.timezone + ', created_at.lte:' + hdate.strftime('%Y-%m-%d') + cfg.timezone
    else:
        date = datetime.date.today() - datetime.timedelta(days=cfg.period)
        datetags = ', created_at.gte:' + date.strftime('%Y-%m-%d') + cfg.timezone

    page = 1
    retrieved = 0
    limit = 50
    images = []
    also_fixed = cfg.also.strip()
    if also_fixed[0] != ',':
        also_fixed = ', ' + also_fixed
    dbtags = ponytags + also_fixed + datetags
    proxies = {} if cfg.proxy == '' else {'https': cfg.proxy}
    print('Retrieving from', cfg.mirror, 'by tags:', dbtags)
    while cfg.pagelimit == 0 or page <= cfg.pagelimit:
        print('Downloading page:', page)
        params = [('sf', cfg.sort), ('per_page', limit), ('page', page), ('q', dbtags)]
        try:
            while True:
                response = requests.get(cfg.mirror + api[cfg.apitype]['path'], params=params, proxies=proxies)
                if not response.status_code == 429:
                    break
                print('Server requested us to wait a bit...')
                time.sleep(10)
        except requests.exceptions.RequestException as e:
            print('HTTPS request error:', e)
            sys.exit(2)
        try:
            jsonpart = response.json();
        except requests.exceptions.JSONDecodeError as e:
            print('JSON decode error:', e)
            sys.exit(3)
        retrieved += len(jsonpart[api[cfg.apitype]['jsonarray']])
        print('Retrieved',  + retrieved, 'images of', str(jsonpart[api[cfg.apitype]['jsontotal']]) + '.')
        images += jsonpart[api[cfg.apitype]['jsonarray']]
        page += 1
        if len(jsonpart[api[cfg.apitype]['jsonarray']]) < limit or retrieved >= jsonpart[api[cfg.apitype]['jsontotal']]:
            break
    return images

images_main = booru_get(cfg.pony)
bonuspony = cfg.bonuspony
if bonuspony != '':
    images_bonus = booru_get(bonuspony + ", -" + cfg.pony)

# Deal with special upload protocols
if cfg.pick[:2] == '*:':
    pickproto = cfg.pick[2:]
    if pickproto == 'rentry' or pickproto == 'dpaste':
        mainheader = '# Main pack:\n\n'
        bonusheader = '# Bonus pack:\n\n'
        footer = ''
        lineleft = ''
        linemiddle = ': ![]('
        lineright = ')\n\n'
    else:
        print('Unknown special protocol:', pickproto)
        sys.exit(31)
else:
    pickproto = 'textfile'
    mainheader = '<html><body><h1>Main pack:</h1><table>'
    bonusheader = '</table><h1>Bonus pack:</h1><table>'
    footer = '</table></body></html>'
    lineleft = '<tr><td>'
    linemiddle = '</td><td><img src="'
    lineright = '"></td>'

# Form a cherry-pick html data
def cherrypick_line(images):
    data = ''
    path = cfg.mirror if api[cfg.apitype]['addpath'] else ''
    for num, picture in enumerate(images):
        data += lineleft + str(num) + linemiddle + path + picture['representations']['medium'] + lineright
    return data

pickdata = mainheader + cherrypick_line(images_main)
if bonuspony != '':
    pickdata += bonusheader + cherrypick_line(images_bonus)
pickdata += footer

# Create a cherry-pick html
def create_textfile(data):
    pickfile = Path(str(Path.home()) + '/' + cfg.pick)
    pickfile.parent.mkdir(parents=True, exist_ok=True)
    pickfile.write_text(data)
    return pickfile.as_uri()

def upload_rentry(data):
    client, cookie = UrllibClient(), SimpleCookie()
    cookie.load(vars(client.get('https://rentry.co'))['headers']['Set-Cookie'])
    csrftoken = cookie['csrftoken'].value
    payload = {'csrfmiddlewaretoken': csrftoken, 'url': '', 'edit_code': '', 'text': data}
    response = json.loads(client.post('https://rentry.co/api/new', payload, headers={"Referer": 'https://rentry.co'}).data)
    if response['status'] == '200': return response['url']
    print('Upload error: {}'.format(response['content']))
    sys.exit(32)

def upload_dpaste(data):
    r_data = {"content": data, "syntax": "md", "expiry_days": 1}
    r_headers = {"User-Agent": "Tabun Pack Poster"}
    try:
        r = requests.post("https://dpaste.com/api/", data=r_data, headers=r_headers)
        if r.status_code == 201:
            return r.text.rstrip() + '-preview'
        else:
            try:
                j = r.json();
                print('Can not upload to dpaste:', j['errors'])
                sys.exit(32)
            except json.JSONDecodeError:
                print('Can not upload to dpaste, but no valid error JSON. Response got:', r.text)
                sys.exit(32)
    except requests.exceptions.RequestException as e:
        print('Upload error: ', e)
        sys.exit(32)

if pickproto == 'textfile':
    pickfilename = create_textfile(pickdata)
if pickproto == 'rentry':
    pickfilename = upload_rentry(pickdata)
if pickproto == 'dpaste':
    pickfilename = upload_dpaste(pickdata)

print('Now open', pickfilename, 'and choose the best pictures.')

# Get a list of pictures to put there
def cherry_pick(prompt, images):
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
                data.append(images[n])
            except IndexError:
                print('Note:', n, 'is out of range; maximum is', len(images) - 1)
                continue
    return data

data_main = cherry_pick('Pictures for main pack: ', images_main)
if bonuspony != '':
    data_bonus = cherry_pick('Pictures for bonus pack: ', images_bonus)
    if data_bonus == []:
        bonuspony = ''

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
        link_rep = picture['representations']['medium'] if current_pic == 0 else picture['representations']['large']
        path = cfg.mirror if api[cfg.apitype]['addpath'] else ''
        while True:
            try:
                print('Uploading ' + progress + ' (' + cfg.mirror + api[cfg.apitype]['imgpath'] + str(picture['id']) + '):', desc)
                alttext = db_replace(cfg.tmpl_alttext, picture, cfg.mirror, cfg.defaults)
                img_link = tabun.upload_image_link(path + link_rep, title=alttext, parse_link=False)
                img_url = tabun.upload_image_link(path + picture['representations']['full'], parse_link=True)
            except tabun_api.TabunError as e:
                print('Tabun upload error:', e)
                cont = input('Retry? [y/N]: ')
                if cont.lower() == 'y':
                    print('Retrying...')
                    continue
                while True:
                    try:
                        print('Uploading large instead of full.')
                        img_url = tabun.upload_image_link(path + picture['representations']['large'], parse_link=True)
                    except tabun_api.TabunError as e:
                        print('Tabun upload error:', e)
                        cont = input('Retry? [y/N]: ')
                        if cont.lower() == 'y':
                            print('Retrying...')
                            continue
                        sys.exit(5)
                    break
            break
        if current_pic == 0:
            op_pic = cfg.tmpl_op_pic.replace('__PIC__', img_url).replace('__FULL__', img_link)
            op_pic = db_replace(op_pic, picture, cfg.mirror, cfg.defaults)
        else:
            if is_bonus:
                spoiler_contents = cfg.tmpl_spoiler_contents_bonus
                if cfg.bonuspic == None or cfg.bonuspic == '':
                    spoiler_header = cfg.tmpl_text_spoiler_header_bonus
                else:
                    spoiler_header = cfg.tmpl_pic_spoiler_header_bonus.replace('__PIC__', cfg.bonuspic)
            else:
                spoiler_contents = cfg.tmpl_spoiler_contents
                if cfg.spoilerpics == None or len(cfg.spoilerpics) < current_pic:
                    spoiler_header = cfg.tmpl_text_spoiler_header
                else:
                    spoiler_header = cfg.tmpl_pic_spoiler_header.replace('__PIC__', cfg.spoilerpics[current_pic - 1])
            spoiler_header = spoiler_header.replace('___', str(current_pic))
            spoiler_contents = spoiler_contents.replace('__PIC__', img_url).replace('__FULL__', img_link).replace('___', str(current_pic))
            block += '<span class="spoiler"><span class="spoiler-title">' + spoiler_header + '</span><span class="spoiler-body">' + spoiler_contents + '</span></span>'
            block = db_replace(block, picture, cfg.mirror, cfg.defaults)
        current_pic += 1
    return block, op_pic

pic_block, op_block = upload_pics(data_main, is_bonus=False)
if bonuspony != '':
    bonus_block = upload_pics(data_bonus, is_bonus=True)[0]
else:
    bonus_block = ''
body = cfg.tmpl_body.replace('__OP_PIC__', op_block).replace('__PIC_BLOCK__', pic_block + bonus_block)

# Check pack number and set title and body placeholders
configfile = Path(str(Path.home()) + '/' + cfg.config)
if configfile.is_file():
    pack_number = int(configfile.read_text()) + 1
else:
    configfile.parent.mkdir(parents=True, exist_ok=True)
    pack_number = 1
configfile.write_text(str(pack_number))
title = cfg.title.replace('___', str(pack_number))
body = body.replace('___', str(pack_number))

# Add a post!
while True:
    try:
        print('Adding a draft post:', title)
        blog, post_id = tabun.add_post(blog_id, title, emoji.demojize(body), cfg.tags, forbid_comment=False, draft=True)
    except tabun_api.TabunError as e:
        print('Tabun posting error:', e)
        cont = input('Retry? [y/N]: ')
        if cont.lower() == 'y':
            print('Retrying...')
            continue
        print('Saving the source to:', cfg.backup)
        backupfile = Path(str(Path.home()) + '/' + cfg.backup)
        backupfile.parent.mkdir(parents=True, exist_ok=True)
        backupfile.write_text(emoji.demojize(body), encoding="utf-8", errors="xmlcharrefreplace")
        sys.exit(10)
    break

print('New post added successfully! Link: ' + cfg.tabun_host + '/blog/' + str(post_id) + '.html')
# If you forgot a link, you may find it here: https://tabun.everypony.ru/topic/saved/ (or on some other of tabun mirrors)
