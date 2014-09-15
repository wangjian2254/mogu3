#coding=utf-8
#author:u'王健'
#Date: 13-6-1
#Time: 下午11:59
from google.appengine.api import memcache
from mogu.models.model import Images
from tools.page import Page

__author__ = u'王健'




class ImageDownload(Page):
    def get(self):
        imgid=self.request.get("image_id")
        if not imgid or imgid == 'null':
            self.error(500)
            return
        img=memcache.get('image_id'+str(imgid))
        if not img:
            img=Images.get_by_id(int(imgid))
            memcache.set('image_id'+str(imgid),img,36000)

        if not img:
            self.error(404)
        else:
            self.response.headers['Content-Type'] = str(img.filetype)
            self.response.headers['Content-Length'] = img.size
            self.response.out.write(img.data)