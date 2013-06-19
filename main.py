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
from mogu.login import Login, Top, Menu
from mogu.notice import NoticeInfoUpdate, NoticeList, NoticeUpdate, NoticeDelete, NoticeDetail
from mogu.picture import ImageDownload
from mogu.plugin import PluginList, PluginUpdate, PluginDelete, PluginDetail, PluginDownload, PluginInfoUpdate, PluginInfoAll, PluginSearch, PluginUpload, PluginImageDel, PluginVersionDelete, ImageDel
from mogu.user import UserLogin, UserRegister


app = webapp2.WSGIApplication([
                                  ('/', Login),
                                  ('/login', Login),
                                  ('/top', Top),
                                  ('/menu', Menu),
                                  ('/UserLogin', UserLogin),
                                  ('/UserRegister', UserRegister),

                                  # 插件管理 接口
                                  ('/PluginList', PluginList),
                                  ('/PluginUpdate', PluginUpdate),
                                  ('/PluginUpload', PluginUpload),
                                  ('/PluginImageDel', PluginImageDel),
                                  ('/PluginDelete', PluginDelete),
                                  ('/PluginVersionDelete', PluginVersionDelete),
                                  ('/PluginDetail', PluginDetail),

                                  #插件 手机端接口
                                  ('/PluginDownload', PluginDownload),
                                  ('/PluginInfoUpdate', PluginInfoUpdate),
                                  ('/PluginInfoAll', PluginInfoAll),
                                  ('/PluginSearch', PluginSearch),

                                  # 系统消息管理 接口
                                  ('/NoticeList',NoticeList),
                                  ('/NoticeUpdate',NoticeUpdate),
                                  ('/NoticeDelete',NoticeDelete),
                                  ('/NoticeDetail',NoticeDetail),

                                  # 系统消息 手机接口
                                  ('/NoticeInfoUpdate',NoticeInfoUpdate),

                                  # 图片下载 手机接口
                                  ('/download',ImageDownload),
                                  ('/ImageDel',ImageDel),



                              ], debug=True)