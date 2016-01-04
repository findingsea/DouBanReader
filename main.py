# -*- coding: utf-8 -*-
import os, datetime
from doubanreader import DBRClient, DBUser
import template


user = DBUser()
client = DBRClient(user)

if not client.isAuth():
    client.auth()

print u'您已经是认证用户:)'

while True:
    try:
        month = int(raw_input(u'请选择月份，或者直接输入年份生成全年的阅读报告：'.encode('utf-8')))
    except Exception, e:
        print u'您的输入有误！'
    else:
        break

if 1 <= month and month <= 12:
    year = datetime.date.today().year
else:
    year = month
    month = 0

collections = client.getUserBookCollections(year, month)

path = str(year) + '/' + str(month)
if not os.path.exists(path):
    os.makedirs(path)

if month != 0:
    filename = template.MARKDOWN_TEMPLATE_TITLE % {'year': year, 'month': month} + '.md'
else:
    filename = template.MARKDOWN_TEMPLATE_WHOLE_YEAR_TITLE % year + '.md'

mk_file = open(path + '/' + filename, 'w+r')

introduction = template.MARKDOWN_TEMPLATE_INTRODUCTION

mk_file.write(client.convertToUTF8(introduction))
mk_file.write('\n\n')

for info in collections:
    book = {}
    book['id'] = info['book']['id']
    book['title'] = info['book']['title']
    book['alt'] = info['book']['alt']
    book['image'] = info['book']['image']
    if info['book']['images'].has_key('large'):
        book['image'] = info['book']['images']['large']
    elif info['book']['images'].has_key('medium'):
        book['image'] = info['book']['images']['medium']

    if month == 0:
        section_title = template.MARKDOWN_TEMPLATE_WHOLE_YEAR_SECTION_TITLE % book
    else:
        section_title = template.MARKDOWN_TEMPLATE_SECTION_TITLE % book

    mk_file.write(client.convertToUTF8(section_title))
    if month == 0:
        mk_file.write(' ' + info['updated'].split()[0])
    mk_file.write('\n\n')

    if month != 0:
        section_picture = template.MARKDOWN_TEMPLATE_SECTION_PICTURE % book
        mk_file.write(client.convertToUTF8(section_picture))
        mk_file.write('\n\n')

        mk_file.write(client.convertToUTF8(client.getUserBookReview(book['id'])))
        mk_file.write('\n\n')

mk_file.close()
