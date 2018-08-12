__author__ = 'Ivan'
#|h_[0-9]+|w_[0-9]+,h_[0-9]+
import re
temp='h_20, w_80, h_90'
temp_sp = temp.split(',')
def re_handle(pattern, str_):
    re.match(pattern, str_)
def re_test(args):
    for item in args:
        item_strip=item.strip()
        result = re.match('^w_(?P<width_in_pixel>[0-9]+)$', item_strip)
        if result:
            yield {'w': int(result.group('width_in_pixel'))}
        result = re.match('^h_(?P<height_in_pixel>[0-9]+)$', item_strip)
        if result:
            yield {'h': int(result.group('height_in_pixel'))}


for im in re_test(temp_sp):
    print(im)

# result=re.search('^w_[0-9]+$|^h_([0-9])+$|w_([0-9])+,h_([0-9])+$',temp)
# print(result)
# print(result.group())