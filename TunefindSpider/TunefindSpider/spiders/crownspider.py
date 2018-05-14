# -*- coding: utf-8 -*-

import scrapy
import re
import datetime

from scrapy import Request
from scrapy.loader import ItemLoader
from urllib import parse
# from ArticleSpider.items import ArticleItemLoader
# from ArticleSpider.items import JobboleArticleItem
# from ArticleSpider.items import JobboleArticleItem2
# from ArticleSpider.utils.commons import get_md5

# filename = 'The Crown S2.txt'
filename = 'Billions S3.txt'

class CrownSpider(scrapy.Spider):


    name = "crownspider"
    allowed_domains = ["www.tunefind.com"]
    start_urls = ['https://www.tunefind.com/show/billions/']
    start_urls = ['https://www.tunefind.com/show/billions/season-3/']

    def parse(self, response):
        '''
            取到每一季的url，并解析
                :param response:
                :return:
        '''

        with open(filename, 'a+') as file:
            file.write('\n--------------')
            file.close()
        #所有集的列表
        episode_urls = response.css('.MainList__item___2MKl8 h3 a::attr(href)').extract()

        for episode_url in episode_urls:
            yield Request(url=parse.urljoin(response.url, episode_url),
                          callback = self.parse_episode)


    def parse_episode(self, response):
        '''
            解析各集
        '''
        with open(filename,'a+') as file:
            file.write('\n')
            file.close()


        #所有歌名和作者
        song_names = response.css('.SongRow__container___3eT_L h4 a::text').extract()
        song_artists = response.css('.SongEventRow__subtitle___3Qli4 a::text').extract()

        with open(filename, 'a+') as file:

            for song_name, song_artist in zip(song_names, song_artists):
                # file.write('\n'+song_name+'  ==  '+song_artist)
                file.write('\n' + song_name)
                file.write('\n---' + song_artist)
                # print(song_name)
                # print(song_artist)
            file.close()
        pass

