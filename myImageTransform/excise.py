# coding: utf-8
__author__ = 'Ivan'
from PIL import Image
import requests

class MyImage(object):
    def __init__(self, url):
        self.url=url
        self.filename=self.get_image_filename()
        self.im = self.get_image_file()

    def get_size(self):
        return self.im.size



    def get_compress_image(self, dst_w=0, dst_h=0):
        ori_w, ori_h = self.get_size()
        w_ratio, h_ratio = None, None
        if 0<dst_w<ori_w or 0<dst_h<ori_h:
            if 0<dst_w<ori_w:
                w_ratio=float(dst_w)/ori_w
            if 0<dst_h<ori_h:
                h_ratio=float(dst_h)/ori_h
            min_ratio = min(s for s in [w_ratio, h_ratio] if s)
            re_width, re_height = int(ori_w*min_ratio), int(ori_h*min_ratio)
        else:
            re_width, re_height=ori_w,ori_h

        # 根据压缩后的像素尺寸进行resize,并另存为filename
        self.im.resize((re_width, re_height), Image.ANTIALIAS).save(self.filename)

    def get_image_filename(self):
        re_result=re.search('.*/(.+)', self.url)
        if re_result:
            return re_result.group(1)

        # 如果不是类似 https://imgsa.baidu.com/forum/pic/item/462309f790529822a8f35517dbca7bcb0b46d426.jpg的格式
        # 那么获取文件类型
        re_result = re.search('.*\.(.*)', url)
        if re_result:
            file_type=re_result.group(1)
            return 'temp.'+file_type
        return 'temp.jpg'

    def get_image_file(self):
        r = requests.get(self.url, stream=True)
        with open(self.filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

        # 获取filename文件句柄
        return Image.open(self.filename)

import re
if __name__ == '__main__':
    url=' w_500 , h_300 /http://img.zcool.cn/community/0117e2571b8b246ac72538120dd8a4.jpg'
    t=re.search('(?P<transform_params>.*?)/(?P<image_url>.+)', url)
    # t = re.search('.*\.(.*)', url)
    print(t.group('transform_params'))
    params=t.group('transform_params')
    params=params.split(',')
    params = [s.strip() for s in params ]
    params=','.join(params)
    print(params)
    # my_img=MyImage(url)
    # my_img.get_image_file()
    # my_img.get_compress_image(500)