#coding=utf-8
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
# from mogu.kind import KindList, KindUpdate, KindDelete, KindAddPlugin, KindMove, KindPluginDelete, KindPluginMove, \
#     FenKindList, FenKindPlugin
from mogu3.login import Login, RegUser, Logout
from mogu.notice import NoticeInfoUpdate, NoticeList, NoticeUpdate, NoticeDelete, NoticeDetail
from mogu.picture import ImageDownload
# from mogu.plugin import PluginList, PluginUpdate, PluginDelete, PluginDetail, PluginDownload, PluginInfoUpdate, \
#     PluginInfoAll, PluginSearch, PluginUpload, PluginImageDel, PluginVersionDelete, ImageDel, UploadHandler, \
#     ServeHandler, PluginUpload2, \
#     GetPluginNameByGamecode
# from mogu.uploadscript import PluginUploadScript, PluginUploadApkScript, PluginUploadApkDataScript
# from mogu.user import UserLogin, UserRegister
# from mogu.website import WebsiteList, WebsiteUpdate, WebsiteDelete
from mogu3.views import Menu, CurrentUser, PluginList, PluginUpdate, UploadHandler, IconUploadHandler, \
    ImageUploadHandler, PluginImageUpdate
from mogu3.views_kind import KindList, KindUpdate, KindMove, KindAddPlugin, KindDelPlugin, KindDel


app = webapp2.WSGIApplication([
                                  ('/login', Login),
                                  ('/logout', Logout),
                                  ('/regUser', RegUser),
                                  # ('/top', Top),
                                  ('/menu.xml', Menu),
                                  ('/currentUser', CurrentUser),
                                  # ('/UserLogin', UserLogin),
                                  # ('/UserRegister', UserRegister),

                                  # 插件管理 接口
                                  ('/PluginList', PluginList),
                                  ('/PluginUpdate', PluginUpdate),
                                  ('/PluginImageUpdate', PluginImageUpdate),
                                  # ('/PluginUpload', PluginUpload),
                                  # ('/PluginUpload2', PluginUpload2),
                                  # ('/PluginImageDel', PluginImageDel),
                                  # ('/PluginDelete', PluginDelete),
                                  # ('/PluginVersionDelete', PluginVersionDelete),
                                  # ('/PluginDetail', PluginDetail),
                                  #
                                  #
                                  ('/imageupload', ImageUploadHandler),
                                  ('/iconupload', IconUploadHandler),
                                  ('/upload', UploadHandler),
                                  # ('/PluginUploadScript', PluginUploadScript),
                                  # ('/PluginUploadApkScript', PluginUploadApkScript),
                                  # ('/PluginUploadApkDataScript', PluginUploadApkDataScript),
                                  # ('/serve/([^/]+)?/([0-9]+)?/([0-9]+)?/$', ServeHandler),
                                  # ('/serve/([^/]+)?', ServeHandler),
                                  #
                                  #
                                  # #插件 手机端接口
                                  # ('/PluginDownload', PluginDownload),
                                  # ('/PluginInfoUpdate', PluginInfoUpdate),
                                  # ('/PluginInfoAll', PluginInfoAll),
                                  # ('/PluginSearch', PluginSearch),

                                  # 系统消息管理 接口
                                  ('/NoticeList', NoticeList),
                                  ('/NoticeUpdate', NoticeUpdate),
                                  ('/NoticeDelete', NoticeDelete),
                                  ('/NoticeDetail', NoticeDetail),

                                  # 系统消息 手机接口
                                  ('/NoticeInfoUpdate', NoticeInfoUpdate),

                                  # 图片下载 手机接口
                                  ('/download', ImageDownload),
                                  # ('/ImageDel', ImageDel),
                                  # ('/WebsiteList', WebsiteList),
                                  # ('/WebsiteUpdate', WebsiteUpdate),
                                  # ('/WebsiteDelete', WebsiteDelete),
                                  #
                                  ('/KindList', KindList),
                                  # ('/FenKindList', FenKindList),
                                  # ('/FenKindPlugin', FenKindPlugin),
                                  #
                                  ('/KindUpdate', KindUpdate),
                                  ('/KindAddPlugin', KindAddPlugin),
                                  ('/KindDelete', KindDel),
                                  ('/KindMove', KindMove),
                                  # ('/KindPluginMove', KindPluginMove),
                                  ('/KindPluginDelete', KindDelPlugin),


                                  #以js的形式提供接口
                                  # ('/getPluginNameByGamecode', GetPluginNameByGamecode),

                              ], debug=True)
