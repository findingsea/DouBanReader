# -*- coding: utf-8 -*-
import re, json, os, urllib
import requests


class DBUser:

    name = ''
    id = ''
    uid = ''
    authorization_code = ''
    access_token = ''
    refresh_token = ''

    def __init__(self):
        if os.path.isfile(USER_INFO_FILE):
            pre_file = open(USER_INFO_FILE, 'r')
        else:
            pre_file = open(USER_INFO_FILE, 'w+r')
        pre_file_read = pre_file.read()
        pre_file.close()
        if pre_file_read.strip():
            user_info = json.loads(pre_file_read.strip())
            self.name = user_info['name']
            self.id = user_info['id']
            self.uid = user_info['uid']
            self.authorization_code = user_info['authorization_code']
            self.access_token = user_info['access_token']
            self.refresh_token = user_info['refresh_token']

    def save(self):
        pre_file = open(USER_INFO_FILE, 'w')
        user_info = {}
        user_info['name'] = self.name
        user_info['id'] = self.id
        user_info['uid'] = self.uid
        user_info['authorization_code'] = self.authorization_code
        user_info['access_token'] = self.access_token
        user_info['refresh_token'] = self.refresh_token
        pre_file.write(json.dumps(user_info))
        pre_file.close()


class DBRClient:

    user = None

    def __init__(self, user):
        self.user = user

    def isAuth(self):
        if self.user.authorization_code and self.user.access_token:
            return True
        else:
            return False

    def auth(self):

        params = {}
        params['client_id'] = CLIENT_ID
        params['redirect_uri'] = REDIRECT_URI
        params['response_type'] = 'code'
        params['scope'] = SCOPE

        print u'请访问如下地址，点击确认后，复制跳转的网址到下面：' + AUTHORIZATION_CODE_URL \
            + '?' + urllib.urlencode(params)

        authorization_code = re.match(\
            u'(.*)code=(.*)', \
            raw_input(u'跳转网址：'.encode('utf-8')).strip()\
        ).group(2)

        params = {'client_id': CLIENT_ID, 'client_secret': SECRET, \
            'redirect_uri': REDIRECT_URI, 'grant_type': 'authorization_code', \
            'code': authorization_code}
        res = requests.post(\
            url=ACCESS_TOKEN_URL, data=params, \
            headers={'Content-Type': 'application/x-www-form-urlencoded'}\
        ).json()

        self.user.authorization_code = authorization_code
        self.user.access_token = res['access_token']
        self.user.refresh_token = res['refresh_token']

        res = requests.get(\
            url=AUTH_USER_INFO_URL, \
            headers={\
                'Authorization': 'Bearer ' + self.user.access_token\
            }\
        ).json()

        self.user.id = res['id']
        self.user.uid = res['uid']
        self.user.name = res['name']

        self.user.save()

    def getUserBookCollections(self, year, month):
        if month == 0:
            params = {\
                'status': 'read', \
                'from': '%d-01-01T00:00:00+08:00', \
                    % (year)
                'to': '%d-01-01T00:00:00+08:00', \
                    % (year + 1)
            }
        else:
            params = {\
                'status': 'read',\
                'from': '%d-%02d-01T00:00:00+08:00' \
                    % (year, month),\
                'to': '%d-%02d-01T00:00:00+08:00' \
                    % (year if month < 12 else year + 1, \
                        month + 1 if month < 12 else 1)\
            }

        res = requests.get(USER_BOOK_COLLECTIONS_URL % self.user.id, \
            params=params
        )
        return res.json()['collections']

    def getUserBookReview(self, book_id):
        review_content = ''
        start = 0
        total = 100
        while start < total:
            res = requests.get(BOOK_REVIEWS_URL % book_id, \
                params={'count': 100, 'start': start}).json()
            review_alt = ''
            for review in res['reviews']:
                if review['author']['id'] == self.user.id:
                    review_alt = review['alt']
                else:
                    continue
            if review_alt:
                review_content = self.getReivew(review_alt)
                break
            total = res['total']
            start = start + 100
        return review_content

    def getReivew(self, url):
        res = requests.get(url)
        res_text = res.text.replace(u'\u3000', '')
        c = re.compile('\s+')
        res_text = re.sub(c, '', res_text)
        pattern = u'(.*)<spanproperty="v:description"class="">(.*?)</span>(.*)'
        content = re.match(pattern, res_text).group(2)
        content = content.replace('<br/>', '\n')
        return content

    def covertToUTF8(self, content):
        return content.encode('utf-8')

USER_INFO_FILE = 'user_info.txt'
CLIENT_ID = '022edc4b51cf759d068c94e1f56e60d7'
API_KEY = CLIENT_ID
SECRET = 'bfeee4fbd1b29e6c'
REDIRECT_URI = 'http://findingsea.github.io'

AUTHORIZATION_CODE = 'authorization_code'
ACCESS_TOKEN = 'access_token'
REFRESH_TOEKN = 'refresh_token'
DOUBAN_USER_ID = 'id'
DOUBAN_USER_UID = 'uid'
DOUBAN_USER_NAME = 'name'

ACCESS_TOKEN_URL = 'https://www.douban.com/service/auth2/token'
AUTHORIZATION_CODE_URL = 'https://www.douban.com/service/auth2/auth?'
SCOPE = 'shuo_basic_r,shuo_basic_w,douban_basic_common'
AUTH_USER_INFO_URL = 'https://api.douban.com/v2/user/~me'
USER_BOOK_COLLECTIONS_URL = 'https://api.douban.com/v2/book/user/%s/collections'
BOOK_REVIEWS_URL = 'https://api.douban.com/v2/book/%s/reviews'
