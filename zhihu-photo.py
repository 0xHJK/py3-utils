#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Usage: python3 zhihu-photo.py https://www.zhihu.com/question/25361867

import requests
import os
import sys
import io
import time
import random
from pyquery import PyQuery as pq

q_url = ''
z_url = 'https://www.zhihu.com'
n_url = z_url + '/node/QuestionAnswerListV2'
url_token = ''
dir_name = ''
pagesize = 10
offset = 0
cookies = {}
headers = {
	'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36',
	'Accept': '*/*',
	'Accept-Encoding': 'gzip, deflate, br'
}

def savePhotos (photos, name, answer_id):
	for i in photos:
		d = pq(i)
		src = d('img').attr('data-original') or d('img').attr('data-actualsrc')
		print('正在获取图片:', src)
		filename = answer_id + '_' + name + '_' + src.split('/')[-1]
		photo = requests.get(src)
		with open(filename, 'wb') as f:
			f.write(photo.content)
			f.close()
		time.sleep(random.random())

def getAnswerPhotos (r):
	for i in r['msg']:
		d = pq(i)
		answer_link = d('.answer-date-link').attr('href')
		answer_id = answer_link.split('/')[-1]
		name = d('.author-link').text() or '匿名用户'
		photos = d('.zm-item-rich-text img.lazy')
		if photos:
			print('\n正在获取', name, '的回答，链接为：', answer_link)
			savePhotos(photos, name, answer_id)

def getAnswers (offset):
	data = {
		'method': 'next',
	  'params': '{"url_token":' + url_token + ',"pagesize":' + str(pagesize) + ',"offset":' + str(offset) + '}',
	}
	r = requests.post(n_url, headers = headers, cookies = cookies, data = data)
	getAnswerPhotos(r.json())

if __name__ == '__main__':
	print('\n' + '*' * 50)
	print('*')
	print('* Author: HJK')
	print('* GitHub: https://github.com/0xHJK')
	print('*')
	print('*' * 50 + '\n')
	try:
		q_url = sys.argv[1]
	except IndexError as e:
		q_url = input('请输入知乎问题地址（如 https://www.zhihu.com/question/25361867）：\n')
	url_token = dir_name = q_url.split('/')[-1]
	if not os.path.exists(dir_name):
		os.mkdir(dir_name)
	os.chdir(dir_name)
	print('\n开始获取问题信息……')
	r = requests.get(q_url, headers = headers, cookies = cookies)
	d = pq(r.text)
	_xsrf = d('input[name="_xsrf"]').val()
	count = int(d('#zh-question-answer-num').attr('data-num'))
	print('\n该问题下共有', count, '个回答')
	# 设置headers和cookies
	headers['X-Requested-With'] = 'XMLHttpRequest'
	headers['X-Xsrftoken'] = _xsrf
	cookies['_xsrf'] = _xsrf
	while offset < count:
		try:
			print('\n开始获取第', offset+1, '个回答到第', offset+10, '个回答的图片')
			getAnswers(offset)
			offset += pagesize
		except KeyboardInterrupt as e:
			print('\n进程中断')
			break
	print('\n运行结束，已获取图片以ID_用户名_原始名称命名')