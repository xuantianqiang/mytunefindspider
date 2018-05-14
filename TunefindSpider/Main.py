# -*- coding: utf-8 -*-

'''
 Main to debug spider

 a spider to get song list in TuneFind website

 __author__ = 'sophon'

'''

from scrapy.cmdline import execute
import os
import sys

#当前main文件的父目录
rootpath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(rootpath)

#执行scrapy命令
# execute(['scrapy','crawl','crownspider'])
execute(['scrapy','crawl','songspider'])