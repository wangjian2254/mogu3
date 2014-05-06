#coding=utf-8
#author:u'王健'
#Date: 13-6-1
#Time: 下午11:25
import datetime
import urllib
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.blobstore import blobstore, BlobInfo
from google.appengine.ext.webapp import blobstore_handlers
from mogu.kind import getKindSort
from mogu.login import login_required
from mogu.models.model import Plugin, PluginVersion, Images, WebSiteUrl, Kind
from tools.page import Page
from tools.util import getResult

__author__ = u'王健'

timezone = datetime.timedelta(hours=8)


class PluginUpdate(Page):
    @login_required
    def get(self):
        id = self.request.get('id', None)
        plugin = {}
        if id:
            plugin = Plugin.get_by_id(int(id))

        self.render('template/plugin/pluginUpdate.html', {'plugin': plugin, 'id': id})

    def post(self):
        noteupdate = datetime.datetime.utcnow() + timezone
        id = self.request.get('id', None)
        name = self.request.get('name', None)
        # kind = self.request.get('kind', None)
        # kinds = []
        # if kind:
        #     kinds = kind.split()
        code = self.request.get('code', None)
        appcode = self.request.get('appcode', None)
        desc = self.request.get('desc', None)
        if id:
            plugin = Plugin.get_by_id(int(id))
        else:
            plugin = Plugin()

        plugin.name = name
        # plugin.kinds = kinds
        plugin.code = code
        plugin.appcode = appcode
        plugin.desc = desc
        plugin.lastUpdateTime = noteupdate
        if not id and 0 < Plugin.all().filter('appcode =', appcode).count():
            self.render('template/plugin/pluginUpdate.html',
                        {'plugin': plugin, 'id': id, 'result': 'warning', 'msg': u'插件包名已经存在。'})
            return
        imgfield = self.request.POST.get('icon')
        if hasattr(imgfield, 'type'):
            if imgfield.type.lower() in ['image/pjpeg', 'image/x-png', 'image/x-icon', 'image/jpeg', 'image/png',
                                         'image/gif', 'image/jpg']:
                imgfile = Images()
                imgfile.filename = imgfield.filename
                imgfile.filetype = imgfield.type
                imgfile.data = db.Blob(imgfield.file.read())
                imgfile.size = imgfield.bufsize
                imgfile.put()
                plugin.imageid = imgfile.key().id()
        plugin.put()
        self.render('template/plugin/pluginUpdate.html',
                    {'plugin': plugin, 'id': plugin.key().id(), 'result': 'succeed', 'msg': u'修改成功。'})


class PluginUpload(Page):
    def get(self):
        id = self.request.get('id', None)
        pluginid = self.request.get('pluginid', None)
        plugin = {}
        pluginVersionList = []
        if pluginid:
            plugin = Plugin.get_by_id(int(pluginid))
            pluginVersionList = PluginVersion.all().filter('plugin =', int(pluginid)).order('-versionnum')

        pluginVersion = {}
        if id:
            pluginVersion = PluginVersion.get_by_id(int(id))
            if not pluginid or pluginVersion.plugin != int(pluginid):
                plugin = Plugin.get_by_id(pluginVersion.plugin)

        self.render('template/plugin/pluginUpload.html',
                    {'plugin': plugin, 'pluginVersion': pluginVersion, 'pluginVersionList': pluginVersionList, 'id': id,
                     'pluginid': pluginid})

    def post(self):
        pluginid = self.request.get('pluginid', '')
        needBigData = False
        id = self.request.get('id', '')
        versioncode = self.request.get('versioncode', '')
        versionnum = self.request.get('versionnum', '')
        updateDesc = self.request.get('updateDesc', '')
        if id:
            pluginVersion = PluginVersion.get_by_id(int(id))
        else:
            pluginVersion = PluginVersion()
            pluginVersion.plugin = int(pluginid)
        pluginVersion.versioncode = versioncode
        pluginVersion.versionnum = int(versionnum)
        pluginVersion.updateDesc = updateDesc

        appdata = self.request.POST.get('data')
        if appdata != '' and appdata != u'' and appdata != None:
            pluginVersion.data = db.Blob(appdata.file.read())
            pluginVersion.size = appdata.bufsize
        else:
            needBigData = True
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
        plugin = {}
        pluginVersionList = []
        if pluginid:
            plugin = Plugin.get_by_id(int(pluginid))
            pluginVersionList = PluginVersion.all().filter('plugin =', int(pluginid)).order('-versionnum')

        data = {'plugin': plugin, 'pluginVersion': pluginVersion, 'pluginVersionList': pluginVersionList, 'id': id,
                'pluginid': pluginid, 'result': 'succeed', 'msg': u'操作成功。', 'needBigData': needBigData}
        if needBigData:
            upload_url = blobstore.create_upload_url('/upload?pluginversionid=%s' % (pluginVersion.key().id()))
            data['upload_url'] = upload_url
            data['msg'] = u'请上传APK文件。'
            self.render('template/plugin/pluginUpload2.html', data)
        else:
            self.render('template/plugin/pluginUpload.html', data)


class PluginUpload2(Page):
    def get(self):
        pluginid = self.request.get('pluginid', '')
        id = self.request.get('id', '')
        pluginVersionList = []
        if pluginid:
            plugin = Plugin.get_by_id(int(pluginid))
            pluginVersionList = PluginVersion.all().filter('plugin =', int(pluginid)).order('-versionnum')

        pluginVersion = {}
        if id:
            pluginVersion = PluginVersion.get_by_id(int(id))
            if not pluginid or pluginVersion.plugin != int(pluginid):
                plugin = Plugin.get_by_id(pluginVersion.plugin)
        data = {'plugin': plugin, 'pluginVersion': pluginVersion, 'pluginVersionList': pluginVersionList, 'id': id,
                'pluginid': pluginid}
        upload_url = blobstore.create_upload_url('/upload?pluginversionid=%s' % (pluginVersion.key().id()))
        data['upload_url'] = upload_url
        self.render('template/plugin/pluginUpload2.html', data)


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        pluginversionid = self.request.get('pluginversionid')
        pluginversion = PluginVersion.get_by_id(int(pluginversionid))
        if pluginversion.datakey:
            b = BlobInfo.get(pluginversion.datakey)
            b.delete()
        pluginversion.datakey = str(blob_info.key())
        pluginversion.size = blob_info.size
        pluginversion.put()
        self.redirect('/PluginUpload?id=%s' % pluginversionid)


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource, start=None, end=None):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.response.headers['Content-Length'] = blob_info.size
        if start and end:
            self.send_blob(blob_info, start=int(start), end=int(end))
        elif start:
            self.send_blob(blob_info, start=int(start))
        else:
            self.send_blob(blob_info)


class PluginImageDel(Page):
    def get(self):
        pid = self.request.get('pid', None)
        if pid:
            p = PluginVersion.get_by_id(int(pid))
            id = self.request.get('id', None)
            if p and id:
                img = Images.get_by_id(int(id))
                if img:
                    img.delete()
                    self.flush(getResult(id, True, u'图片删除成功。'))
                    return
                p.imageids.remove(int(id))
                p.put()
            else:
                self.flush(getResult(id, False, u'图片删除失败，插件版本不存在。'))
                return
        self.flush(getResult(id, False, u'图片删除失败，图片不存在。'))
        return


class ImageDel(Page):
    def get(self):
        id = self.request.get('id', None)
        if id:
            img = Images.get_by_id(int(id))
            if img:
                img.delete()
                self.flush(getResult(id, True, u'图片删除成功。'))
                return

        self.flush(getResult(id, False, u'图片删除失败，插件版本不存在。'))
        return


class PluginList(Page):
    def get(self):
        pluginList = Plugin.all().filter('isdel =', False).order('-date')
        self.render('template/plugin/pluginList.html', {'pluginList': pluginList})


class PluginDetail(Page):
    def get(self):
        id = self.request.get('id', None)
        plugin = {}
        pluginVersion = {}
        if id:
            plugin = Plugin.get_by_id(int(id))
            pvl = PluginVersion.all().filter('plugin =', int(id)).order('-versionnum').fetch(1)
            if pvl:
                pluginVersion = pvl[0]
        self.render('template/plugin/pluginDetail.html', {'plugin': plugin, 'pluginVersion': pluginVersion})


class PluginDelete(Page):
    def get(self):
        id = self.request.get('id', None)
        if id:
            plugin = Plugin.get_by_id(int(id))
            for pv in PluginVersion.all().filter('plugin =', int(id)):
                if pv.imageids:
                    db.delete(Images.get_by_id(pv.imageids))
                pv.delete()
            plugin.delete()
            self.flush(getResult(id, True, u'删除成功。'))
        else:
            self.flush(getResult('', False, u'删除失败，未提供插件id。'))


class PluginVersionDelete(Page):
    def get(self):
        id = self.request.get('id', None)
        if id:
            pv = PluginVersion.get_by_id(int(id))
            if pv.imageids:
                db.delete(Images.get_by_id(pv.imageids))
            pv.delete()
            self.flush(getResult('', True, u'删除成功。'))
        else:
            self.flush(getResult('', False, u'删除失败，未提供插件id。'))


class PluginDownload(Page):
    def get(self):
        pid = self.request.get('pluginid', None)
        if pid:
            p = Plugin.get_by_id(int(pid))
        pvid = self.request.get('id', None)
        if not pvid:
            pvlist = PluginVersion.all().filter('plugin =', int(pid)).order('-versionnum').fetch(1)
            if len(pvlist):
                pvid = pvlist[0].key().id()
        if pvid:
            pv = PluginVersion.get_by_id(int(pvid))
            if pv:
                if pv.datakey:
                    self.redirect(str('%s/serve/%s' % (WebSiteUrl.getInitUrl(), pv.datakey)))
                    return
                self.response.headers['Content-Type'] = 'application/octet-stream'
                self.response.headers['Content-Length'] = pv.size
                self.response.out.write(pv.data)
                return
        self.error(404)


class PluginInfoUpdate(Page):
    def post(self):
        appcodes = self.request.get('appcodes', '').split(',')
        pluginVersionDict = {}
        for appcode in appcodes:
            versionnum = self.request.get(appcode, '')
            pluginVersionDict[appcode] = {'versionnum': versionnum, 'isdel': True}
            plugin = memcache.get('plugin' + appcode)
            if not plugin:
                plugin = Plugin.all().filter('appcode =', appcode).fetch(1)
                if len(plugin):
                    plugin = plugin[0]
                    memcache.set('plugin' + appcode, plugin, 360000)
            if plugin and plugin.isdel == False:
                pluginVersionDict[appcode]['isdel'] = False
                pluginVersion = memcache.get('newpluginVersion' + appcode)
                if not pluginVersion:
                    pluginVersion = PluginVersion.all().filter('plugin =', plugin.key().id()).order(
                        '-versionnum').fetch(1)
                    if len(pluginVersion):
                        pluginVersion = pluginVersion[0]
                        memcache.set('newpluginVersion' + appcode, pluginVersion, 360000)
                if pluginVersion:
                    pluginVersionDict[appcode]['plugin'] = plugin
                    pluginVersionDict[appcode]['pluginVersion'] = pluginVersion
                    pluginVersionDict[appcode]['newversionnum'] = pluginVersion.versionnum
                if not pluginVersion.data and not pluginVersion.datakey:
                    del pluginVersionDict[appcode]
        # 输出 json 字符串 plugin 对象
        if pluginVersionDict:
            msg = [{"msg": u"新收到%s条插件更新信息" % (len(pluginVersionDict.keys()),), "type": 1}]
        else:
            msg = []
        result = {'pluginlist': jsonToStr(pluginVersionDict), "notice": []}
        self.flush(result)


class PluginInfoAll(Page):
    def get(self):
        pluginVersionDict = {}
        query = Plugin.all().filter('isactive =', True)
        appcode = self.request.get('appcode', None)
        if appcode:
            query.filter('appcode =', appcode)
        for plugin in query.order('-lastUpdateTime'):
            if plugin.isdel:
                pluginVersionDict[plugin.appcode] = {'isdel': plugin.isdel}
            else:
                pluginVersionDict[plugin.appcode] = {'plugin': plugin, 'isdel': plugin.isdel}
                pluginVersion = memcache.get('newpluginVersion' + plugin.appcode)
                if not pluginVersion:
                    pluginVersion = PluginVersion.all().filter('plugin =', plugin.key().id()).order(
                        '-versionnum').fetch(1)
                    if len(pluginVersion):
                        pluginVersion = pluginVersion[0]
                        memcache.set('newpluginVersion' + plugin.appcode, pluginVersion, 360000)
                if pluginVersion:
                    pluginVersionDict[plugin.appcode]['pluginVersion'] = pluginVersion
                    pluginVersionDict[plugin.appcode]['newversionnum'] = pluginVersion.versionnum
                    pluginVersionDict[plugin.appcode]['size'] = pluginVersion.size
                if not pluginVersion.data and not pluginVersion.datakey:
                    del pluginVersionDict[plugin.appcode]
        kindlist = []
        for i, kind in enumerate(Kind.get_by_id(getKindSort().kindlist)):
            #kindlist.append({'name':kind.name,'index':kind.index,'list':filter(lambda x: x, kind.applist)})
            kindlist.append({'name': kind.name, 'index': i,
                             'list': [getPluginByMemcache(x).appcode for x in kind.applist if
                                      getPluginByMemcache(x).isactive]})
        # 输出 json 字符串 plugin 对象
        result = {'pluginlist': jsonToStr(pluginVersionDict), "notice": [], 'kind': kindlist, 'status': 200,
                  'success': True, 'message': u''}
        self.flush(result)


def jsonToStr(pluginVersionDict):
    jl = []
    for k in pluginVersionDict.keys():
        if pluginVersionDict[k]['isdel']:
            jl.append({'appcode': k, 'isdel': True})
        else:
            p = {'imglist': [], 'appcode': k, 'isdel': False,
                 'url': '%s/serve/%s' % (WebSiteUrl.getInitUrl(), pluginVersionDict[k]['pluginVersion'].datakey),
                 'updateDesc': pluginVersionDict[k]['pluginVersion'].updateDesc,
                 'newversionname': pluginVersionDict[k]['pluginVersion'].versioncode,
                 'newversion': pluginVersionDict[k]['newversionnum'], 'name': pluginVersionDict[k]['plugin'].name,
                 'desc': pluginVersionDict[k]['plugin'].desc,
                 'iconurl': '%s/download?image_id=%s' % (
                     WebSiteUrl.getInitUrl(), pluginVersionDict[k]['plugin'].imageid),
                 'size': pluginVersionDict[k]['pluginVersion'].size,
                 'lastUpdate': pluginVersionDict[k]['pluginVersion'].date.strftime('%Y-%m-%d %H:%M')}
            if not p['size']:
                blob_info = blobstore.BlobInfo.get(pluginVersionDict[k]['pluginVersion'].datakey)
                p['size'] = blob_info.size
                pluginVersionDict[k]['pluginVersion'].size = blob_info.size
                pluginVersionDict[k]['pluginVersion'].put()
            for i, imgid in enumerate(pluginVersionDict[k]['pluginVersion'].imageids):
                p['imglist'].append({'appversion': pluginVersionDict[k]['newversionnum'], 'index': i + 1,
                                     'url': '%s/download?image_id=%s' % (WebSiteUrl.getInitUrl(), imgid)})
            jl.append(p)
    return jl


class PluginSearch(Page):
    def get(self):
        pass


def getPluginByMemcache(id):
    p = memcache.get('pluginid%s' % id)
    if not p:
        p = Plugin.get_by_id(int(id))
        memcache.set('pluginid%s' % id, p, 3600 * 24 * 10)
    return p


class GetPluginNameByGamecode(Page):
    def get(self):
        gamecode = self.request.get('gamecode', None)
        plugin = memcache.get('gamecode%s' % gamecode)
        if not plugin:
            plugin = Plugin.all().filter('appcode =', gamecode).fetch(1)
            memcache.set('gamecode%s' % gamecode, plugin, 3600 * 24 * 10)
        result = "plugindata['%s']='%s';pluginimgdata['%s']='%s';" % (gamecode, plugin.name,gamecode, plugin.imageid)
        self.flush(result)
