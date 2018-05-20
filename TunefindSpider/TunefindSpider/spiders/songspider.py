# -*- coding: utf-8 -*-

import scrapy

from urllib import parse
from scrapy import Request
from scrapy.loader import ItemLoader

from TunefindSpider.items import MyItemLoader
from TunefindSpider.items import SongSeasonItem
from TunefindSpider.items import SongEpisodeItem
from TunefindSpider.items import SongItem
from TunefindSpider.items import TuneItem
# import re
# import datetime
#
# from scrapy.loader import ItemLoader
# from urllib import parse

class SongSpider(scrapy.Spider):


    name = "songspider"
    allowed_domains = ["www.tunefind.com"]
    start_urls = ['https://www.tunefind.com/show/sherlock-uk/',
                  'https://www.tunefind.com/show/game-of-thrones/']


    def parse(self, response):
        '''
            取到每一季的url，并解析
                :param response:
                :return:
        '''
        # yield Request(url=response.url, callback=self.parse_all)

        season_urls = response.css('.EpisodeListItem__title___32XUR a::attr(href)').extract()

        for season_url in season_urls:
            yield Request(url=parse.urljoin(response.url, season_url),
                          callback=self.parse_seasons)


    def parse_seasons(self, response):
        '''
        解析各季页面，得到各集的列表
        :param response:
        :return:
        '''
        episode_urls = response.css('.EpisodeListItem__title___32XUR a::attr(href)').extract()
        for episode_url in episode_urls:
            yield Request(url=parse.urljoin(response.url, episode_url),
                          callback=self.parse_episodes)

    def parse_episodes(self, response):
        '''
            解析各集页面，取到各字段，生成Item
        :param response:
        :return:
        '''
        '''解析标题'''
        # 'S1 · E1 · Wolferton Splash'
        episode_title = response.xpath("//h2[@class='EpisodePage__title___MiEq3']").xpath('string(.)').extract_first()
        episode_title = episode_title.split(' · ') #['S1 ', ' E1 ', ' Wolferton Splash']

        seasonId = episode_title[0]  #第几季
        episodeId = episode_title[1]    #第几集
        episodeName = episode_title[2]  #集名

        show_Name = response.css(".TvHeader__title___33Oa3 a::text").extract_first()



        '''解析歌曲列表'''
        songNames =  response.css(".SongRow__container___3eT_L .SongTitle__heading___3kxXK a::text").extract()
        artistsNames = response.css(".SongRow__container___3eT_L .SongEventRow__subtitle___3Qli4 a::text").extract()
        songDescs = (response.xpath("//div[@class='SceneDescription__description___3Auqj']")).xpath(
                             'string(.)').extract()


        '''生成Item'''
        for index in range(0, len(songNames)):

            item_loader = MyItemLoader(item=TuneItem(), response=response)

            item_loader.add_value("songName", songNames[index])
            item_loader.add_value("seasonId",seasonId)
            item_loader.add_value("episodeId", episodeId)
            item_loader.add_value("episodeName", episodeName)
            item_loader.add_value("showName", show_Name)
            item_loader.add_value("artistsName", artistsNames[index])
            item_loader.add_value("songDesc", songDescs[index])

            tune_item = item_loader.load_item()

            yield tune_item



    def parse_season(self,response):
        '''
            解析剧的首页，得到所有季的信息，生成Item
        '''
        #解析各字段
        season_name_list = response.css(".MainList__item___2MKl8 h3 a::text").extract()
        episode_counts_list = response.css(".EpisodeListItem__links___xftsa li:nth-child(1) h5 a::text").extract()
        song_counts_list = response.css(".EpisodeListItem__links___xftsa li:nth-child(2) h5 a::text").extract()
        show_name = response.url.split('/')[-1]

        for index in range(0,len(season_name_list)):
            # 创建Item_loader
            item_loader = MyItemLoader(item=SongSeasonItem(), response=response)

            item_loader.add_value('season_name',season_name_list[index])
            item_loader.add_value('show_name', show_name)
            item_loader.add_value('episode_counts',episode_counts_list[index])
            item_loader.add_value('song_counts',song_counts_list[index])

            season_item = item_loader.load_item()
            yield season_item


        # 取到各季的url，访问
        season_url_nodes = response.css('.MainList__item___2MKl8 h3 a')
        # 依次处理每季
        for season_url_node in season_url_nodes:
            # 构造request,并请求解析当前seson
            season_url = season_url_node.css('::attr(href)').extract_first()
            # 处理每季的页面
            yield Request(url=parse.urljoin(response.url, season_url),
                          callback=self.parse_episode)


    def parse_episode(self,response):
        '''
            处理各季的页面，生成EpisodeItem
        '''

        episode_name_list = response.css(".MainList__item___2MKl8 h3 a::text").extract()
        song_counts_list = response.css(".EpisodeListItem__links___xftsa li:nth-child(1) h5 a::text").extract()
        pub_time_list = response.css(".EpisodeListItem__subtitle___3APYi time::attr(datetime)").extract()
        season_name = 'Season '+(response.url.split('/')[-1]).split('-')[-1]

        for index in range(0,len(episode_name_list)):
            item_loader = MyItemLoader(item=SongEpisodeItem(),response=response)

            item_loader.add_value("episode_name", episode_name_list[index])
            item_loader.add_value('song_counts', song_counts_list[index])
            item_loader.add_value('season_id', season_name) #item中根据season_name查表来获取外键的Id
            item_loader.add_value('pub_time', pub_time_list[index])

            episode_item = item_loader.load_item()
            yield episode_item


        #访问各集的页面，解析各歌曲的信息
        episode_url_nodes = response.css('.MainList__item___2MKl8 h3 a::attr(href)').extract()
        for episode_url_node in episode_url_nodes:
            yield Request(url=parse.urljoin(response.url,episode_url_node),
                          callback=self.parse_songs)

    def parse_songs(self,response):
        '''
            解析各集的信息，生成Item
        '''

        song_name_list = response.css(".SongRow__container___3eT_L h4 a::text").extract()
        artists_name_list = response.css(".SongRow__container___3eT_L .SongEventRow__subtitle___3Qli4 a::text").extract()
        # song_desc_list = response.css(".SceneDescription__description___3Auqj div").extract()
        song_desc_list = (response.xpath("//div[@class='SceneDescription__description___3Auqj']")).xpath('string(.)').extract()
        episode_name = response.css(".EpisodePage__title___MiEq3 a::text").extract()[1]  #E1

        for index in range(0, len(song_name_list)):

            item_loader = MyItemLoader(item=SongItem(), response=response)

            item_loader.add_value("song_name",song_name_list[index])
            item_loader.add_value("artists_name",artists_name_list[index])
            item_loader.add_value("song_desc",song_desc_list[index])
            item_loader.add_value("episode_id",episode_name)

            song_item = item_loader.load_item()

            yield song_item
