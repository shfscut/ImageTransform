# coding: utf-8
import re
import os

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.views import View
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
    def __init__(self, url):
        self.url = url
        self.imagename = self.get_image_name()
        self.filepath = os.path.join(settings.MEDIA_ROOT,self.imagename)
        self.im = self.create_image_from_url()

    def get_image_size(self):
        return self.im.size

    def compress_image(self, dst_w=0, dst_h=0):
        ori_w, ori_h = self.get_image_size()
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

    def get_image_name(self):
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

    def create_image_from_url(self):
        r = requests.get(self.url, stream=True)
        try:
            r.raise_for_status() # Raises stored HTTPError, if one occurred
        except HTTPError:
            raise

        try:
            with open(self.filepath, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)
            im = Image.open(self.filepath)
        except OSError:
            raise
        # 获取filename文件句柄
        return im


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
            comp_img = CompressImage(image_url)
            comp_img.create_image_from_url()
            comp_img.compress_image(width_in_pixel, height_in_pixel)
        except HTTPError as e:
            print(str(e))
            return HttpResponse(str(e))
        except OSError as e:
            print(str(e))
            return HttpResponse(str(e))
        # image_data=open(my_img.filepath, 'rb').read()
        return FileResponse(open(comp_img.filepath, 'rb'), content_type='image/jpeg')


if __name__ == '__main__':
    url = 'http://img.zcool.cn/community/0117e2571b8b238120dd8a4.jpg'
    url_success='http://img.zcool.cn/community/0117e2571b8b246ac72538120dd8a4.jpg'
    r = requests.get(url, stream=True)
    # try:
    #     r.raise_for_status()
    # except HTTPError as e:
    #     print(str(e))
    # if r.status_code:
    #     print('fail')
    # else:
    # with open('temp.jpg', 'wb') as fd:
    #     for chunk in r.iter_content(chunk_size=128):
    #         fd.write(chunk)
    # im=Image.open('testimage.txt')
    # im.size()