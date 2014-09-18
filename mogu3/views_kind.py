# coding=utf-8
# Date:2014/9/12
# Email:wangjian2254@gmail.com
from datetime import datetime
from google.appengine.api import memcache
from mogu.models.model import Plugin, PluginCount, KindSort, Kind
from mogu3.login import login_required, get_current_user, login_required_admin
from tools.page import Page

__author__ = u'王健'


def getKindSort():
    kindsort = memcache.get("kindsort")
    if not kindsort:
        kindsort = KindSort.get_by_key_name("kindsort")
        if not kindsort:
            kindsort = KindSort(key_name='kindsort')
            for k in Kind.all():
                kindsort.kindlist.append(k.key().id())
            kindsort.put()
        memcache.set("kindsort", kindsort, 3600 * 24)
    return kindsort


class KindList(Page):
    @login_required
    def get(self, *args):
        cachename = 'allkind'
        cacheresult = memcache.get(cachename)
        if cacheresult:
            self.flush(cacheresult)
            return
        kindsort = getKindSort()
        l = []
        i = 0
        for kind in Kind.get_by_id(kindsort.kindlist):
            if not kind:
                continue
            p = {'id': kind.key().id(), 'name': kind.name, 'type': kind.type, 'index': i}
            l.append(p)
            i += 1
        self.getResult(True, u'获取分类列表', l, cachename=cachename)


class KindUpdate(Page):
    @login_required_admin
    def post(self, *args):
        id = self.request.get('id', None)
        name = self.request.get('name', None)
        type = self.request.get('type', '0')
        kindsort = getKindSort()
        if id:
            kind = Kind.get_by_id(int(id))
        else:
            kind = Kind()

        kind.name = name
        kind.type = type
        kind.put()
        if not id:
            kindsort.kindlist.append(kind.key().id())
            kindsort.put()

        self.getResult(True, u'分类修改成功', kind.key().id())


class KindDel(Page):
    @login_required_admin
    def post(self, *args):
        id = self.request.get('id', None)
        kindsort = getKindSort()
        if id:
            kind = Kind.get_by_id(int(id))
            kind.delete()
            kindsort.kindlist.remove(kind.key().id())
            kindsort.put()
        self.getResult(True, u'分类删除成功', id)


class KindAddPlugin(Page):
    @login_required_admin
    def post(self, *args):
        id = self.request.get('id', None)
        pluginid = self.request.get('pluginid', None)
        if id and pluginid:
            id = int(id)
            plugin = Plugin.get_by_id(int(pluginid))
            if id not in plugin.kindids:
                plugin.kindids.append(id)
                plugin.put()
        self.getResult(True, u'分类添加应用成功', None)


class KindDelPlugin(Page):
    @login_required_admin
    def post(self, *args):
        id = self.request.get('id', None)
        pluginid = self.request.get('pluginid', None)
        if id and pluginid:
            id = int(id)
            plugin = Plugin.get_by_id(int(pluginid))
            if id in plugin.kindids:
                plugin.kindids.remove(id)
                plugin.put()
        self.getResult(True, u'分类删除应用成功', None)


class KindMove(Page):
    @login_required_admin
    def post(self, *args):
        id = self.request.get('id', None)
        path = self.request.get('fx', 'up')
        kindsort = getKindSort()
        if id:
            id = int(id)
            index = kindsort.kindlist.index(id)
            if path == 'up':
                if index >= 1:
                    k = kindsort.kindlist.pop(index)
                    kindsort.kindlist.insert(index - 1, k)
            elif path == 'down':
                if index < len(kindsort.kindlist) - 1:
                    k = kindsort.kindlist.pop(index)
                    kindsort.kindlist.insert(index + 1, k)
            kindsort.put()
            memcache.delete('allkind')
        self.getResult(True, u'分类移动成功', id)