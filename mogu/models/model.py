#coding=utf-8
#author:u'王健'
#Date: 13-6-1
#Time: 下午9:21
import json
import os

__author__ = u'王健'

from google.appengine.ext import db


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
    # trueName = db.StringProperty()  #//姓名
    # tele = db.StringProperty()      #//电话号码
    # mobile = db.StringProperty()    #//手机
    date = db.DateTimeProperty(auto_now_add=True)  #//注册时间
    lastUpdateTime = db.DateTimeProperty(auto_now=True) #//最后一次修改时间
    # appData = db.TextProperty()#记录应用的必要数据gae端事json格式，传输时用urlprams的方式传输

    # __appinit = False
    # __appParms = {}

    # def getParms(self):
    #     if not self.__appinit:
    #         self.__appParms = json.loads(self.appData or '{}')
    #         self.__appinit = True
    #     return self.__appParms

    # def put(self, **kwargs):
    #     if self.__appinit:
    #         self.appData = json.dumps(self.__appParms)
    #     super(User, self).put(**kwargs)

    @classmethod
    def get_by_keyname(cls, key_names, parent=None, **kwargs):
        n = 'u' + str(len(key_names) - 1) + key_names
        u = cls.get_by_key_name(key_names=n, parent=parent, **kwargs)
        if not u:
            return cls.get_by_key_name(key_names=key_names, parent=parent, **kwargs)
        else:
            return u


class Plugin(db.Model):
    name = db.StringProperty()
    # kinds = db.StringListProperty()
    code = db.StringProperty()
    appcode = db.StringProperty()
    desc = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)  #//创建时间
    lastUpdateTime = db.DateTimeProperty(auto_now=True) #//最后一次修改时间
    isdel = db.BooleanProperty(default=False)


class PluginVersion(db.Model):
    plugin = db.IntegerProperty()
    versioncode = db.StringProperty(indexed=False)
    versionnum = db.IntegerProperty()
    data = db.BlobProperty()
    size = db.IntegerProperty()
    updateDesc = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)  #//提交时间
    imageids = db.ListProperty(item_type=int)


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
        return "http://%s/image/%s" % (os.environ['HTTP_HOST'], self.key().id())


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




