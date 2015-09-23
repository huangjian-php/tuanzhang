# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json, os
import scrapy
from scrapy.pipelines import files
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO
from scrapy.utils.misc import md5sum
from tuanzhang.items import FilesItem

class TuanzhangPipeline(object):

    def open_spider(self, spider):
        self.json = []

    def process_item(self, item, spider):
        self.json.append(dict(item))

    def close_spider(self, spider):
        print self.json
        fp = open('result.json', 'w+')
        fp.write(json.dumps(self.json))
        fp.close()


class  FilesPipeline(files.FilesPipeline):
    """FilesPipeline"""
    def open_spider(self, spider):
        self.spiderinfo = self.SpiderInfo(spider)
        self.json = {}
        self.json['filename'] = {}
        self.json['file_urls'] = []

    def close_spider(self, spider):
        print self.json
        fp = open('retry.json', 'w+')
        fp.write(json.dumps(self.json))
        fp.close()

    def get_media_requests(self, item, info):
        for file_url in item['file_urls']:
            yield scrapy.Request(file_url, cookies={
                '.ASPXANONYMOUS' : '9bMi0aYq0QEkAAAAZDBjMzQ2Y2YtN2EwYS00ZGVjLWFmZmQtNTlkM2IzNmNlNDRm0',
                'ASP.NET_SessionId' : 'zv4axilksd5yl0k0o32gs54e',
                'authentication' : 'DNN',
                'dnn_IsMobile' : 'False',
                '.DOTNETNUKE' : '419D8B851D2AD8886FC67A4F94DD09869B381CAF128CC7D0F6837783E974FEB4341531AA3B53A1BE4A3313DE0F9BCBBBCC566E646B2A38C2A0A0549388198D1F53DA3D1826003264EE13E35D6B3C6B6C612824157BE0AA0DDBF1A6EF3048D6F7ADB5D1E867EF9A70856D8E21AADB6A9D766D37B59D3456995FE7D37715062E767CE4FE7C',
                '_ga' : 'GA1.2.1508715189.1442802415',
                '_gat' : '1',
                'language' : 'en-US'
                }, meta={'filename' : item['filename'][file_url]})

    def file_downloaded(self, response, request, info):
        path = 'full/' + request.meta['filename'] + '.pdf'
        buf = BytesIO(response.body)
        self.store.persist_file(path, buf, info)
        checksum = md5sum(buf)
        size = os.path.getsize(path)
        if size < 100:
            self.json['filename'][response.url] = request.meta['filename']
            self.json['file_urls'].append(response.url)

        return checksum
        
    def item_completed(self, results, item, info):
        file_paths = {}
        for ok, x in results:
            if ok:
                file_paths[x['url']] = x['path']

        if not file_paths:
            print "Item contains no files"
        item['file_paths'] = file_paths
        return item


class  RenamePipeline(object):
    """Rename"""
    def open_spider(self, spider):
        self.json = []

    def process_item(self, item, spider):
        for file_url in item['file_urls']:
            path = 'full\\' + item['filename'][file_url] + '.pdf'
            if os.path.exists(path):
                path = '(1)' + path
            
            self.json.append((item['file_paths'][file_url], path))
        return item

    def close_spider(self, spider):
        for k, v in self.json:
            os.rename(k, v)
