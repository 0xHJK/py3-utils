#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, os, sys, time, random, getopt
from pyquery import PyQuery as pq
from bosonnlp import BosonNLP

NODE_URL = 'https://www.zhihu.com/node/QuestionAnswerListV2'
PAGESIZE = 10
MAX_COUNT = 50
DEFAULT_KEY = '1pzQ3lO3.8646.kLm3DFG9Lwxa'
DEFAULT_LEVEL = 2
FORCE = False
USAGE = ('usage: python3 zhihu-get.py -u <url> -k <bosonnlp_api_key> -c [count] -l [level] [--force]\n\n'
	'level=0: Location Only;\n'
	'level=1: Person Only;\n'
	'level=2: Product Only;\n'
	'level=3: Company & Organization;\n'
	'level=4: level2+level3;\n'
	'level=5: Keyword Base\n'
	'level=6: Keyword Advanced'
	'level=9: level4＋level6;\n'
	'default level=2;\n\n')

def printAuthor():
	print('\n' + '*' * 50)
	print('*')
	print('* Author: HJK')
	print('* GitHub: https://github.com/0xHJK')
	print('*')
	print('*' * 50 + '\n')

def getArgs():
	zhihu_args = {
		'key': DEFAULT_KEY,
		'level': DEFAULT_LEVEL,
		'count': MAX_COUNT,
		'force': FORCE
	}
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hfu:k:c:l:', ['help', 'url=', 'key=', 'count=', 'level=', 'force'])
	except getopt.GetoptError as e:
		print(USAGE)
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			print(USAGE)
			sys.exit()
		elif opt in ('-u', '--url'):
			zhihu_args['url'] = arg
		elif opt in ('-k', '--key'):
			zhihu_args['key'] = arg
		elif opt in ('-c', '--count'):
			zhihu_args['count'] = int(arg)
		elif opt in ('-l', '--level'):
			zhihu_args['level'] = int(arg)
		elif opt in ('-f', '--force'):
			zhihu_args['force'] = True
	if not ('url' in zhihu_args):
		print(USAGE)
		sys.exit(2)
	print(zhihu_args)
	return zhihu_args

def readFileLines(filename):
	try:
		with open(filename, 'r') as f:
			lines = f.readlines()
	except:
		lines = ['']
	return lines

def saveFileLines(filename, lines):
	print('正在保存%s文件……' % filename)
	with open(filename, 'w') as f:
		f.writelines(lines)

def sortList (ul):
	ul2 = list(set(ul))
	ul3 = []
	for item in ul2:
		t = (item, ul.count(item))
		ul3.append(t)
	def by_count(t):
		return t[1]
	return sorted(ul3, key = by_count, reverse = True)

def getAnswerKeys (text_set, api_key):
	keys = []
	nlp = BosonNLP(api_key)
	result = nlp.extract_keywords(text_set, top_k=30)
	for weight, word in result:
		keys.append((word, int(weight*10)))
	return keys

def getAnswerNounKeys(text_set, api_key):
	nlp = BosonNLP(api_key)
	result = nlp.tag(text_set)
	words = ''
	for d in result:
		for it in zip(d['word'], d['tag']):
			if it[1] == 'n':
				words += it[0]
			# print(' '.join([ '%s/%s' % it]))
	return getAnswerKeys(words, api_key)

def getAnswerEntities(text_set, api_key, level):
	def f(x):
		return {
			'0': 'location',
			'1': 'person_name',
			'2': 'product_name',
			'3': ('org_name', 'company_name'),
			'4': ('product_name', 'org_name', 'company_name'),
		}[str(x)]
	nlp = BosonNLP(api_key)
	result = nlp.ner(text_set)[0]
	words = result['word']
	entities = result['entity']
	ul = []
	for entity in entities:
		if (entity[2] == f(level) or entity[2] in f(level)):
			ul.append(''.join(words[entity[0]:entity[1]]))
	keys = sortList(ul)
	return keys

def getNLPAnalysis(text_set, api_key, level):
	results = []
	keys_list = []
	i = 1
	if level < 5:
		results = getAnswerEntities(text_set, api_key, level)
	elif level == 5:
		results = getAnswerKeys(text_set, api_key)
	elif level == 6:
		results = getAnswerNounKeys(text_set, api_key)
	elif level == 9:
		results_temp = getAnswerEntities(text_set, api_key, 4) + getAnswerNounKeys(text_set, api_key)
		def by_count(t):
			return t[1]
		results = sorted(results_temp, key = by_count, reverse = True)
	for result in results:
		keys_list.append('No.%s  %s  (%s)\n' % (str(i), result[0], str(result[1])))
		i += 1
	return ''.join(keys_list)

def getAnswers(offset, url_token, headers, cookies):
	text = ''
	data = {
		'method': 'next',
		'params': '{"url_token":' + url_token + ',"pagesize":' + str(PAGESIZE) + ',"offset":' + str(offset) + '}'
	}
	r = requests.post(NODE_URL, headers = headers, cookies = cookies, data = data)
	if r.status_code == 200:
		answers = r.json()['msg']
		for answer in answers:
			d = pq(answer)
			text = text + d('.zm-editable-content').text() + '\n'
	return text

def getZhihuAnswers(url_token, zhihu_args):
	answers_info = []
	text_set = ''
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
	while (offset < count and offset < zhihu_args['count']):
		print('正在获取第', offset + 1, '个回答到第', offset + 10, '个回答')
		text_set = text_set + getAnswers(offset, url_token, headers, cookies)
		offset += PAGESIZE
		time.sleep(random.random())
	answers_info.append(title + '\n')
	answers_info.append(zhihu_args['url'] + '\n')
	answers_info.append(str(count) + '\n')
	answers_info.append(text_set + '\n')
	return answers_info

def main(zhihu_args):
	url_token = zhihu_args['url'].split('/')[-1]
	answers_file = url_token + '.txt'
	keys_file = url_token + '_l' + str(zhihu_args['level']) + '.txt'
	# 获取并保存回答
	def getAndSaveAnswers(url_token, answers_file):
		answers_info = getZhihuAnswers(url_token, zhihu_args)
		saveFileLines(answers_file, answers_info)
		return answers_info
	# 获取并保存关键字
	def getAndSaveKeys(answers_info, keys_file):
		keys_info = []
		keys_info.append(answers_info[0])
		keys_info.append(answers_info[1])
		keys_info.append(getNLPAnalysis(answers_info[-1], zhihu_args['key'], zhihu_args['level']))
		saveFileLines(keys_file, keys_info)
		return keys_info
	# 尝试从本地获取文件
	if not zhihu_args['force']:
		keys_info = readFileLines(keys_file)
		# 如果关键字不存在
		if len(keys_info[-1]) < 1:
			answers_info = readFileLines(answers_file)
			# 如果知乎回答不存在
			if len(answers_info[-1]) < 1:
				answers_info = getAndSaveAnswers(url_token, answers_file)
			# 获取并保存关键字
			keys_info = getAndSaveKeys(answers_info, keys_file)
	else:
		answers_info = getAndSaveAnswers(url_token, answers_file)
		keys_info = getAndSaveKeys(answers_info, keys_file)
	# 输出结果
	print('\033[95m', keys_info[0],  end = '')
	print('\033[0m', keys_info[1],  end = '')
	for key in keys_info[2:]:
		print('\033[93m', key)
		# 不知道为什么分割字符串不行……感觉很奇怪
		# ks = key.split('  ')
		# print('\033[94m%s \033[93m%s \033[0m%s' % (ks[0], ks[1], ks[2]), end = '')

if __name__ == '__main__':
	printAuthor()
	main(getArgs())

