#coding=utf-8
#author:u'王健'
#Date: 13-6-1
#Time: 下午11:59
from datetime import datetime
import urllib
import uuid
from google.appengine.api import memcache
from google.appengine.ext.blobstore import blobstore, BlobInfo
from google.appengine.ext.webapp import blobstore_handlers
from mogu.models.model import Images, Plugin

__author__ = u'王健'

imagetype = ['image/pjpeg', 'image/x-png', 'image/x-icon', 'image/jpeg', 'image/png',
                                         'image/gif', 'image/jpg']


class ImageDownload(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self,imgid):
        # imgid=self.request.get("image_id")
        if not imgid or imgid == 'null':
            self.error(500)
            return
        imgid = imgid.split('.')[0]

        img = memcache.get('image_id%s'%imgid)
        last_modefy = self.request.headers.environ.get("HTTP_IF_MODIFIED_SINCE", None)
        if not img or not last_modefy or img < last_modefy:
            resource = str(urllib.unquote(imgid))
            img = blobstore.BlobInfo.get(resource)
        else:
            self.abort(304)
        if not img:
            self.error(404)
        else:
            modified = datetime.now().strftime('%Y-%m-%d %H:%M')
            self.response.headers['Content-Length'] = img.size
            self.response.headers['Last-Modified'] = modified
            memcache.set('image_id%s' % imgid, modified, 3600*24*7)
            self.send_blob(img)


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource, start=None, end=None):
        resource = str(urllib.unquote(resource))
        if not start:
            pvquery = Plugin.all().filter('apkkey =', resource).fetch(1)
            if len(pvquery) > 0:
                plugin = pvquery[0]
                plugin.downnum += 1
                plugin.put(download=True)
        blob_info = blobstore.BlobInfo.get(resource)
        if not blob_info:
            self.error(404)
            return
        self.response.headers['Content-Length'] = blob_info.size
        if start and end:
            self.send_blob(blob_info, start=int(start), end=int(end))
        elif start:
            self.send_blob(blob_info, start=int(start))
        else:
            self.send_blob(blob_info)


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