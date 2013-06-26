#coding=utf-8
#author:u'王健'
#Date: 13-6-1
#Time: 下午11:53
import datetime,time
from google.appengine.api import memcache
from google.appengine.ext import db
from mogu.login import login_required
from mogu.models.model import Notice, Plugin, Images, PluginVersion
from setting import WEBURL
from tools.page import Page
import json
from tools.util import getResult

__author__ = u'王健'

timezone = datetime.timedelta(hours=8)


class NoticeUpdate(Page):
    @login_required
    def get(self):
        noteupdate = datetime.datetime.utcnow() + timezone
        id = self.request.get('id', None)
        notice = {}
        if id:
            notice = Notice.get_by_id(int(id))
        noticeconten=[]
        if notice:
            for item in notice.content:
                noticeconten.append(json.loads(item))
        pluginList = Plugin.all().filter('isdel =', False).order('-lastUpdateTime')
        self.render('template/notice/noticeUpdate.html', {'notice': notice,'noteupdate':noteupdate, 'noticecontent':noticeconten, 'id': id, 'pluginList': pluginList})

    def post(self):
        noteupdate = datetime.datetime.utcnow() + timezone
        id = self.request.get('id', None)
        title = self.request.get('title', None)
        indexs = self.request.get('index', '').split(',')
        type = self.request.get('type', None)
        pluginid = self.request.get('plugin', None)
        pluginimg = self.request.get('pluginimg', None)
        startdate = self.request.get('startdate', None)
        enddate = self.request.get('enddate', None)
        plugin = None
        if type == '2' and pluginid:
            plugin = Plugin.get_by_id(int(pluginid))

        if id:
            notice = Notice.get_by_id(int(id))
            notice.content=[]
        else:
            notice = Notice()
        if plugin:
            notice.plugin=plugin.key().id()
            notice.pluginimg=int(pluginimg)
        notice.title = title
        notice.startdate=datetime.datetime.strptime(startdate+' 00:00:00','%Y-%m-%d %H:%M:%S')
        notice.enddate=datetime.datetime.strptime(enddate+' 23:59:59','%Y-%m-%d %H:%M:%S')
        for inputname in indexs:
            content = self.request.POST.get(inputname, '')
            if content != '' and content != u'' and content != None:
                if inputname.find('image') == 0:
                    # imgfield = self.request.POST.get(inputname)
                    if content != '' and content != u'' and content != None:
                        if isinstance(content,unicode):
                            try:
                                content=int(content)
                                notice.content.append(json.dumps({'type': 'img', 'imgid': content, 'url': '%s/download?image_id=%s' % (WEBURL, content)}))
                                continue
                            except:
                                pass


                        elif content.type.lower() not in ['image/pjpeg', 'image/x-png', 'image/jpeg', 'image/png',
                                                        'image/gif',
                                                        'image/jpg']:
                            continue
                        imgfile = Images()
                        imgfile.filename = content.filename
                        imgfile.filetype = content.type
                        imgfile.data = db.Blob(content.file.read())
                        imgfile.size = content.bufsize
                        imgfile.put()
                    notice.content.append(json.dumps({'type': 'img', 'imgid': imgfile.key().id(), 'url': '%s/download?image_id=%s' % (WEBURL, imgfile.key().id())}))
                if inputname.find('content') == 0:
                    notice.content.append(json.dumps({'type': 'text', 'content': content}))
        notice.type = int(type)

        notice.lastUpdateTime = noteupdate

        notice.put()
        deleteNoticeMemcache()
        noticeconten=[]
        for item in notice.content:
            noticeconten.append(json.loads(item))
        pluginList = Plugin.all().filter('isdel =', False).order('-lastUpdateTime')
        self.render('template/notice/noticeUpdate.html',
                    {'notice': notice,'noteupdate':noteupdate, 'noticecontent':noticeconten, 'id': notice.key().id(), 'pluginList': pluginList, 'result': 'succeed',
                     'msg': u'修改成功。'})


class NoticeList(Page):
    def get(self):
        noticeList = Notice.all().filter('isdel =', False).order('-lastUpdateTime')
        self.render('template/notice/noticeList.html', {'noticeList': noticeList})


class NoticeDetail(Page):
    def get(self):
        id = self.request.get('id', None)
        notice = {}
        if id:
            notice = Notice.get_by_id(int(id))
        noticeconten=[]
        if notice:
            for item in notice.content:
                noticeconten.append(json.loads(item))
        pluginList = Plugin.all().filter('isdel =', False).order('-lastUpdateTime')
        self.render('template/notice/noticeDetail.html', {'notice': notice, 'noticecontent':noticeconten, 'id': id, 'pluginList': pluginList})



class NoticeDelete(Page):
    def get(self):
        id = self.request.get('id', None)
        if id:
            notice=Notice.get_by_id(int(id))
            if notice:
                notice.isdel=True
                notice.put()
                self.flush(getResult(id, True, u'系统消息删除成功。'))
                deleteNoticeMemcache()
                return
            self.flush(getResult(id, False, u'系统消息删除失败，系统消息不存在。'))
            return
        self.flush(getResult('', False, u'系统消息删除失败。'))


class NoticeInfoUpdate(Page):
    def get(self):
        timelineold=self.request.get('timeline','0')
        if timelineold:
            timeline=float(timelineold)
        else:
            return
        newtimeline=datetime.datetime.utcnow()+timezone
        timeline=datetime.datetime(*tuple(time.gmtime(timeline))[:6])
        query=memcache.get('newnotice'+newtimeline.strftime('%Y-%m-%d %H'))
        if not query:
            query=[]
            for n in Notice.all().filter('enddate >=',newtimeline).order('enddate'):
                query.append(n)
            memcache.set('newnotice'+newtimeline.strftime('%Y-%m-%d %H'),query,3600)
        # if timelineold=='0':
        #
        # else:
        #     query=Notice.all().filter('lastUpdateTime >=',timeline)
        noticelist=[]
        for notice in query:
            if notice.lastUpdateTime>=timeline:
                noticelist.append(notice)
        if noticelist:
            msg=[{"msg":u"新收到%s条系统信息"%(len(noticelist),),"type":1}]
        else:
            msg=[]
        result={'noticelist':jsonStrNotice(noticelist),'timeline': time.mktime(newtimeline.timetuple()),"notice":msg}
        self.flush(result)




def jsonStrNotice(noticelist):
    nlist=[]
    for notice in noticelist:
        n={'title':notice.title, 'id':notice.key().id(),'content':[], 'isdel':notice.isdel, 'type':notice.type, 'lastUpdateTime':notice.lastUpdateTime.strftime('%Y-%m-%d %H:%M'), 'startdate':notice.startdate.strftime('%Y-%m-%d %H:%M'),'enddate':notice.enddate.strftime('%Y-%m-%d %H:%M')}
        if notice.type==1:
            for c in notice.content:
                n['content'].append(json.loads(c))
        if notice.type==2 and notice.plugin:
            plugin=Plugin.get_by_id(notice.plugin)
            n['pluginappcode']=plugin.appcode
            n['content'].append({'content':plugin.desc, 'type':'text'})

            pluginVersionList=PluginVersion.all().filter('plugin =',plugin.key().id()).order('-versionnum').fetch(1)
            if len(pluginVersionList):
                pluginVersion=pluginVersionList[0]
                n['content'].append({'content':pluginVersion.updateDesc, 'type':'text'})
                n['pluginimg']=notice.pluginimg
                for imgid in pluginVersion.imageids:
                    n['content'].append({'type': 'img', 'imgid': imgid, 'url': '%s/download?image_id=%s' % (WEBURL, imgid)})
        nlist.append(n)
    return nlist


def deleteNoticeMemcache():
    newtimeline=datetime.datetime.utcnow()+timezone
    memcache.delete('newnotice'+newtimeline.strftime('%Y-%m-%d %H'))