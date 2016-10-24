#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Usage: python3 lol-down.py
# 2016-07-19 已被腾讯屏蔽

import requests
from bs4 import BeautifulSoup

def getlinks():
	print('正在获取版本信息……')
	r = requests.get('http://lol.qq.com/download.shtml')
	r.encoding = 'gb2312'
	soup = BeautifulSoup(r.text, 'html.parser')
	info = soup.find('p', attrs={'class':'downinfo'}).text
	ver = info.split(' | ')[0].split('：')[1]
	print('开始扫描真实下载地址……')
	links = []
	links.append('http://down.qq.com/lol/full/LOL_%s_FULL.exe' % ver)
	p = 1
	while True:
		link = 'http://down.qq.com/lol/full/LOL_%s_FULL.7z.%03d' % (ver, p)
		r = requests.head(link, allow_redirects=True)
		if r.status_code == 200:
			links.append(link)
			p += 1
		else:
			break
	print('以下是当前版本完整安装包的下载地址：')
	for x in links:
		print(x)
	
getlinks()
