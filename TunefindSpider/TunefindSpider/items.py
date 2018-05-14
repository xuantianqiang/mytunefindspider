# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime


from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst,MapCompose


class TunefindspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass



class MyItemLoader(ItemLoader):
    #自定义Season的ItemLoader
    default_output_processor = TakeFirst()


import re
def get_nums(value):
    #找出数字返回，默认为0
    nums_match = re.match('.*(\d+)',value)
    if nums_match:
        nums = int(nums_match.group(0))
    else:
        nums = 0
    return nums

class SongSeasonItem(scrapy.Item):
    #剧的季信息
    season_id = scrapy.Field()  #id
    season_name = scrapy.Field() #第几季
    show_name = scrapy.Field()  #哪部剧
    episode_counts = scrapy.Field(
        input_processor = MapCompose(get_nums)#这一季有几集,要对解析到的字符串处理下
    )
    song_counts = scrapy.Field(
        input_processor = MapCompose(get_nums)#这一季歌曲数
    )

    def get_insert_sql(self):
        #入库操作
        insert_sql = '''
              insert into season(s_name, show_name, episode_counts, song_counts)
              values(%s, %s, %s, %s)
        '''
        params = (self["season_name"], self["show_name"],
                  self["episode_counts"], self["song_counts"])

        return insert_sql, params

class SongEpisodeItem(scrapy.Item):

    def get_episode_name(value):
        #处理各集的名称
        name = value.split('·')[-1][1:]
        return name

    def get_pub_time(value):
        date_match = re.match('.*(\d{4}-\d{2}-\d{2})',value)
        if date_match:
            date_time = date_match.group(0)
        else:
            date_time = ''
        try:
            date_time = datetime.datetime.strptime(date_time,'%Y-%m-%d').date()
        except Exception as e:
            date_time =datetime.datetime.strptime('1997-01-01','%Y-%m-%d').date()
        return date_time

    #各集信息
    episode_id = scrapy.Field()
    episode_name = scrapy.Field(
        input_processor = MapCompose(get_episode_name)
    )
    season_id = scrapy.Field()
    song_counts = scrapy.Field(
        #数字，正则匹配就行
        input_processor = MapCompose(get_nums)
    )
    pub_time = scrapy.Field(
        input_processor = MapCompose(get_pub_time)
    )
    def get_insert_sql(self):
        insert_sql = '''
            insert into episode(e_name, s_counts, pub_time)
            values(%s, %s, %s)
        '''
        params = (self["episode_name"],self["song_counts"],self["pub_time"])
        return insert_sql, params


class SongItem(scrapy.Item):
    #各歌曲的信息

    def get_song_desc(value):
        if value == 'Add scene description':
            return 'NULL'
        else:
            return value


    song_name = scrapy.Field()
    artists_name = scrapy.Field()
    song_desc = scrapy.Field(
        input_processort = MapCompose(get_song_desc)
    )
    episode_id = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = '''
            insert into song(s_name, artists_name, s_desc)
            values(%s, %s, %s)
        '''
        params = (self["song_name"],self["artists_name"],self['song_desc'])

        return insert_sql, params


