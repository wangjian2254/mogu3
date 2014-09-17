# coding=utf-8
# author:u'王健'
#Date: 13-6-1
#Time: 下午9:21
import json
import os
from google.appengine.api import memcache
from google.appengine.ext.blobstore import BlobInfo

__author__ = u'王健'

from google.appengine.ext import db


class WebSiteUrl(db.Model):
    """
    网站域名，方便使用 快速的域名
    """
    url = db.URLProperty()
    updateTime = db.DateTimeProperty(auto_now=True)

    @classmethod
    def getInitUrl(cls):
        url = memcache.get('usedurl')
        if not url:
            u = cls.all().order('-updateTime').fetch(1)
            if len(u):
                url = u[0].url
                memcache.set('usedurl', u[0].url, 3600 * 24 * 10)
            else:
                u = WebSiteUrl()
                u.url = 'http://localhost:8180'
                u.put()
                url = u.url
        return str(url)

    def delete(self, **kwargs):
        super(WebSiteUrl, self).delete(**kwargs)
        memcache.delete('usedurl')

    def put(self, **kwargs):
        super(WebSiteUrl, self).put(**kwargs)
        memcache.set('usedurl', self.url, 3600 * 24 * 10)


class Users(db.Model):
    name = db.StringProperty()  #本站昵称
    username = db.EmailProperty()
    password = db.StringProperty()
    auth = db.StringProperty()


class KindSort(db.Model):
    kindlist = db.ListProperty(item_type=int, indexed=False)


class Kind(db.Model):
    name = db.StringProperty()
    type = db.StringProperty()  #用户可选 1:用户可选
    # applist = db.ListProperty(item_type=int, indexed=False)

    def put(self, **kwargs):
        super(Kind, self).put(**kwargs)

        memcache.delete('allkind')


class PluginCount(db.Model):
    num = db.IntegerProperty(indexed=False, default=0)


class Plugin(db.Model):
    name = db.StringProperty()
    code = db.StringProperty()
    appcode = db.StringProperty()
    desc = db.TextProperty(indexed=False)
    updatedesc = db.TextProperty(indexed=False)
    date = db.DateTimeProperty(auto_now_add=True)  #//创建时间
    lastUpdateTime = db.DateTimeProperty(auto_now=True)  #//最后一次修改时间
    imagelist = db.StringListProperty(indexed=False)

    imageid = db.StringProperty(indexed=False)

    apkkey = db.StringProperty()
    apkverson = db.IntegerProperty(indexed=False, default=0)

    isactive = db.BooleanProperty(default=False)
    status = db.StringProperty(indexed=False)
    username = db.StringProperty()  #隶属用户
    kindids = db.ListProperty(item_type=int)  #应用分类
    type = db.StringProperty()  #应用 类型 0：单机 1:积分 2：多人
    type_status = db.IntegerProperty(indexed=False, default=1)
    index_time = db.DateTimeProperty()  #//排序时间，默认等于apk最新提交时间
    downnum = db.IntegerProperty(default=0)  #插件下载次数

    def delete(self, **kwargs):
        if self.imageid:
            b = BlobInfo.get(self.imageid.split('.')[0])
            if b:
                b.delete()
        if self.apkkey:
            b = BlobInfo.get(self.apkkey)
            if b:
                b.delete()
        for imguri in self.imagelist:
            b = BlobInfo.get(imguri.split('.')[0])
            if b:
                b.delete()
        super(Plugin, self).delete(**kwargs)
        pluginCount = PluginCount.get_or_insert('plugin_count')
        pluginCount.num -= 1
        pluginCount.put()
        memcache.delete('pluginid%s' % self.key().id())
        memcache.delete('user_applist_%s' % (self.username))
        l = []
        for i in range(0, pluginCount.num % 30):
            l.append('applist_%s' % i)
        l.append('applist_%s' % len(l))
        memcache.delete_multi(l)

    def put(self, **kwargs):
        if kwargs.has_key("download"):
            del kwargs['download']
            super(Plugin, self).put(**kwargs)
            return
        if not self.is_saved:
            flag = True
        else:
            flag = False
        if self.name and self.code and self.appcode and self.desc and self.imageid and self.apkkey:
            if self.type == '0' and self.type_status != 0:
                self.isactive = False
                self.status = u'等待签名'
            else:
                self.isactive = True
        else:
            self.isactive = False
            self.status = u'名称、code、应用包名、简介、图标 不能为空'
        super(Plugin, self).put(**kwargs)
        pluginCount = PluginCount.get_or_insert('plugin_count')
        if flag:
            pluginCount.num += 1
            pluginCount.put()

        memcache.delete('pluginid%s' % self.key().id())
        memcache.delete('user_applist_%s' % (self.username))
        l = []
        for i in range(0, pluginCount.num % 30):
            l.append('applist_%s' % i)
        l.append('applist_%s' % len(l))
        memcache.delete_multi(l)


# class PluginDownloadNum(db.Model):
#     # plugin = db.IntegerProperty() #插件id 使用key_name='pluginid_%s'%id
#     kindid = db.IntegerProperty()  #插件分类
#     downnum = db.IntegerProperty()  #插件下载次数


class PluginVersion(db.Model):
    plugin = db.IntegerProperty()
    versioncode = db.StringProperty(indexed=False)
    versionnum = db.IntegerProperty()
    data = db.BlobProperty()
    size = db.IntegerProperty()
    datakey = db.StringProperty(indexed=False)
    updateDesc = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)  #//提交时间
    imageids = db.ListProperty(item_type=int)

    check_status = db.IntegerProperty()  #如果是第三方上传的，需要标记为 未破解。在破解过后，再取消标记。

    def put(self, **kwargs):

        super(PluginVersion, self).put(**kwargs)
        p = Plugin.get_by_id(self.plugin)
        if self.versioncode and self.versionnum and (self.data or self.datakey) and self.updateDesc and len(
                self.imageids) and self.check_status == 0:
            p.isactive = True
        else:
            p.isactive = False
        p.put()
        memcache.get('newpluginVersion' + p.appcode)


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
    lastUpdateTime = db.DateTimeProperty()  #//最后一次修改时间
    startdate = db.DateTimeProperty(auto_now_add=True)  #//开始时间
    enddate = db.DateTimeProperty()  #//提交时间
    isdel = db.BooleanProperty(default=False)




