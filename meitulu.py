#!/usr/bin/env python
#coding:utf-8

from pyquery import PyQuery
from tools import GrabBase,Common
import json
import re

class grab(GrabBase,object):

	def __init__(self,):
		super(grab, self).__init__('http://www.meitulu.com')
		

	def items(self):
		url = self.domain + '/item'

		allItems = {}
		#网站index in (3,6209)
		start = 5040
		for index in range(start,start+20) :
			item = {}

			link = url+'/{index}.html'.format(index=index)
			self.url = link
			response = self.Get(link)

			pyhtml = PyQuery(response.content)

			imgLinks = self.GetImgLinks(pyhtml)

			pageNum = self.GetPageNum(pyhtml)
			modelName = self.GetModelName(pyhtml)
			modelInfo = self.GetModelInfo(pyhtml)

			print 'link',link
			print 'modelName',modelName
			print '\n'

			item.update(modelName=modelName,modelInfo=modelInfo,link=link,pageNum=pageNum,imgLinks=imgLinks)

			if modelName not in allItems :
				allItems.update({modelName:[item]})
			else :
				allItems[modelName].append(item)

		return allItems


	def GetModelName(self,pyhtml):
		elements = pyhtml('.readinfo p')

		for ele in elements.items() :
			text = unicode(ele.text())

			if u'姓名' in text :
				text = text.split(u'：')[1].strip()
				break
		else :
			text = pyhtml('title').text()
			text = text.split()[0]

			if '-' in text :
				text = text.split('-')[0]

		return text

	def GetModelInfo(self,pyhtml):
		elements = pyhtml('.readinfo p')

		allInfo = {}
		infos = []
		if elements :
			txt = ''
			for p in elements.items() :
				text = unicode(p.text())
				info = {}
				name = text.split(u'：')[0].strip() if u'：' in text else ''
				value = text.split(u'：')[1].strip() if u'：' in text else ''

				info.update(name=name,text=value)

				if Common.HasElementTag(p,'a') :
					if len(p('a')) > 1 :
						urls = [a.attr('href') for a in p('a').items()]
						info.update(url=urls)
					else :
						info.update(url=p('a').attr('href'))

				infos.append(info)

				txt += (p.text()+';      ')

			allInfo.update(attr=infos,txt=txt)
			return allInfo

		return []
		raise ValueError,'Get ModelInfo Fail , url is {url}'.format(url=self.url)

	def GetImgLinks(self,pyhtml):
		elements = pyhtml('.content img')

		links = [img.attr('src') for img in elements.items()]

		if links :
			return links

		return []
		raise ValueError,'Get ImgLinks Fail, url is {url}'.format(url=self.url)

	def GetPageNum(self,pyhtml):
		element = pyhtml('#pages>a:last').prev()

		href = element.attr('href')

		if href :
			pages = re.search(r'/\d*_(\d*).html',href).groups()[0]
			pages = int(pages)

			return pages

		return 0
		raise ValueError,'Get Pages Fail , url is {url}'.format(url=self.url)




if __name__ == '__main__':
	drag = grab()
	allItems = drag.items()
	jsonStr = json.dumps(allItems)

	print jsonStr
	# print str(jsonStr).decode('unicode_escape')