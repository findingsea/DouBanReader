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
        month = int(raw_input(u'请选择月份，输入0代表全年：'.encode('utf-8')))
    except Exception, e:
        print u'您的输入有误！'
    else:
        break

year = datetime.date.today().year

collections = client.getUserBookCollections(year, month)

path = str(year) + '/' + str(month)
if not os.path.exists(path):
    os.makedirs(path)
filename = template.MARKDOWN_TEMPLATE_TITLE % {'year': year, 'month': month} + '.md'
mk_file = open(path + '/' + filename, 'w+r')

mk_file.write(template.MARKDOWN_TEMPLATE_INTRODUCTION)
mk_file.write('\n\n')

title = template.MARKDOWN_TEMPLATE_TITLE % {'year': year, 'month': month}
mk_file.write(client.covertToUTF8(title))
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

    section_title = template.MARKDOWN_TEMPLATE_SECTION_TITLE % book
    mk_file.write(client.covertToUTF8(section_title))
    mk_file.write('\n\n')

    section_picture = template.MARKDOWN_TEMPLATE_SECTION_PICTURE % book
    mk_file.write(client.covertToUTF8(section_picture))
    mk_file.write('\n\n')

    mk_file.write(client.covertToUTF8(client.getUserBookReview(book['id'])))
    mk_file.write('\n\n')

mk_file.close()
