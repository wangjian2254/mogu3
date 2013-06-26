#coding=utf-8
#author:u'王健'
#Date: 13-6-1
#Time: 下午9:19
import logging
from mogu.models.model import UserNameNumber, User
from tools.page import Page
from tools.util import getResult

__author__ = u'王健'




def getUname():
#    memname=memcache.get('username')
    unn=UserNameNumber.get_by_key_name('userNameNumber')
#    if not memname:
    if not unn:
        unn=UserNameNumber(key_name='userNameNumber')
        ul=User.all().order('-__key__').fetch(1)
        if ul:
            u=ul[0]
            uname=u.key().name()
            unames=uname.split('u')
            if len(unames)>=3:
                uname=unames[2]
            else:
                uname='1000'
            if len(uname)<=3:
                uname='1000'
            else:
                uname=str(int(uname)+1)
        else:
            uname='1000'
    else:
        uname=str(unn.userName+1)
#    else:
#        uname=str(int(memname)+1)
#    memcache.set('username',uname,3600)
    unn.userName=int(uname)
    unn.put()
    if User.get_by_keyname('u'+str(len(uname))+'u'+uname):
        return getUname()
    else:
#        u=User(key_name='u'+str(len(uname))+'u'+uname)
#        u.userName=uname
#        u.passWord=uname
#        u.trueName=''
#        u.tele=''
#        u.mobile=''
#        u.put()
        return uname


class UserRegister(Page):
    def get(self):
        try:


            UserName = self.request.get('UserName')
            UserPwd = self.request.get('UserPwd')
            if not UserName:
                self.response.out.write(getUname())
                return
            try:
                int(UserName)
                int(UserPwd)
            except :
                self.flush(getResult(None,False,u'用户名或密码不是数字'))
                return
            #没有进行参数正确验证
            if UserName=='' or UserPwd=='':
                self.flush(getResult(None,False,u'用户名和密码不能为空'))
                return


            user = User.get_by_keyname('u'+UserName)
            if not user:
                user = User(key_name='u'+str(len(UserName))+'u'+UserName)
                user.userName = self.request.get('UserName').strip('\n')
                user.passWord = self.request.get('UserPwd').strip('\n')
                # user.trueName = self.request.get('trueName').strip('\n')
                # user.tele = self.request.get('tele').strip('\n')
                # user.mobile = self.request.get('mobile').strip('\n')
                user.put()
                # addInit(user.userName,user.trueName,user.tele,user.mobile)#默认初始化订阅
                self.flush(getResult(None))
            else:
                self.flush(getResult(None,False,u'保存用户信息时出错，请稍后再试。'))

        except Exception,e:
            logging.error('user register:'+str(e))
            self.response.out.write(getResult(None,False,u'系统错误，请稍后再试。'))



class UserLogin(Page):
    def get(self):
        UserName = self.request.get('UserName')
        UserPwd = self.request.get('UserPwd')
        ulist=User.all().filter('userName =',UserName).filter("passWord =",UserPwd).fetch(1)
        if ulist:
            self.flush(getResult(None))
        else:
            self.flush(getResult(None,False,u'用户名或密码不正确。'))
        pass
  