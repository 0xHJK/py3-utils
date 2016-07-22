#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Usage: python3 zhihu-photos.py -u https://www.zhihu.com/question/25361867

import requests, os, sys, time, random, getopt
from pyquery import PyQuery as pq

NODE_URL = 'https://www.zhihu.com/node/QuestionAnswerListV2'
PAGESIZE = 10
MAX_COUNT = 0
# 暂时没卵用
FORCE = True
USAGE = 'usage: python3 zhihu-photos.py -u <url> -c [count] [--force]'

def printAuthor():
	print('\n' + '*' * 50)
	print('*')
	print('* Author: HJK')
	print('* GitHub: https://github.com/0xHJK')
	print('*')
	print('*' * 50 + '\n')

def getArgs():
	zhihu_args = {
		'count': MAX_COUNT,
		'force': FORCE
	}
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hfu:c:', ['help', 'force', 'url=', 'count='])
	except getopt.GetoptError as e:
		print(USAGE)
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			print(USAGE)
			sys.exit()
		elif opt in ('-u', '--url'):
			zhihu_args['url'] = arg
		elif opt in ('-c', '--count'):
			zhihu_args['count'] = int(arg)
		elif opt in ('-f', '--force'):
			zhihu_args['force'] = True
	if not ('url' in zhihu_args):
		print(USAGE)
		sys.exit(2)
	print(zhihu_args)
	return zhihu_args

def saveFileBit(filename, file):
	print('正在保存\033[94m%s\033[0m文件……' % filename)
	with open(filename, 'wb') as f:
		f.write(file)

def getAndSavePhotos(offset, url_token, headers, cookies):
	photos = []
	data = {
		'method': 'next',
		'params': '{"url_token":' + url_token + ',"pagesize":' + str(PAGESIZE) + ',"offset":' + str(offset) + '}'
	}
	r = requests.post(NODE_URL, headers = headers, cookies = cookies, data = data)
	if r.status_code == 200:
		answers = r.json()['msg']
		for answer in answers:
			d = pq(answer)
			pre_name = d('.answer-date-link').attr('href').split('/')[-1] + '_' + (d('.author-link').text() or '匿名用户') + '_'
			imgs = d('.zm-item-rich-text img.lazy')
			urls = []
			if imgs:
				for img in imgs:
					src = d(img).attr('data-original') or d(img).attr('data-actualsrc')
					photo = requests.get(src)
					if photo.status_code == 200:
						saveFileBit(pre_name + src.split('/')[-1], photo.content)
					urls.append(src + '\n')
					time.sleep(random.random())
				photos += urls
	return photos

def getZhihuAnswers(url_token, zhihu_args):
	answers_info = []
	photos = []
	offset = 0
	cookies = {}
	headers = { 'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36' }
	r = requests.get(zhihu_args['url'], headers = headers, cookies = cookies)
	d = pq(r.text)
	_xsrf = d('input[name="_xsrf"]').val()
	count = int(d('#zh-question-answer-num').attr('data-num'))
	title = d('#zh-question-title').text()
	headers['X-Requested-With'] = 'XMLHttpRequest'
	headers['X-Xsrftoken'] = _xsrf
	cookies['_xsrf'] = _xsrf
	while (offset < count and (zhihu_args['count'] < 1 or offset < zhihu_args['count'])):
		print('正在获取第', offset + 1, '个回答到第', offset + 10, '个回答')
		photos = photos + getAndSavePhotos(offset, url_token, headers, cookies)
		offset += PAGESIZE
		time.sleep(random.random())
	answers_info.append(title)
	answers_info.append(zhihu_args['url'])
	answers_info.append(str(count))
	answers_info.append(photos)
	return answers_info

def main(zhihu_args):
	url_token = zhihu_args['url'].split('/')[-1]
	if not os.path.exists(url_token):
		os.mkdir(url_token)
	os.chdir(url_token)
	answers_info = getZhihuAnswers(url_token, zhihu_args)
	print('\n\033[0m问题\033[95m%s' % answers_info[0])
	print('\033[0m链接\033[95m%s' % answers_info[1])
	print('\033[0m共计\033[94m%s\033[0m个回答，\033[94m%d\033[0m张图片' % (answers_info[2], len(answers_info[-1])))
	print('已获取图片以ID_用户名_原始名称命名，保存在\033[94m%s\033[0m文件夹( ´ ▽ ` )ﾉ\n' % url_token)

if __name__ == '__main__':
	printAuthor()
	main(getArgs())
