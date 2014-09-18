# coding=utf-8
# Date:2014/9/18
#Email:wangjian2254@gmail.com
from google.appengine.api import memcache
from google.appengine.ext.blobstore import blobstore
from mogu.models.model import Plugin, Kind, WebSiteUrl
from mogu3.views_kind import getKindSort
from tools.page import Page

__author__ = u'王健'


def getPluginByMemcache(id):
    p = memcache.get('pluginid%s' % id)
    if not p:
        p = Plugin.get_by_id(int(id))
        memcache.set('pluginid%s' % id, p, 3600 * 24 * 10)
    return p


class PluginInfoAll(Page):
    def get(self):
        #url 缓存
        cachename = 'plugininfoall'
        cacheresult = memcache.get(cachename)
        if cacheresult:
            self.flush(cacheresult)
            return
        #无 url缓存
        allkindlist = memcache.get('allkindlist')
        if not allkindlist:
            allkindlist = Kind.get_by_id(getKindSort().kindlist)
            memcache.set('allkindlist', allkindlist, 3600 * 24)
        kindlist = []
        pluginlist = []
        for i, kind in enumerate(allkindlist):
            pluginquery = Plugin.all().filter('kindids =', kind.key().id()).filter('isactive =', True).order('index_time')
            k = {'name': kind.name, 'index': i, 'list': []}
            for p in pluginquery.fetch(7):
                pluginlist.append(json_to_str(p))
                k['list'].append(p.appcode)
            kindlist.append(k)
        # 输出 json 字符串 plugin 对象
        # result = {'pluginlist': jsonToStr(pluginVersionDict), "notice": [], 'kind': kindlist, 'status': 200,
        #           'success': True, 'message': u''}
        self.getResult(True, u'', {'pluginlist': pluginlist, 'kind': kindlist, "notice": []}, cachename=cachename)


def json_to_str(plugin):
    p = {'imglist': [], 'appcode': plugin.appcode,
         'url': '%s/serve/%s' % (WebSiteUrl.getInitUrl(), plugin.apkkey),
         'updateDesc': plugin.updatedesc,
         'newversion': plugin.apkverson, 'name': plugin.name,
         'desc': plugin.desc,
         'iconurl': '%s/download/%s' % (WebSiteUrl.getInitUrl(), plugin.imageid),
         'size': blobinfo_size_memcache(plugin.apkkey)}
    for i, imgid in enumerate(plugin.imagelist):
        p['imglist'].append({'index': i, 'url': '%s/download/%s' % (WebSiteUrl.getInitUrl(), imgid)})
    return p


def blobinfo_size_memcache(key):
    size = memcache.get(key)
    if not size:
        blobinfo = blobstore.BlobInfo.get(key)
        memcache.set(key, blobinfo.size, 3600 * 24 * 10)
        size = blobinfo.size
    return size