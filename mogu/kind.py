#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import urllib
from mogu.models.model import WebSiteUrl, Kind, Plugin, KindSort
from tools.page import Page
from tools.util import getResult

__author__ = u'王健'

def getKindSort():
    kindsort = KindSort.get_by_key_name("kindsort")
    # kindsort.delete()
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
            if not kind:
                continue
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
        type = self.request.get('type',None)
        id = self.request.get('id','')
        url = self.request.get('url','KindList')
        if id:
            id = int(id)
            kind = Kind.get_by_id(id)
        else:
            kind = Kind()
        kind.index = int(index)
        kind.name = name
        kind.type = type
        kind.put()
        ks = getKindSort()
        if kind.key().id() in  ks.kindlist:
            ks.kindlist.remove(kind.key().id())
        ks.kindlist.insert(int(index),kind.key().id())
        ks.put()
        return self.redirect('/%s'%url)
    def post(self):
        self.get()



class KindMove(Page):
    def get(self):
        path = self.request.get('path','')
        kindid = self.request.get('kindid','')
        url = self.request.get('url','KindList')
        if kindid:
            kindid = int(kindid)
        else:
            return self.redirect('/%s'%url)

        ks = getKindSort()
        if  kindid not in  ks.kindlist:
            return self.redirect('/%s'%url)
        else:
            index = ks.kindlist.index(kindid)

            if path == 'up':
                if index>=1:
                    k = ks.kindlist.pop(index)
                    ks.kindlist.insert(index-1,k)
            elif path == 'down':
                if index<len(ks.kindlist)-1:
                    k = ks.kindlist.pop(index)
                    ks.kindlist.insert(index+1,k)
            ks.put()
        return self.redirect('/%s'%url)

class KindAddPlugin(Page):
    def post(self):
        index = self.request.get('index','0')
        gameid = self.request.get('appcode','')
        kindid = self.request.get('kindid','')
        url = self.request.get('url','KindList')
        if kindid:
            kindid = int(kindid)
            kind = Kind.get_by_id(kindid)
        else:
            return self.redirect('/%s'%url)
        if not gameid:
            return self.redirect('/%s'%url)
        gameid = int(gameid)
        if gameid  in kind.applist:
            kind.applist.remove(gameid)
        kind.applist.insert(int(index), gameid)
        kind.put()
        return self.redirect('/%s'%url)


class KindPluginMove(Page):
    def get(self):
        path = self.request.get('path','')
        kindid = self.request.get('kindid','')
        id = self.request.get('id','')
        url = self.request.get('url','KindList')
        if kindid:
            kindid = int(kindid)
            kind = Kind.get_by_id(kindid)
        else:
            return self.redirect('/%s'%url)
        if not id:
            return self.redirect('/%s'%url)
        id = int(id)
        if id not in  kind.applist:
            return self.redirect('/%s'%url)
        else:
            index = kind.applist.index(id)

            if path == 'up':
                if index>=1:
                    k = kind.applist.pop(index)
                    kind.applist.insert(index-1,k)
            elif path == 'down':
                if index<len(kind.applist)-1:
                    k = kind.applist.pop(index)
                    kind.applist.insert(index+1,k)
            kind.put()
        return self.redirect('/%s'%url)


class KindDelete(Page):
    def get(self):
        id = self.request.get('id',None)
        if id:
            w=Kind.get_by_id(int(id))
            w.delete()
        ks = getKindSort()
        if int(id) in ks.kindlist:
            ks.kindlist.remove(int(id))
            ks.put()
        return self.flush(getResult(id, True, u'删除成功。'))


class KindPluginDelete(Page):
    def get(self):
        id = self.request.get('id',None)
        kindid = self.request.get('kindid',None)
        if kindid:
            kindid = int(kindid)
            kind = Kind.get_by_id(kindid)
        else:
            return self.redirect('/KindList')
        if int(id) in kind.applist:
            kind.applist.remove(int(id))
            kind.put()
        return self.flush(getResult('kind%str%s'%(kindid,id), True, u'删除成功。'))

class FenKindList(Page):
    def get(self):
        url = 'FenKindList'
        kindlist = []
        for kind in Kind.get_by_id(getKindSort().kindlist):
            if not kind:
                continue

            kindlist.append(kind)
        self.render('template/kind/fenkindList.html',{"kindlist":kindlist, 'url':url})


class FenKindPlugin(Page):
    def get(self):
        kindid = self.request.get('kindid',None)

        if kindid:
            kindid = int(kindid)
            # kind = Kind.get_by_id(kindid)
        else:
            return self.redirect('/KindList')
        url = urllib.quote( 'FenKindPlugin?kindid=%s'%kindid)
        kindlist = []
        allpluginlist = Plugin.all().filter('isdel =',False)

        for kind in Kind.get_by_id([kindid]):
            if not kind:
                continue
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
        self.render('template/kind/fenkindplugin.html',{"kindlist":kindlist, 'url':url})
