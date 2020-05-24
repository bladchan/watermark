# -*- coding: utf-8 -*-
# Created by bladchan
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os
import colorsys
import sys


def get_dominant_color(image):  # 返回图片的支配色
    image = image.convert('RGBA')
    image.thumbnail((200, 200))
    max_score = 0
    dominant_color = (255, 255, 255)
    for count, (r, g, b, a) in image.getcolors(image.size[0] * image.size[1]):
        # 跳过纯黑色
        if a == 0:
            continue
        saturation = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[1]
        y = min(abs(r * 2104 + g * 4130 + b * 802 + 4096 + 131072) >> 13, 235)
        y = (y - 16.0) / (235 - 16)
        if y > 0.9:
            continue
        score = (saturation + 0.1) * count
        if score > max_score:
            max_score = score
            dominant_color = (r, g, b)
    return dominant_color


def add_watermark(filename, text, size, flag):
    font = ImageFont.truetype('msyh.ttf', size, encoding="unic")
    w1, h1 = font.getsize(text)
    w1 += 3
    h1 += 3
    image = Image.open(filename)
    w = image.width
    h = image.height
    if w1 > w or h1 > h:
        return 0
    draw = ImageDraw.Draw(image)
    # 判断水印是否清晰
    pixels = image.load()
    if flag:
        for i in range(w - w1, w, 1):
            for j in range(h - h1, h, 1):
                pixels[i, j] = (220, 220, 220)
        rgb = (0, 0, 0)
    else:
        crop_img = image.crop((w - w1, h - h1, w, h))
        avg_rgb = get_dominant_color(crop_img)
        print(avg_rgb)
        if avg_rgb[0] <= 128 and avg_rgb[1] <= 128 and avg_rgb[2] <= 128:
            rgb = (255, 0, 0)  # 深色 添加红色水印以加强对比度
        else:
            rgb = (0, 0, 0)  # 浅色 添加黑色水印
    draw.text((w - w1, h - h1), text, rgb, font=font)
    image.save(sys.path[0] + '\\output\\' + filename[0:-4] + '_marked.' + filename[-3:])
    return 1


if __name__ == '__main__':
    d = sys.path[0]
    a = os.listdir(d)
    flag = 1  # 是否加背景色以防止原图背景与水印冲突，建议添加 1:水印添加背景 0:水印不添加背景
    # 注：如果选择不添加背景色，将根据添加水印区域的平均rgb判断，浅色添加黑色水印，深色添加红色水印
    name = "这是水印"  # 水印内容 自适应
    suffix = ['png', 'jpg']  # 需要添加水印的图片类型列表
    size = 30  # 水印字体大小
    if not os.path.isdir(d + '/output'):  # 创建输出目录
        os.makedirs(d + '/output')
    count = 0
    for i in a:
        if i[-3:] in suffix:
            if add_watermark(i, name, size, flag):
                count += 1
            else:
                print("Error : 文件", d + '/' + i, "因水印长度超出图片长度而无法添加")
    print("Info : 共给", count, "个文件添加水印")
