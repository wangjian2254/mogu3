#coding=utf-8
#author:u'王健'
#Date: 13-6-1
#Time: 下午11:59
import urllib
from google.appengine.api import memcache
from google.appengine.ext.blobstore import blobstore, BlobInfo
from google.appengine.ext.webapp import blobstore_handlers
from mogu.models.model import Images
from tools.page import Page

__author__ = u'王健'




class ImageDownload(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        imgid=self.request.get("image_id")
        if not imgid or imgid == 'null':
            self.error(500)
            return
        img = memcache.get('image_id'+str(imgid))
        if not img:
            resource = str(urllib.unquote(imgid))
            img = blobstore.BlobInfo.get(resource)
            memcache.set('image_id'+str(imgid), img, 36000)

        if not img:
            self.error(404)
        else:
            self.response.headers['Content-Type'] = str(img.content_type)
            self.response.headers['Content-Length'] = img.size
            self.send_blob(img)
#
# class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
#     def get(self, resource, start=None, end=None):
#         resource = str(urllib.unquote(resource))
#         pvquery=PluginVersion.all().filter('datakey =',resource).fetch(1)
#         if len(pvquery)>0:
#             pv = pvquery[0]
#             plugin = PluginDownloadNum.get_by_key_name('pluginid_%s'%pv.plugin)
#             if plugin:
#                 plugin.downnum+=1
#                 plugin.put()
#         blob_info = blobstore.BlobInfo.get(resource)
#         self.response.headers['Content-Length'] = blob_info.size
#         if start and end:
#             self.send_blob(blob_info, start=int(start), end=int(end))
#         elif start:
#             self.send_blob(blob_info, start=int(start))
#         else:
#             self.send_blob(blob_info)