# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import MySQLdb
import MySQLdb.cursors
import pymysql

from twisted.enterprise import adbapi


class TunefindspiderPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlTwistedPipeline(object):
    #twist异步连接，进行mysql数据库操作
    def __init__(self,dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):
        dbparams = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset = "utf8",
            cursorclass =MySQLdb.cursors.DictCursor,
            use_unicode = True,
        )

        #创建连接池
        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparams)

        return cls(dbpool)


    def process_item(self, item, spider):
        #数据库操作
        # if item.QUREY:
        #     query = self.dbpool.runInteraction(self.do_query,item)

        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        #处理异常
        print(failure)


    def do_insert(self, cursor, item):
        #入库
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)






