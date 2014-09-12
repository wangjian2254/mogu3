# coding=utf-8
# Date:2014/9/12
#Email:wangjian2254@gmail.com
from datetime import datetime
from google.appengine.api import memcache
from mogu.models.model import Plugin, PluginCount
from mogu3.login import login_required, get_current_user
from tools.page import Page

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
            page = int(self.request.get('page','0'))
            cachename = 'applist_%s' % (page)
            cacheresult = memcache.get(cachename)
            if cacheresult:
                self.flush(cacheresult)
                return
            if not page:
                query = Plugin.all().order('__key__').fetch(30)
            else:
                query = Plugin.all().order('__key__').fetch(30, 30*page)
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
                     'imageid': plugin.imageid, 'date': plugin.date.strftime('%Y-%m-%d %H:%M'),
                     'lastUpdateTime': plugin.lastUpdateTime.strftime('%Y-%m-%d %H:%M'), 'username': plugin.username,
                     'isactive': plugin.isactive}
                l.append(p)
        self.getResult(True,u'获取应用列表', {'list': l, 'count': count}, cachename=cachename)