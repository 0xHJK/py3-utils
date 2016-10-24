#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from openpyxl import Workbook
from pyquery import PyQuery as pq

URL = 'http://epub.sipo.gov.cn/patentoutline.action'
HEADERS = { 'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36' }
KEYWORD = '区块链'

def getPatents(page):
	res = []
	data = {
		'showType': '1',
		'strSources': 'pip',
		'strWhere': 'PA,IN,AGC,AGT+="%区块链%" or PAA,TI,ABH+="区块链"',
		'numSortMethod': '4',
		'strLicenseCode': '',
		'numIp': '38',
		'numIpc':'',
		'numIg': '1',
		'numIgc': '',
		'numIgd': '',
		'numUg': '2',
		'numUgc': '',
		'numUgd': '',
		'numDg': '0',
		'numDgc': '',
		'pageSize':'10',
		'pageNow': page
	}
	r = requests.post(URL, headers = HEADERS, data = data)
	d = pq(r.text)
	cps = d('.cp_box')
	for cp in cps:
		info = []
		title = d(cp).find('h1').text()
		print(title)
		info.append(title.split(']')[1].strip())
		etc = d(cp).find('li')
		i = 0
		while i < 8:
			txt = d(d(etc)[i]).text()
			if txt:
				info.append(txt.split('：')[1])
			i += 1
		res.append(info)
	print(res)
	return(res)

def saveExcel(patents):
	wb = Workbook()
	ws = wb.active
	ws.append(['标题', '申请公布号', '申请公布日', '申请号', '申请日', '申请人', '发明人', '地址'])
	for p in patents:
		ws.append(p)
	wb.save('patents.xlsx')

def main():
	patents = []
	i = 1
	while i < 5:
		patents += getPatents(i)
		i += 1
	saveExcel(patents)

if __name__ == '__main__':
	main()