#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Usage: python3 douban-top250.py [start]

import requests
import sys
import time
import random
import webbrowser
from pyquery import PyQuery as pq

top_url = 'https://movie.douban.com/top250'
start = 0
pagesize = 25
count = 250
headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36'
}

def printAuthor ():
	print('\n' + '*' * 50)
	print('*')
	print('* Author: HJK')
	print('* GitHub: https://github.com/0xHJK')
	print('*')
	print('*' * 50 + '\n')

def saveCurrent (current):
	with open('douban-top250.txt', 'w') as f:
		f.write(current)
		f.close()

def getCurrent ():
	try:
		start = int(sys.argv[1]) - 1
		return start
	except IndexError as e:
		try:
			with open('douban-top250.txt', 'r') as f:
				start = f.read()
				f.close()
				return start
		except:
			start = 0
	# print(start)
	return start

def getMovieDetail (movie_url):
	r = requests.get(movie_url, headers = headers)
	if r.status_code == 200:
		d = pq(r.text)
		sources = d('.bs li')
		def playMovie (link):
			no = d('.top250-no').text()
			title = d('h1').text()
			rating_num = d('.rating_num').text()
			info = d('#info').text()
			summary = d('#link-report').text()
			current = str(no.split('.')[1])
			print('\033[95m', no, title, rating_num)
			print('\033[94m', info)
			print('\033[93m', summary)
			print('\033[0m', '播放地址：', link, '\n')
			print('老大，是否要播放？')
			play = input('(y)给老子打开\n(n)老子现在不想看，下一个\n')
			if play == 'y':
				webbrowser.open_new(link)
				saveCurrent(current)
				print('开始播放', title, '\n程序将自动记录位置，下次搜索默认将从此片开始')
				sys.exit(0)
			else:
				return True
		for source in sources:
			if d(source).find('.buylink-price').text() == '免费':
				link = d(source).find('.playBtn').attr('href')
				playMovie(link)
				break
			else:
				if source == sources[-1]:
					print('要付钱，放不起，下一个')

def getPlayableMovies (start):
	payload = { 'start': start }
	r = requests.get(top_url, headers = headers, params = payload)
	d = pq(r.text)
	movies = d('.grid_view li')
	for movie in movies:
		movie_name = d(movie).find('.hd').text()
		movie_no = 'No.' + d(movie).find('.pic em').text()
		if d(movie).find('.playable'):
			movie_url = d(movie).find('.hd a').attr('href')
			print('\n', movie_no, '正在获取播放资源', movie_name, movie_url)
			time.sleep(random.random())
			getMovieDetail(movie_url)
		else:
			print('\n', movie_no, '不可播放', movie_name)


if __name__ == '__main__':
	printAuthor()
	start = int(getCurrent())
	print('开始获取豆瓣电影TOP250中免费资源，当前从第', start + 1, '部开始获取')
	while start < 250:
		getPlayableMovies(start)
		start += pagesize
	