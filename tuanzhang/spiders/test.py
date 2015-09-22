# -*- coding: utf-8 -*-
import scrapy
from tuanzhang.items import FilesItem
import json


class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["monolithicpower.com"]
    start_urls = (
        'http://www.monolithicpower.com/',
    )

    def parse(self, response):
        #url = 'http://www.monolithicpower.com/DesktopModules/DocumentManage/API/Document/GetDocument?id=3320'
        fp = open('retry.json', 'r+')
        info = json.load(fp)
        fp.close()

        print info
        item = FilesItem()
        item['filename'] = info['filename']
        item['file_urls'] = info['file_urls']
        return item

