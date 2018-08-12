# coding: utf-8
import re
import os

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.views import View
import requests
from PIL import Image

from myImageTransform import settings
# Create your views here.

class MyImage(object):
    def __init__(self, url):
        self.url = url
        self.filename = self.get_image_filename()
        self.filepath = os.path.join(settings.MEDIA_ROOT,self.filename)
        self.im = self.get_image_file()

    def get_size(self):
        return self.im.size

    def get_compress_image(self, dst_w=0, dst_h=0):
        """
        Compress pictures according to width and height
        :param dst_w: pixel of target width
        :param dst_h: pixel of target height
        :return:
        """
        ori_w, ori_h = self.get_size()
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
        self.im.resize((re_width, re_height), Image.ANTIALIAS).save(self.filepath)

    def get_image_filename(self):
        """
        get the image filename according to self.url
        :return: image filename
        """
        re_result = re.search('.*/(.+)', self.url)
        if re_result:
            return re_result.group(1)

        # 如果不是类似 https://imgsa.baidu.com/forum/pic/item/462309f790529822a8f35517dbca7bcb0b46d426.jpg的格式
        # 那么获取文件类型
        re_result = re.search('.*\.(.*)', self.url)
        if re_result:
            file_type = re_result.group(1)
            return 'temp.' + file_type
        return 'temp.jpg'

    def get_image_file(self):
        """
        Get third-party images through requests.get, write them to the file,
        and finally return the file handle
        :return: the Image object
        """
        r = requests.get(self.url, stream=True)
        with open(self.filepath, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

        # 获取filename文件句柄
        return Image.open(self.filepath)


class ResizeImage(View):
    def get(self, request, transform_params, image_url):
        """
        :param request:
        :param transform_params: 类似w_{width_in_pixel}, h_{height_in_pixel}
        :param image_url:类似 https://imgsa.baidu.com/forum/pic/item/462309f790529822a8f35517dbca7bcb0b46d426.jpg
        :return:
        """
        # 第一步：正则表达式分析transform_params
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
        my_img = MyImage(image_url)
        my_img.get_image_file()
        my_img.get_compress_image(width_in_pixel, height_in_pixel)
        # image_data=open(my_img.filepath, 'rb').read()
        return FileResponse(open(my_img.filepath, 'rb'), content_type='image/jpeg')
