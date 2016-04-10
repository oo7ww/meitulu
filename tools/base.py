#!/usr/bin/env python
#coding:utf-8
from pyquery import PyQuery
import requesocks
import requests
import logging
import urllib
import time
import json
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Common(object):
    def __init__(self, arg):
        super(Common, self).__init__()

    @staticmethod
    def GetUnit(currency):
        return {
        'USD':'$',
        'EUR':'€',
        'CNY':'￥',
        'JPY':'¥',
        'GBP':'£',
        'HKD':'HK$'
        }[currency]

    @staticmethod
    def GetHeaders(urls):
        domain = Common.GetDomain(urls)
        return {
            'Referer':domain,
            'Connection': 'Keep-Alive',
            'Cache-Control': 'max-age=0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        }

    @staticmethod
    def GetDomain(urls):
        if isinstance(urls, basestring):
            url = urls
        elif isinstance(urls, list):
            url = urls[0]
        url_ = url.split('/')
        domain = url_[0]+'//'+url_[2]

        return domain

    @staticmethod
    def GetModulNameByUrl(urls):
        if isinstance(urls, basestring):
            url = urls
        elif isinstance(urls, list):
            url = urls[0]
        url_ = url.split('/')
        url_ = url_[2].split('.')
        if len(url_) > 2 : 
            return url_[1]
        elif len(url_) == 2 :
            return url_[0]
        else :
            raise ValueError,'get ModulName By Url Fail'

    @staticmethod
    def GetProtocol(urls):
        if isinstance(urls, basestring):
            url_ = urls
        if isinstance(urls, list):
            url_ = urls[0]

        return url_.split('/')[0]

    @staticmethod
    def HasElementTag(pyhtml,tagName):
        return len(pyhtml(tagName))

    @staticmethod
    def combine(dict1,dict2):
        map(lambda x:dict1[x].update(dict2[x]),filter(lambda x: x in dict1,dict2))
        map(lambda x:dict1.update(dict2),filter(lambda x: x not in dict1,dict2))
        

class GrabBase(object):

    def __init__(self,urls):
        super(GrabBase, self).__init__()
        self.url = urllib.unquote(urls) if isinstance(urls,basestring) else urllib.unquote(urls[0])
        self.urls = map(lambda x : urllib.unquote(x),urls) if isinstance(urls,list) else [urllib.unquote(urls)]
        self.vars = {}
        self.name = Common.GetModulNameByUrl(self.urls)
        self.domain = Common.GetDomain(self.urls)
        self.session = requests.session()
        self.headers = Common.GetHeaders(self.domain)
        self.useProxy = False
        self.protocol = Common.GetProtocol(self.urls)

    def __del__(self):
        self.url = None
        self.urls = None
        self.name = None
        self.vars = None
        self.domain = None
        self.headers = None
        self.protocol = None
        self.session.close()
        self.session= None
   
    def lists(self):
        if not self.urls :
            raise ValueError,'urls is None , not call pages()'

        product_arr = []
        for url in self.urls :
            product_arr += self.list(url=url)

        return product_arr


    def pages(self):
        if not self.urls :
            raise ValueError,'urls is None , not call pages()'

        product_arr = []
        for url in self.urls :
            product_arr += self.page(url=url)

        return product_arr


    def getPyHtml(self,url):

        resposne = self.Get(url, headers=self.headers)
        status_code = resposne.status_code

        self.vars['fstUrl'] = url
        self.vars['resUrl'] = resposne.url

        if resposne.text:
            pyhtml = PyQuery(resposne.text)
        else:
            pyhtml = PyQuery('Nothing')

        if status_code == 404:
            return 404, pyhtml

        if 'productNotFound.jsp' in resposne.url:
            return 404, pyhtml

        return status_code, pyhtml


    def LoadSession(self, path=None):
        if not path:
            path = self.sessionPath

        session_dic = {}
        try:
            with open(path, 'rb') as fr:
                session_dic = pickle.load(fr)
                self.session.cookies = session_dic['session'].cookies
                if self.DEBUGCF['pverify']:
                    print 'load Cookies:', session_dic['session'].cookies.get_dict()
                    print 'load time:', int(round(time.time(), 2))
        except Exception, e:
            raise e


    def DumpSession(self,path):
        if not path:
            path = self.sessionPath
            
        session_dic = {'time':int(round(time.time(),2)),'stime':time.strftime('%Y-%m-%d %H:%M:%S'),'session':self.session}
        try:
            with open(path,'wb') as fw:
                pickle.dump(session_dic,fw)
                if self.DEBUGCF['pverify'] :
                    print 'dump Cookies:',session_dic['session'].cookies.get_dict()
                    print 'dump time:',session_dic['time']
        except Exception, e:
            raise e
   

    def ResVerify(self,response):
        pass


    def Verify(self,response):
        pass

    def Get(self,url,params=None,headers=None,cookies=None,verify=None,proxy=None):
        args = {'headers':self.session.headers if self.session.headers else self.headers}
        if params : 
            args.update(dict(params=params))
        if headers : 
            args.update(dict(headers=headers))
        if verify : 
            args.update(dict(verify=verify))
        if proxy :
            self.session.proxies = proxy    #调用时使用proxy
        if cookies : 
            Cookies = self.session.cookies
            Cookies.update(cookies)
            args.update(dict(cookies=Cookies))
        if self.useProxy :                  #初始化时使用proxy.
            self.SetProxy()

        response = self.session.get(url,**args)

        return response


    def Post(self,url,data=None,headers=None,cookies=None,verify=None,proxy=None):
        args = {'headers':self.headers}
        if data : 
            args.update(dict(data=data))
        if headers : 
            args.update(dict(headers=headers))
        if verify : 
            args.update(dict(verify=verify))
        if proxy :
            self.session.proxies = proxy    #调用时使用proxy
        if cookies : 
            Cookies = self.session.cookies
            Cookies.update(cookies)
            args.update(dict(cookies=Cookies))
        if self.useProxy :                  #初始化时使用proxy.
            self.SetProxy()

        response = self.session.post(url,**args)

        return response
