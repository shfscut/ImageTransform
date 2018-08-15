# coding: utf-8
import re
import os
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, FileResponse, StreamingHttpResponse
from django.views import View
from django.views.decorators.cache import cache_page

import requests
from requests.exceptions import HTTPError
from PIL import Image

from markdownblog import settings
# Create your views here.

class CompressImage(object):
    """
    1. create_image_from_url:根据url链接，创建图片
    2. get_image_name：根据url链接，获取图片名称
    3. get_image_size：获取原始图片尺寸
    4. compress_image：压缩原始图片
    """
    def __init__(self, url, compress_width=0, compress_height=0):
        self.url = url
        self.compress_width=compress_width
        self.compress_height=compress_height
        self.imagename = self.get_image_name()
        self.source_filepath = os.path.join(settings.MEDIA_ROOT,self.imagename)
        self.compress_filepath=os.path.join(settings.MEDIA_ROOT, 'w{}h{}-{}'.format(compress_width, compress_height, self.imagename))
        self.im = self.create_image_from_url()

    def get_image_size(self):
        return self.im.size

    def get_image_name(self):
        re_result = re.search('.*/(.+)', self.url)
        try:
            return re_result.group(1)
        except AttributeError:
            raise AttributeError("url %r is not correct {image_url}" % (self.url))
        # raise IndexError("url %r is not correct {image_url}"
        #           % (self.url))
        # 如果不是类似 https://imgsa.baidu.com/forum/pic/item/462309f790529822a8f35517dbca7bcb0b46d426.jpg的格式
        # 那么获取文件类型
        # re_result = re.search('.*\.(.*)', self.url)
        # if re_result:
        #     file_type = re_result.group(1)
        #     return 'temp.' + file_type
        # return 'temp.jpg'

    def get_image_object(self):
        try:
            im=Image.open(self.source_filepath)
        except OSError:
            raise
        return im

    def compress_image(self):
        ori_w, ori_h = self.get_image_size()
        dst_w, dst_h = self.compress_width, self.compress_height
        w_ratio, h_ratio = None, None
        if 0 < dst_w < ori_w or 0 < dst_h < ori_h:
            if 0 < dst_w < ori_w:
                w_ratio = float(dst_w) / ori_w
            if 0 < dst_h < ori_h:
                h_ratio = float(dst_h) / ori_h
            min_ratio = min(s for s in [w_ratio, h_ratio] if s)
            re_width, re_height = int(ori_w * min_ratio), int(ori_h * min_ratio)
        else:
            re_width, re_height = ori_w, ori_h

        # 根据压缩后的像素尺寸进行resize,并保存为filename
        self.im.resize((re_width, re_height), Image.ANTIALIAS).save(self.compress_filepath)



    def create_image_from_url(self):
        if os.path.exists(self.source_filepath):
            if self.is_new():
                return self.get_image_object()

        r = requests.get(self.url, stream=True)
        try:
            r.raise_for_status() # Raises stored HTTPError, if one occurred
        except HTTPError:
            raise

        try:
            with open(self.source_filepath, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)
        except OSError:
            raise
        # 获取filename文件句柄
        return self.get_image_object()

    def is_new(self):
        """
        判断self.source_filepath是否为最新的图片
        :return:True or False
        """
        r=requests.head(self.url)
        last_modified = r.headers['Last-Modified']
        dt_last_modified=datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
        timestamp=os.path.getmtime(self.source_filepath)
        # 注意时区问题，要转化成utc
        dt_source_filepath=datetime.utcfromtimestamp(timestamp)
        return dt_source_filepath > dt_last_modified


class ImageProxy(View):
    def get(self, request, transform_params, image_url):
        # 正则表达式分析transform_params
        params_split = transform_params.split(',')

        width_in_pixel, height_in_pixel=0,0
        for item in params_split:
            item_strip = item.strip()
            result = re.match('^w_(?P<w>[0-9]+)$', item_strip)
            if result:
                width_in_pixel = int(result.group('w'))
            result = re.match('^h_(?P<h>[0-9]+)$', item_strip)
            if result:
                height_in_pixel = int(result.group('h'))

        # 第二步 获取image_url
        try:
            comp_img = CompressImage(image_url,width_in_pixel, height_in_pixel)
            comp_img.create_image_from_url()
            comp_img.compress_image()
        except Exception as e:
            return HttpResponse(str(e))
        # image_data=open(my_img.filepath, 'rb').read()
        return HttpResponse(open(comp_img.compress_filepath, 'rb'), content_type='image/jpeg')

@cache_page(10)
def test(request):
    return HttpResponse('test')


