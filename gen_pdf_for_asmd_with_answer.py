# -*- encoding: utf-8 -*-
# The code is unrelated with kid_addition_subtraction. Put it in this repo for backup
# The code is about add/subtract/multiply/divide too, but for generating pdf file to print
# 排版和生成 pdf 部分改自 qyb 的示例代码

from reportlab import platypus
from reportlab.lib.units import inch
import random

def genList(num):
    items = []
    for i in range(num):
        random_num = random.randint(0, 4)
        remainder = random_num % 4 # 随机加减乘除
        if remainder == 0:
            a = random.randint(2, 99)
            b = random.randint(2, 99)
            c = a + b
            items.append(a)
            items.append('+')
            items.append(b)
            items.append('=')
            items.append(' ')
            items.append(a)
            items.append('+')
            items.append(b)
            items.append('=')
            items.append(c)
        elif remainder == 1:
            a = random.randint(4, 99)
            while True:
                b = random.randint(2, 99)
                c = a - b
                if c > 0: # 确保减法的值是正数
                    break
            items.append(a)
            items.append('-')
            items.append(b)
            items.append('=')
            items.append(' ')
            items.append(a)
            items.append('-')
            items.append(b)
            items.append('=')
            items.append(c)
        elif remainder == 2:
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            c = a * b
            items.append(a)
            items.append('×')
            items.append(b)
            items.append('=')
            items.append(' ')
            items.append(a)
            items.append('×')
            items.append(b)
            items.append('=')
            items.append(c)
        else:
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            c = a * b
            items.append(c)
            items.append('÷')
            items.append(a)
            items.append('=')
            items.append(' ')
            items.append(c)
            items.append('÷')
            items.append(a)
            items.append('=')
            items.append(b)
    return items

def genTable(items):
    data = []
    for i in range(0, len(items)/2, 20):
    #生成一个有 10 列的表格数据
        data.append(items[i:i+5] + items[i+10:i+15]) # 跳过有答案的数据
    table = platypus.Table(data, 0.5*inch, 0.19*inch, [('FONT', (0,0), (-1,-1), 'Courier')])
    # 每个cell 0.5' 宽，0.19' 高，差不多 100 题排满一张 A4
    # Courier 是等宽字体，为了俺的算式看起来整齐
    # (0,0)/(-1,-1)说的是font style运用范围，从左上到右下
    return table

def genTable_with_answer(items):
    data = []
    for i in range(5, len(items)/2, 20): # 从有答案的数据开始
    #生成一个有 10 列的表格数据
        data.append(items[i:i+5] + items[i+10:i+15]) # 跳过没答案的数据
    table = platypus.Table(data, 0.5*inch, 0.19*inch, [('FONT', (0,0), (-1,-1), 'Courier')])
    # 每个cell 0.5' 宽，0.19' 高，差不多 100 题排满一张 A4
    # Courier 是等宽字体，为了俺的算式看起来整齐
    # (0,0)/(-1,-1)说的是font style运用范围，从左上到右下
    return table

fname = 'asmd_with_answer.pdf'
title = 'Math'
author = 'qyt'
doc = platypus.SimpleDocTemplate(fname, topMargin=1*inch, bottomMargin=0.8*inch, title=title, author=author)
# 目标是一个叫 fname 的 PDF 文件，缺省上下留白有点多，修改为上1'，下0.8'，由于 100 道题撑不满整整一页，所以不对称的页眉页脚高度显示出来上下的留白几乎一样
                                                                                                                         
elements = []
n = 10
for i in range(n):
    items = genList(100 * 2)  #随机生成 100 道题目（其实是 200 道题，无答案 100 道，带答案 100 道）
    elements.append(genTable(items))
    elements.append(platypus.flowables.PageBreak())
    elements.append(genTable_with_answer(items))
    elements.append(platypus.flowables.PageBreak())
    # 生成 2n 页的数据，每个表格后面跟着一个换页
                                                                                                                                                       
doc.build(elements)
