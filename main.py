# -*- coding: utf-8 -*-
import os, datetime
from doubanreader import DBRClient, DBUser
import template


user = DBUser()
client = DBRClient(user)

if not client.isAuth():
    client.auth()

print u'您已经是认证用户:)'

year = 0
month = 0

while True:
    try:
        print u'输入格式：'
        print u'1.直接输入月份生成当年该月的读书报告。'
        print u'2.直接输入年份生成该年的全年读书报告。'
        print u'3.输入格式为xxxx.xx生成指定年份指定月份的读书报告。\n'
        s = raw_input(u'请输入您需要生成的读书报告：'.encode('utf-8'))
        if s.find('.') != -1:
            year = int(s.split('.')[0])
            month = int(s.split('.')[1])
        elif len(s) == 4:
            year = int(s)
        else:
            month = int(s)
    except Exception, e:
        print u'您的输入有误！'
    else:
        break

if year == 0:
    year = datetime.date.today().year

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

print 'Number of books: %s' % len(collections)

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
