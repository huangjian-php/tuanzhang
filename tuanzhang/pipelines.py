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

    def get_media_requests(self, item, info):
        for file_url in item['file_urls']:
            yield scrapy.Request(file_url, cookies={
                '.ASPXANONYMOUS' : 'HkZetkYp0QEkAAAANDc0ZDRlNDYtODIyYy00Mjg2LWE2MzYtYWU4ZGZiNmEzMmE40',
                'ASP.NET_SessionId' : 'anjij3yloyjcipaxsyj5z4w3',
                'authentication' : 'DNN',
                'dnn_IsMobile' : 'False',
                '.DOTNETNUKE' : '46C2302193779383F45DE7C199AD0F0589E557FE8013A744A8DD7AA1445FC7F953D509DD3FB59FA0F6AB48ADFA44895EBF9ACC0802E763AA42AC1F8C20397B3CC4E9FA994BA4BF5C3AF436CD7B5E2DEFB0BC4BA47360477CBD369C634BDA92E9959EBF26EFB834AC751F849CEF297B2C9B14568010BA924D28F45D48AAE025D25392C4C8',
                '_ga' : 'GA1.2.1645343463.1442651428',
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
            print response.url
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