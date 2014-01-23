#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from mogu.models.model import WebSiteUrl
from tools.page import Page

__author__ = u'王健'


class WebsiteList(Page):
    def get(self):
        l = WebSiteUrl.all().order('-updateTime')
        self.render('template/website/websiteList.html',{"websiteList":l})

class WebsiteUpdate(Page):
    def post(self):
        url = self.request.get('url', None)
        id = self.request.get('id', None)
        if url:
            if 0==WebSiteUrl.all().filter('url =',url).count():
                w = WebSiteUrl()
                w.url=url
                w.put()
        if id:
            w=WebSiteUrl.get(int(id))
            w.put()
        return self.redirect('/WebsiteList')

class WebsiteDelete(Page):
    def get(self):
        id = self.request.get('id',None)
        if id:
            w=WebSiteUrl.get(int(id))
            w.delete()
        return self.redirect('/WebsiteList')
