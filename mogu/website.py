# coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from google.appengine.api import memcache
from mogu.models.model import WebSiteUrl
from tools.page import Page
from tools.util import getResult

__author__ = u'王健'


class WebsiteList(Page):
    def get(self):
        cachename = 'websiteurl'
        cacheresult = memcache.get(cachename)
        if cacheresult:
            self.flush(cacheresult)
            return
        l = []
        for w in WebSiteUrl.all().order('-updateTime'):
            l.append({'id': w.key().id(), 'url': w.url, 'updateTime': w.updateTime.strftime('%Y-%m-%d %H:%M')})
        self.getResult(True, u'获取网站域名', l, cachename=cachename)


class WebsiteUpdate(Page):
    def get(self):
        url = self.request.get('url', None)
        id = self.request.get('id', None)
        if url:
            if 0 == WebSiteUrl.all().filter('url =', url).count():
                w = WebSiteUrl()
                w.url = url
                w.put()
        if id:
            w = WebSiteUrl.get_by_id(int(id))
            w.put()
        memcache.delete('websiteurl')
        self.getResult(True, u'修改网站备用域名成功', None)

    def post(self):
        self.get()


class WebsiteDelete(Page):
    def get(self):
        id = self.request.get('id', None)
        if id:
            w = WebSiteUrl.get_by_id(int(id))
            w.delete()
        memcache.delete('websiteurl')
        self.getResult(True, u'修改网站备用域名成功', id)
