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
                for pv in PluginVersion.all().filter('plugin =',plugin.key().id()):
                    for img in Images.get_by_id(pv.imageids):
                        if img:
                            img.delete()
                    if pv.datakey:
                        b=blobstore.BlobInfo.get(pv.datakey)
                        if b:
                            b.delete()
                    pv.delete()
                if plugin.imageid:
                    img = Images.get_by_id(plugin.imageid)
                    if img:
                        img.delete()
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
        plugin.lastUpdateTime = noteupdate
        if not id and 0 < Plugin.all().filter('appcode =', appcode).count():
            return self.flush({'status':500,'message':u'插件已经存在'})
        imgfield = self.request.POST.get('icon')
        if hasattr(imgfield,'type'):
            if imgfield.type.lower()  in ['image/pjpeg', 'image/x-png','image/x-icon', 'image/jpeg', 'image/png', 'image/gif','image/jpg']:

                imgfile = Images()
                imgfile.filename = imgfield.filename
                imgfile.filetype = imgfield.type
                imgfile.data = db.Blob(imgfield.file.read())
                imgfile.size = imgfield.bufsize
                imgfile.put()
                plugin.imageid=imgfile.key().id()
        plugin.put()

        pluginid = plugin.key().id()

        versioncode = self.request.get('versioncode', '')
        versionnum = self.request.get('versionnum', '')
        updateDesc = self.request.get('updateDesc', '……')

        pluginVersion = PluginVersion()
        pluginVersion.plugin = int(pluginid)
        pluginVersion.versioncode = versioncode
        pluginVersion.versionnum = int(versionnum)
        pluginVersion.updateDesc = updateDesc


        for i in range(1, 11):
            imgfilename = 'image' + str(i)
            imgfield = self.request.POST.get(imgfilename)
            if imgfield != '' and imgfield != u'' and imgfield != None:
                if imgfield.type.lower() not in ['image/pjpeg', 'image/x-png', 'image/jpeg', 'image/png', 'image/gif',
                                                 'image/jpg']:
                    continue
                imgfile = Images()
                imgfile.filename = imgfield.filename
                imgfile.filetype = imgfield.type
                imgfile.data = db.Blob(imgfield.file.read())
                imgfile.size = imgfield.bufsize
                imgfile.put()
                pluginVersion.imageids.append(imgfile.key().id())
        pluginVersion.put()

        upload_url = blobstore.create_upload_url('/upload?pluginversionid=%s'%(pluginVersion.key().id()))
        self.flush({'status' : 200, 'upload_url' : upload_url})



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