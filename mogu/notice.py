# coding=utf-8
# author:u'王健'
#Date: 13-6-1
#Time: 下午11:53
import datetime, time
from google.appengine.api import memcache
from google.appengine.api.blobstore import blobstore
from google.appengine.ext import db
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.ext.webapp import blobstore_handlers

from mogu.models.model import Notice, Plugin, Images, PluginVersion
from mogu3.login import login_required, login_required_admin
from setting import WEBURL
from tools.page import Page
import json
from tools.util import getResult

__author__ = u'王健'

timezone = datetime.timedelta(hours=8)


class NoticeUpdate(Page):
    @login_required_admin
    def post(self):
        noteupdate = datetime.datetime.utcnow() + timezone
        id = self.request.get('id', None)
        title = self.request.get('title', None)
        type = self.request.get('type', None)
        pluginid = self.request.get('plugin', None)
        startdate = self.request.get('startdate', None)
        enddate = self.request.get('enddate', None)
        plugin = None
        if type == '2' and pluginid:
            plugin = Plugin.get_by_id(int(pluginid))
        if id:
            notice = Notice.get_by_id(int(id))
            notice.content = []
        else:
            notice = Notice()
        if plugin:
            notice.plugin = plugin.key().id()
            notice.pluginimg = plugin.imageid
        notice.title = title
        notice.startdate = datetime.datetime.strptime(startdate + ' 00:00:00', '%Y/%m/%d %H:%M:%S')
        notice.enddate = datetime.datetime.strptime(enddate + ' 23:59:59', '%Y/%m/%d %H:%M:%S')
        notice.type = int(type)
        notice.lastUpdateTime = noteupdate
        notice.put()
        deleteNoticeMemcache()
        noticeconten = []
        for item in notice.content:
            noticeconten.append(json.loads(item))
        noticedict = {'id': notice.key().id(), 'title': notice.title, 'type': notice.type,
                      'lastUpdateTime': notice.lastUpdateTime.strftime('%Y-%m-%d %H:%M'),
                      'startdate': notice.startdate.strftime('%Y-%m-%d %H:%M'), 'pluginid': notice.plugin,
                      'enddate': notice.enddate.strftime('%Y-%m-%d %H:%M'), 'pluginimg': notice.pluginimg,
                      'noticeconten': noticeconten}
        self.getResult(True, u'保存系统信息成功', noticedict)


class NoticeList(Page):
    @login_required_admin
    def get(self):
        cachename = 'noticelist'
        cacheresult = memcache.get(cachename)
        if cacheresult:
            self.flush(cacheresult)
            return
        noticeList = []
        for notice in Notice.all().filter('isdel =', False).order('-lastUpdateTime'):
            noticeList.append({'id': notice.key().id(), 'title': notice.title, 'type': notice.type,
                               'lastUpdateTime': notice.lastUpdateTime.strftime('%Y-%m-%d %H:%M'),
                               'startdate': notice.startdate.strftime('%Y-%m-%d %H:%M'),
                               'enddate': notice.enddate.strftime('%Y-%m-%d %H:%M'),
                               'pluginimg': notice.pluginimg})
        self.getResult(True, u'获取应用列表', {'list': noticeList}, cachename=cachename)


def noticeToDice(notice):
    if not notice:
        return None
    noticeconten = []
    for item in notice.content:
        noticeconten.append(json.loads(item))
    noticedict = {'id': notice.key().id(), 'title': notice.title, 'type': notice.type,
                          'lastUpdateTime': notice.lastUpdateTime.strftime('%Y-%m-%d %H:%M'),
                          'startdate': notice.startdate.strftime('%Y-%m-%d %H:%M'), 'pluginid': notice.plugin,
                          'enddate': notice.enddate.strftime('%Y-%m-%d %H:%M'), 'pluginimg': notice.pluginimg,
                          'noticeconten': noticeconten}
    return noticedict

class NoticeDetail(Page):
    def get(self):
        id = self.request.get('id', None)
        notice = {}
        if id:
            notice = Notice.get_by_id(int(id))
        noticedict = noticeToDice(notice)
        if noticedict:
            self.getResult(True, u'', noticedict)
        else:
            self.getResult(False, u'', None)


class NoticeDelete(Page):
    def get(self):
        id = self.request.get('id', None)
        if id:
            notice = Notice.get_by_id(int(id))
            if notice:
                notice.isdel = True
                notice.put()
                self.getResult(True, u'系统消息删除成功。', id)
                deleteNoticeMemcache()
                return
            self.getResult(False, u'系统消息删除失败，系统消息不存在。', id)
            return
        self.getResult(False, u'系统消息删除失败。', '')

class DeleteContentNotice(Page):
    def get(self):
        id = self.request.get('id', None)
        contentIndex = self.request.get('contentIndex', None)
        if id:
            notice = Notice.get_by_id(int(id))
            if notice and contentIndex:
                contentIndex = int(contentIndex)
                item = notice.content.pop(contentIndex)
                item = json.loads(item)
                if item.get('type') == 'img':
                    b = BlobInfo.get(item.get('imgid').split('.')[0])
                    if b:
                        b.delete()
                notice.put()
                self.getResult(True, u'', None)
                deleteNoticeMemcache()
                return
            self.getResult(False, u'系统消息修改失败，系统消息不存在。', id)
            return
        self.getResult(False, u'系统消息修改失败。', '')

class NoticeAppendContent(Page):
    def post(self):
        id = self.request.get('id', None)
        content = self.request.get('content', None)
        if id:
            notice = Notice.get_by_id(int(id))
            if notice and content:
                notice.content.append(json.dumps({'type': 'text', 'content': content}))
                notice.put()
                noticedict = noticeToDice(notice)
                self.getResult(True, u'系统消息修改成功', noticedict)
                deleteNoticeMemcache()
                return
            self.getResult(False, u'系统消息修改失败，系统消息不存在。', id)
            return
        self.getResult(False, u'系统消息修改失败。', '')


class NoticeAppendImage(Page):
    def get(self):
        id = self.request.get('id', None)
        upload_url = blobstore.create_upload_url('/noticeupload?id=%s' % (id))
        self.getResult(True, u'', upload_url)



class NoticeUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        if not upload_files:
            self.response.out.write(
                json.dumps({'success': False, 'message': u'上传图片失败', 'status_code': 200, 'dialog': 1}))
            return
        blob_info = upload_files[0]
        id = self.request.get('id')
        notice = Notice.get_by_id(int(id))
        notice.content.append(json.dumps({'type': 'img', 'imgid': '%s.%s' % (str(blob_info.key()), blob_info.filename.split('.')[-1])}))
        notice.put()
        noticedict = noticeToDice(notice)
        self.response.out.write(json.dumps({'success': True, 'message': u'上传图片成功', 'result':noticedict, 'status_code': 200, 'dialog': 1}))

class NoticeInfoUpdate(Page):
    def get(self):
        timelineold = self.request.get('timeline', '0')
        if timelineold:
            timeline = float(timelineold)
        else:
            return
        newtimeline = datetime.datetime.utcnow() + timezone
        timeline = datetime.datetime(*tuple(time.gmtime(timeline))[:6])
        query = memcache.get('newnotice' + newtimeline.strftime('%Y-%m-%d %H'))
        if not query:
            query = []
            for n in Notice.all().filter('enddate >=', newtimeline).order('enddate'):
                query.append(n)
            memcache.set('newnotice' + newtimeline.strftime('%Y-%m-%d %H'), query, 3600)
        # if timelineold=='0':
        #
        # else:
        #     query=Notice.all().filter('lastUpdateTime >=',timeline)
        noticelist = []
        for notice in query:
            if notice.lastUpdateTime >= timeline:
                noticelist.append(notice)
        if noticelist:
            msg = [{"msg": u"新收到%s条系统信息" % (len(noticelist),), "type": 1}]
        else:
            msg = []
        result = {'noticelist': jsonStrNotice(noticelist), 'timeline': time.mktime(newtimeline.timetuple()),
                  "notice": msg}
        self.flush(result)


def jsonStrNotice(noticelist):
    nlist = []
    for notice in noticelist:
        n = {'title': notice.title, 'id': notice.key().id(), 'content': [], 'isdel': notice.isdel, 'type': notice.type,
             'lastUpdateTime': notice.lastUpdateTime.strftime('%Y-%m-%d %H:%M'),
             'startdate': notice.startdate.strftime('%Y-%m-%d %H:%M'),
             'enddate': notice.enddate.strftime('%Y-%m-%d %H:%M')}
        if notice.type == 1:
            for c in notice.content:
                n['content'].append(json.loads(c))
        if notice.type == 2 and notice.plugin:
            plugin = Plugin.get_by_id(notice.plugin)
            n['pluginappcode'] = plugin.appcode
            n['content'].append({'content': plugin.desc, 'type': 'text'})
            n['content'].append({'content': plugin.updatedesc, 'type': 'text'})
            for imgid in plugin.imagelist:
                n['content'].append(
                    {'type': 'img', 'imgid': imgid, 'url': '%s/download/%s' % (WEBURL, imgid)})

        nlist.append(n)
    return nlist


def deleteNoticeMemcache():
    newtimeline = datetime.datetime.utcnow() + timezone
    memcache.delete('newnotice' + newtimeline.strftime('%Y-%m-%d %H'))