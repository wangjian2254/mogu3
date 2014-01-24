#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from mogu.models.model import WebSiteUrl, Kind, Plugin, KindSort
from tools.page import Page
from tools.util import getResult

__author__ = u'王健'

def getKindSort():
    kindsort = KindSort.get_by_key_name("kindsort")
    if not kindsort:
        kindsort=KindSort(key_name='kindsort')
        for k in Kind.all():
            kindsort.kindlist.append(k.key().id())
        kindsort.put()
    return kindsort

class KindList(Page):
    def get(self):
        kindlist = []
        allpluginlist = Plugin.all().filter('isdel =',False)

        for kind in Kind.get_by_id(getKindSort().kindlist):
            pluginlist = Plugin.get_by_id(kind.applist)
            pluginlistempty= []
            for p in allpluginlist:
                f = False
                for pl in pluginlist:
                    if p.key().id() == pl.key().id():
                        f = True
                        break
                if not f:
                    pluginlistempty.append(p)
            kindlist.append((kind,pluginlist,pluginlistempty))
        self.render('template/kind/kindList.html',{"kindlist":kindlist})

class KindUpdate(Page):
    def get(self):
        index = self.request.get('index','0')
        name = self.request.get('name','')
        id = self.request.get('id','')
        if id:
            id = int(id)
            kind = Kind.get_by_id(id)
        else:
            kind = Kind()
        kind.index = int(index)
        kind.name = name
        kind.put()
        ks = getKindSort()
        if kind.key().id() in  ks.applist:
            ks.applist.remove(kind.key().id())
        ks.applist.insert(int(index),kind.key().id())
        ks.put()
        return self.redirect('/KindList')
    def post(self):
        self.get()
class KindDelete(Page):
    def get(self):
        id = self.request.get('id',None)
        if id:
            w=Kind.get_by_id(int(id))
            w.delete()
        return self.flush(getResult(id, True, u'删除成功。'))
