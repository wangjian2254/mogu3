#coding=utf-8
#author:u'王健'
#Date: 13-6-1
#Time: 下午9:21
import json
import os
from google.appengine.api import memcache

__author__ = u'王健'

from google.appengine.ext import db

class WebSiteUrl(db.Model):
    '''
    网站域名，方便使用 快速的域名
    '''
    url = db.URLProperty()
    updateTime = db.DateTimeProperty(auto_now=True)

    @classmethod
    def getInitUrl(cls):
        url = memcache.get('usedurl')
        if not url:
            u = cls.all().order('-updateTime').fetch(1)
            if len(u):
                url = u[0].url
                memcache.set('usedurl',u[0].url,3600*24*10)
            else:
                u = WebSiteUrl()
                u.url = 'http://plugins.mmggoo.com'
                u.put()
                url = u.url
        return url

    def delete(self,**kwargs):
        super(WebSiteUrl, self).delete(**kwargs)
        memcache.delete('usedurl')
    def put(self,**kwargs):
        super(WebSiteUrl, self).put(**kwargs)
        memcache.set('usedurl',self.url,3600*24*10)

#记录最新的用户名
class UserNameNumber(db.Model):
    userName = db.IntegerProperty(indexed=False)


class Users(db.Model):
    name = db.StringProperty()#本站昵称
    username = db.EmailProperty()
    password = db.StringProperty()
    auth = db.StringProperty()


class User(db.Model): #//用户表
    userName = db.StringProperty() #//用户名
    passWord = db.StringProperty()  #//密码
    date = db.DateTimeProperty(auto_now_add=True)  #//注册时间
    lastUpdateTime = db.DateTimeProperty(auto_now=True) #//最后一次修改时间

    @classmethod
    def get_by_keyname(cls, key_names, parent=None, **kwargs):
        n = 'u' + str(len(key_names) - 1) + key_names
        u = cls.get_by_key_name(key_names=n, parent=parent, **kwargs)
        if not u:
            return cls.get_by_key_name(key_names=key_names, parent=parent, **kwargs)
        else:
            return u


class Kind(db.Model):
    name = db.StringProperty()
    index = db.IntegerProperty()
    applist = db.StringListProperty(indexed=False)

class Plugin(db.Model):
    name = db.StringProperty()
    code = db.StringProperty()
    appcode = db.StringProperty()
    desc = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)  #//创建时间
    lastUpdateTime = db.DateTimeProperty(auto_now=True) #//最后一次修改时间
    isdel = db.BooleanProperty(default=False)
    imageid = db.IntegerProperty(indexed=False)
    isactive=db.BooleanProperty(default=False)

    def put(self,**kwargs):
        if self.name and self.code and self.appcode and self.desc and self.imageid:
            pass
        else:
            self.isactive = False
        super(Plugin, self).put(**kwargs)


class PluginVersion(db.Model):
    plugin = db.IntegerProperty()
    versioncode = db.StringProperty(indexed=False)
    versionnum = db.IntegerProperty()
    data = db.BlobProperty()
    size = db.IntegerProperty()
    datakey=db.StringProperty(indexed=False)
    updateDesc = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)  #//提交时间
    imageids = db.ListProperty(item_type=int)

    def put(self,**kwargs):
        super(PluginVersion, self).put(**kwargs)
        p = Plugin.get_by_id(self.plugin)
        if self.versioncode and self.versionnum and (self.data or self.datakey) and self.updateDesc and len(self.imageids) :
            p.isactive = True
        else:
            p.isactive = False
        p.put()


class Images(db.Model):
    filename = db.StringProperty(indexed=False)
    filetype = db.StringProperty(indexed=False)
    size = db.IntegerProperty(indexed=False)
    data = db.BlobProperty()

    @property
    def id(self):
        return str(self.key().id())

    @property
    def imgurl(self):
        return "%s/image/%s" % (WebSiteUrl.getInitUrl(), self.key().id())


class Notice(db.Model):
    title = db.StringProperty(indexed=False)
    content = db.StringListProperty(indexed=False)
    type = db.IntegerProperty()
    plugin = db.IntegerProperty()
    pluginimg = db.IntegerProperty()
    lastUpdateTime = db.DateTimeProperty() #//最后一次修改时间
    startdate = db.DateTimeProperty(auto_now_add=True)  #//开始时间
    enddate = db.DateTimeProperty()  #//提交时间
    isdel = db.BooleanProperty(default=False)




