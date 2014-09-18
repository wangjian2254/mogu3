# coding=utf-8
#
from setting import RankUri

__author__ = u'王健'
from mogu.models.model import Users
from tools.page import Page

import urllib


__author__ = 'wangjian2254'

loginurl = '/login'


def login_required(fn):
    def auth(*arg):
        web = arg[0]
        user = get_current_user(web)
        if user.get('username'):
            fn(*arg)
        else:
            # web.redirect('/paper/234.html','post')
            web.getResult(False, u'请先登录', None, 404)
    return auth


def login_required_admin(fn):
    @login_required
    def auth(*arg):
        web = arg[0]
        user = get_current_user(web)
        if user.get('auth') == 'admin':
            fn(*arg)
        else:
            # web.redirect('/paper/234.html','post')
            web.getResult(False, u'权限不足', None, 404)
    return auth


def setLogin(web, user):
    setCookie = 'webusername=%s;' % user.username.encode('utf-8')
    web.response.headers.add_header('Set-Cookie', setCookie + 'Max-Age = 3600000;path=/;')
    if user.name:
        setCookie = 'webnickname=%s;' % user.username.encode('utf-8')
        web.response.headers.add_header('Set-Cookie', setCookie + 'Max-Age = 3600000;path=/;')
    setCookie = 'auth=%s;' % user.auth.encode('utf-8')
    # setCookie=str(setCookie)
    web.response.headers.add_header('Set-Cookie', setCookie + 'Max-Age = 3600000;path=/;')


def setLogout(web):
    setCookie = 'webusername=;'
    web.response.headers.add_header('Set-Cookie', setCookie + 'Max-Age = 3600000;path=/;')
    setCookie = 'webnickname=;'
    web.response.headers.add_header('Set-Cookie', setCookie + 'Max-Age = 3600000;path=/;')
    setCookie = 'auth=;'
    web.response.headers.add_header('Set-Cookie', setCookie + 'Max-Age = 3600000;path=/;')


def get_current_user(web):
    guist = {}
    Cookies = {}  # tempBook Cookies
    Cookies['request_cookie_list'] = [{'key': cookie_key, 'value': cookie_value} for cookie_key, cookie_value in
                                      web.request.cookies.iteritems()]
    for c in Cookies['request_cookie_list']:
        if c['key'] == 'webusername':
            guist["username"] = c['value']
        if c['key'] == 'webnickname':
            guist["name"] = urllib.unquote(c['value'].encode("utf-8"))
        if c['key'] == 'auth':
            guist["auth"] = c['value']
    if guist and guist.has_key('username'):
        # user = Users.all().filter('username =', guist['username']).fetch(1)
        # if user:
        return guist
    return False


class Login(Page):
    # def get(self, *args):
    # fromurl = self.request.get('fromurl', '/')
    # self.render('template/login.html', {'fromurl': fromurl})

    def post(self, *args):
        username = self.request.get('username')
        password = self.request.get('password')
        fromurl = self.request.get('fromurl', None)
        if len(Users.all().fetch(1)) == 0:
            u = Users()
            u.name = 'admin'
            u.username = 'admin@gmail.com'
            u.password = 'admin'
            u.auth = 'admin'
            u.put()
        user = Users.all().filter('username =', username).filter('password =', password).fetch(1)
        if user:
            user = user[0]
            setLogin(self, user)
            #            if fromurl:
            #                self.redirect(fromurl)
            #            else:
            self.getResult(True, u'登录成功', None)
            # self.render('template/workframe.html', {})
        else:
            self.getResult(False, u'用户名密码错误', None)


class RegUser(Page):
    def get(self, *args):
        self.render('template/regUser.html', {})

    def post(self, *args):
        username = self.request.get('username')
        password = self.request.get('password')
        password2 = self.request.get('opassword')

        if password != password2:
            self.getResult(False, u'密码和确认密码不一致', None)
            return

        user = Users.all().filter('username =', username).fetch(1)
        if user:
            self.getResult(False, u'用户名已经被占用，请换一个用户名', None)
            return
        else:
            u = Users()
            u.name = username
            u.username = username
            u.password = password
            u.auth = 'user'
            u.put()
            setLogin(self, u)
            self.getResult(True, u'注册成功.',
                           {'username': u.username, 'truename': u.username, 'id': u.username})


class Logout(Page):
    def get(self, *args):
        # fromurl = '/'
        setLogout(self)
        self.getResult(True, '')


        # class Top(Page):
        # @login_required
        #     def get(self):
        #         self.render('template/topnav.html', {})
        #
        #
        # class Menu(Page):
        #     @login_required
        #     def get(self):
        #         user = get_current_user(self)
        #         if user.auth == 'admin':
        #             self.render('template/menu.html', {'RankUri': RankUri})
        #         if user.auth == 'user':
        #             self.render('template/menu2.html', {'RankUri': RankUri})
        #
        #