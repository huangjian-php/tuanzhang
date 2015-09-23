# -*- coding: utf-8 -*-
import scrapy
from tuanzhang.items import FilesItem
import json


class TestSpider(scrapy.Spider):
    name = "retry"
    allowed_domains = ["monolithicpower.com"]
    start_urls = (
        'http://www.monolithicpower.com/',
    )

    def parse(self, response):
        fp = open('retry.json', 'r+')
        info = json.load(fp)
        fp.close()

        #print info
        item = FilesItem()
        item['filename'] = info['filename']
        item['file_urls'] = info['file_urls']
        return item

    

