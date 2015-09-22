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
                'ASP.NET_SessionId' : 'anjij3yloyjcipaxsyj5z4w3',
                'authentication' : 'DNN',
                'dnn_IsMobile' : 'False',
                '.DOTNETNUKE' : '033E9855CAABF5F46B44A69607A1F140610106B7B931C77DCC24C75B3D621357F651778680410226BDCA223D20DF23532F461FED77F07E18A7345C7966EC8034C5FB5EE996006831320DA71FB9DFDDFC6907B47DD82116C7B08CF40E0994BBDFF5EC7B406D4D34E3F9E6DC5D6A899E2B84CEAEA4A2F01D17F480E7E3FCFFF9E48AAA0DD8',
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
