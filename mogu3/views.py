# coding=utf-8
# Date:2014/9/12
# Email:wangjian2254@gmail.com
from datetime import datetime
import json
import urllib
from google.appengine.api import memcache
from google.appengine.ext.webapp import blobstore_handlers
from mogu.models.model import Plugin, PluginCount, Users
from mogu3.login import login_required, get_current_user, login_required_admin
from setting import RankUri
from tools.page import Page
from google.appengine.ext.blobstore import blobstore, BlobInfo

__author__ = u'王健'


class Menu(Page):
    @login_required
    def get(self, *args):
        menuxml = '''
        <?xml version='1.0' encoding='utf-8'?>
                <root>

                    <menu  label='应用管理' mod='apkadd'>
                    </menu>
                    <menu label='系统消息管理' mod='notice' >
                    </menu>
                    <menu label='网址管理' mod='uri' >
                    </menu>
                    <menu  label='分类'>
                        <menuitem label='分类管理' mod='kind'></menuitem>
                        <menuitem label='应用排序' mod='appkind'></menuitem>
                    </menu>
                    <menu label='积分、房间管理'>
                        <menuitem label='游戏积分' mod='gamelist'></menuitem>
                        <menuitem label='游戏房间' mod='roomlist'></menuitem>
                    </menu>
                </root>
        '''
        user_menuxml = '''
        <?xml version='1.0' encoding='utf-8'?>
                <root>
                    <menu  label='应用管理'  mod='apkadd'>
                    </menu>

                </root>
        '''
        user = get_current_user(self)
        # if user.get('username') == 'asa':
        #     u = Users.all().filter('username =', 'asa').fetch(1)
        #     if u:
        #         u = u[0]
        #         u.auth = 'admin'
        #         u.put()
        if user.get('auth') == 'admin':
            self.flush(menuxml)
        if user.get('auth') == 'user':
            self.flush(user_menuxml)


class CurrentUser(Page):
    @login_required
    def get(self, *args):
        u = get_current_user(self)
        result = {'username': u.get('username'), 'name': u.get('username'), 'uid': u.get('username'),
                        'auth': u.get('auth')}
        if u.get('auth') == 'admin':
            result['rankurl'] = RankUri
        self.getResult(True, u'', result)


class PluginNameList(Page):
    @login_required_admin
    def get(self, *args):
        cachename = 'appnamelist'
        cacheresult = memcache.get(cachename)
        if cacheresult:
            self.flush(cacheresult)
            return
        l = []
        for p in Plugin.all().filter('isactive =', True).order('__key__'):
            l.append({'id': p.key().id(), 'name': p.name, 'icon': p.imageid})
        self.getResult(True, u'', l, cachename=cachename)

class PluginList(Page):
    @login_required
    def get(self, *args):
        user = get_current_user(self)
        l = []
        count = 0
        query = []
        cachename = ''
        if user.get('auth') == 'admin':
            page = int(self.request.get('page', '0'))
            kind = self.request.get('kind', '')
            cachename = 'applist_%s_%s' % (kind, page)
            cacheresult = memcache.get(cachename)
            if cacheresult:
                self.flush(cacheresult)
                return

            if kind:
                query = Plugin.all().order('index_time')
                query = query.filter('kindids =', int(kind))
                count = query.count()
            else:
                query = Plugin.all().order('__key__')
                count = PluginCount.getPluginCount()
            if not page:
                query = query.fetch(30)
            else:
                query = query.fetch(30, 30 * page)

        if user.get('auth') == 'user':
            cachename = 'user_applist_%s' % (user.get('username'))
            cacheresult = memcache.get(cachename)
            if cacheresult:
                self.flush(cacheresult)
                return
            query = Plugin.all().filter('username =', user.get('username')).order('__key__')
            count = query.count()
        self.plugin_dict(l, count, query, cachename)

    @login_required_admin
    def post(self):
        pluginids = self.request.get('pluginids','')
        import hashlib
        cachename = hashlib.md5(pluginids).hexdigest().upper()
        cacheresult = memcache.get(cachename)
        if cacheresult:
            self.flush(cacheresult)
            return
        pluginids = pluginids.split(',')
        ids = []
        for i in pluginids:
            try:
                ids.append(int(i))
            except:
                pass
        query = Plugin.get_by_id(ids)
        count = len(ids)
        l = []
        self.plugin_dict(l, count, query, cachename)

    def plugin_dict(self, l,count, query, cachename):
        for plugin in query:
            p = {'id': plugin.key().id(), 'name': plugin.name, 'appcode': plugin.appcode, 'code': plugin.code,
                 'imageid': plugin.imageid, 'date': plugin.date.strftime('%Y-%m-%d %H:%M'), 'type': plugin.type,
                 'lastUpdateTime': plugin.lastUpdateTime.strftime('%Y-%m-%d %H:%M'), 'username': plugin.username,
                 'apkkey': plugin.apkkey, 'apkverson': plugin.apkverson, 'desc': plugin.desc,
                 'imagelist': plugin.imagelist, 'updatedesc': plugin.updatedesc, 'downnum': plugin.downnum,
                 'isactive': plugin.isactive, 'status': plugin.status, 'kindids': plugin.kindids}
            l.append(p)
        self.getResult(True, u'获取应用列表', {'list': l, 'count': count}, cachename=cachename)


class PluginApkUpdate(Page):
    @login_required
    def post(self, *args):
        pluginid = self.request.get('pluginid')
        updatedesc = self.request.get('updatedesc')

        if not pluginid:
            self.getResult(False, u'请选择应用。', None)
            return
        else:
            plugin = Plugin.get_by_id(int(pluginid))
        plugin.updatedesc = updatedesc
        plugin.put()
        upload_url = blobstore.create_upload_url('/upload?pluginid=%s' % (plugin.key().id()))
        self.getResult(True, u'保存应用成功',
                       {"pluginid": plugin.key().id(), 'upload_url': upload_url})

class PluginUpdate(Page):
    @login_required
    def post(self, *args):
        user = get_current_user(self)
        appcode = self.request.get('appcode')
        pluginid = self.request.get('pluginid')

        if not pluginid:
            count = Plugin.all().filter("appcode =", appcode).count()
            if count > 0:
                self.getResult(False, u'应用包名（appcode） 在系统中已经存在，请更换应用包名。', None)
                return
            plugin = Plugin()
            plugin.username = user.get('username')
            plugin.kindids.append(int(self.request.get('kind')))
            plugin.index_time = datetime.now()
        else:
            plugin = Plugin.get_by_id(int(pluginid))
            if user.get("auth") != 'admin' and user.get('username') != plugin.username:
                self.getResult(False, u'删除失败，权限不足。', None)
                return
            if len(plugin.kindids) == 0:
                plugin.kindids.append(int(self.request.get('kind')))
            else:
                plugin.kindids[0] = int(self.request.get('kind'))

        plugin.name = self.request.get('name', '')
        plugin.appcode = self.request.get('appcode', '')
        plugin.desc = self.request.get('desc', '')
        plugin.type = self.request.get('type')
        plugin.code = self.request.get('code')
        plugin.put()
        upload_url = blobstore.create_upload_url('/upload?pluginid=%s' % (plugin.key().id()))
        upload_icon_url = blobstore.create_upload_url('/iconupload?pluginid=%s' % (plugin.key().id()))
        self.getResult(True, u'保存应用成功',
                       {"pluginid": plugin.key().id(), 'upload_url': upload_url, 'upload_icon_url': upload_icon_url})


class PluginDelete(Page):
    @login_required
    def get(self, *args):
        user = get_current_user(self)
        pluginid = self.request.get('pluginid')
        plugin = Plugin.get_by_id(int(pluginid))
        if not plugin:
            self.getResult(True, u'删除成功。', None)
            return
        if user.get("auth") == 'admin' or user.get('username') == plugin.username:
            plugin.delete()
            self.getResult(True, u'删除成功。', None)
        else:
            self.getResult(False, u'删除失败，权限不足。', None)



class PluginAddKind(Page):
    @login_required_admin
    def get(self, *args):
        pluginid = self.request.get('pluginid')
        kindid = self.request.get('kindid')
        plugin = Plugin.get_by_id(int(pluginid))
        if int(kindid) not in plugin.kindids:
            plugin.kindids.append(int(kindid))
            plugin.put()
            self.getResult(True, u'加入分类成功。', None)
        else:
            self.getResult(False, u'应用已经在分类内了。', None)


class PluginOutKind(Page):
    @login_required_admin
    def get(self, *args):
        pluginid = self.request.get('pluginid')
        kindid = self.request.get('kindid')
        plugin = Plugin.get_by_id(int(pluginid))
        if int(kindid) in plugin.kindids:
            plugin.kindids.remove(int(kindid))
            plugin.put()
            self.getResult(True, u'应用移出成功。', None)
        else:
            self.getResult(False, u'应用已经不在分类内了。', None)


class PluginTop(Page):
    @login_required_admin
    def get(self, *args):
        pluginid = self.request.get('pluginid')
        kindid = self.request.get('kindid')
        plugin = Plugin.get_by_id(int(pluginid))
        query = Plugin.all().filter('kindids =', int(kindid)).order('index_time').fetch(1)
        for p in query:
            if p.key().id() != plugin.key().id():
                import datetime as dt
                plugin.index_time = p.index_time - dt.timedelta(minutes=1)
                plugin.put()
                self.getResult(True, u'置顶成功。', None)
            else:
                self.getResult(False, u'置顶失败。', None)


class PluginImageUpdate(Page):
    @login_required
    def get(self, *args):
        pluginid = self.request.get('pluginid')
        upload_icon_url = blobstore.create_upload_url('/imageupload?pluginid=%s' % pluginid)
        self.getResult(True, u'', upload_icon_url)



class IconUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        if not upload_files:
            self.response.out.write(
                json.dumps({'success': False, 'message': u'上传图标失败', 'status_code': 200, 'dialog': 1}))
            return
        blob_info = upload_files[0]
        pluginid = self.request.get('pluginid')
        plugin = Plugin.get_by_id(int(pluginid))
        if plugin.imageid:
            b = BlobInfo.get(plugin.imageid.split('.')[0])
            if b:
                b.delete()
        plugin.imageid = '%s.%s' % (str(blob_info.key()), blob_info.filename.split('.')[-1])
        plugin.put()
        self.response.out.write(json.dumps({'success': True, 'message': u'上传图标成功', 'status_code': 200, 'dialog': 1}))


class ImageUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        if not upload_files:
            self.response.out.write(
                json.dumps({'success': False, 'message': u'上传应用图片失败', 'status_code': 200, 'dialog': 1}))
            return
        blob_info = upload_files[0]
        pluginid = self.request.get('pluginid')
        plugin = Plugin.get_by_id(int(pluginid))
        plugin.imagelist.append('%s.%s' % (str(blob_info.key()), blob_info.filename.split('.')[-1]))
        plugin.put()
        self.response.out.write(json.dumps(
            {'success': True, 'result': '%s.%s' % (str(blob_info.key()), blob_info.filename.split('.')[-1]),
             'message': u'上传应用图片成功', 'status_code': 200, 'dialog': 1}))


class DeleteAppImage(Page):
    @login_required
    def post(self):
        imgid=self.request.get("imagekey", '')
        filename = str(urllib.unquote(imgid))
        pluginid = self.request.get('pluginid')
        plugin = Plugin.get_by_id(int(pluginid))
        imgid = imgid.split('.')[0]


        if filename in plugin.imagelist:
            plugin.imagelist.remove(filename)
            plugin.put()
            img = BlobInfo.get(imgid)
            if img:
                img.delete()
            self.getResult(True, u'图片删除成功', None)
            return
        self.getResult(False, u'图片删除失败', None)

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        if not upload_files:
            self.response.out.write(
                json.dumps({'success': False, 'message': u'上传APK失败', 'status_code': 200, 'dialog': 1}))
            return
        blob_info = upload_files[0]
        pluginid = self.request.get('pluginid')
        plugin = Plugin.get_by_id(int(pluginid))
        if plugin.apkkey:
            b = BlobInfo.get(plugin.apkkey)
            if b:
                b.delete()
        plugin.apkkey = str(blob_info.key())
        plugin.apkverson += 1
        plugin.type_status = 1
        plugin.put()
        self.response.out.write(json.dumps({'success': True, 'message': u'上传APK成功', 'status_code': 200, 'dialog': 1}))
