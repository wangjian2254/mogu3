#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from mogu.models.model import Plugin, PluginVersion, Images, WebSiteUrl, Kind
from google.appengine.ext.blobstore import blobstore, BlobInfo
from google.appengine.api import files
from google.appengine.ext import db
from tools.page import Page
import datetime

__author__ = u'王健'
timezone = datetime.timedelta(hours=8)

class PluginUploadScript(Page):
    def post(self):
        noteupdate = datetime.datetime.utcnow() + timezone
        id = self.request.get('id', None)
        name = self.request.get('name', None)
        code = self.request.get('code', None)
        appcode = self.request.get('appcode', None)
        if 0 < Plugin.all().filter('appcode =', appcode).count():
            for plugin in Plugin.all().filter('appcode =', appcode):

                if plugin.apkkey:
                    b = blobstore.BlobInfo.get(plugin.apkkey)
                    if b:
                        b.delete()
                if plugin.imageid:
                    b = blobstore.BlobInfo.get(plugin.imageid)
                    if b:
                        b.delete()
                for imgid in plugin.imagelist:
                    b = blobstore.BlobInfo.get(imgid)
                    if b:
                        b.delete()
                plugin.delete()
        desc = self.request.get('desc', None)
        if id:
            plugin = Plugin.get_by_id(int(id))
        else:
            plugin = Plugin()

        plugin.name = name
        plugin.code = code
        plugin.appcode = appcode
        plugin.desc = desc
        plugin.type = '0'
        plugin.username = 'admin@gmail.com'
        plugin.index_time = noteupdate
        plugin.lastUpdateTime = noteupdate
        if not id and 0 < Plugin.all().filter('appcode =', appcode).count():
            return self.flush({'status':500,'message':u'插件已经存在'})

        plugin.put()
        upload_icon_url = blobstore.create_upload_url('/iconupload?pluginid=%s' % (plugin.key().id()))
        imgurllist = []
        for i in range(10):
            imgurllist.append(blobstore.create_upload_url('/imageupload?pluginid=%s' % (plugin.key().id())))
        self.flush({'status': 200, 'upload_icon_url': upload_icon_url, 'upload_image_url': imgurllist})



class PluginUploadApkScript(Page):
    def post(self):
        appcode = self.request.get('appcode', None)
        for plugin in Plugin.all().filter('appcode =', appcode):
            for pv in PluginVersion.all().filter('plugin =',plugin.key().id()):
                if pv.datakey:
                    b=blobstore.BlobInfo.get(pv.datakey)
                    if b:
                        b.delete()
                upload_url = blobstore.create_upload_url('/upload?pluginversionid=%s'%(pv.key().id()))
                return self.flush({'status' : 200, 'upload_url' : upload_url})
        return self.flush({'status':500,'message':u'插件已经存在'})


class PluginUploadApkDataScript(Page):
    def post(self):
        pluginversionid = self.request.get('pluginversionid', None)
        pv = PluginVersion.get_by_id(int(pluginversionid))
        if pv.datakey:
            b = BlobInfo.get(pv.datakey)
            if b:
                b.delete()
        file_name = files.blobstore.create(mime_type='application/octet-stream')
        with files.open(file_name, 'a') as f:
            f.write(self.request.POST.get('file'))
        files.finalize(file_name)
        blob_key = files.blobstore.get_blob_key(file_name)
        pv.datakey=str(blob_key)
        pv.size = files.blobstore.size
        pv.save()
        return self.flush({'status':200,'message':u'插件已经存在'})