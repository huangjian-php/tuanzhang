# -*- coding: utf-8 -*-
import scrapy
from tuanzhang.items import FilesItem
import json
import time


class SheetMpsSpider(scrapy.Spider):
    name = "sheet_mps"
    allowed_domains = ["monolithicpower.com"]
    start_urls = (
        'http://www.monolithicpower.com/',
    )

    def __init__(self):
        self.cnt = 0

    def parse(self, response):
        fp = open('category.json', 'r+')
        category = json.load(fp)
        fp.close()
        url = 'http://www.monolithicpower.com/Desktopmodules/Product/Ajax.ashx?method=getProducts&categoryID=%s&_=%d'
        for val in category['Data']:
            _url = url % (val['CategoryID'], (time.time() * 1000))
            yield scrapy.Request(_url, callback=self.secondary_parse, cookies={
                '.ASPXANONYMOUS' : '9bMi0aYq0QEkAAAAZDBjMzQ2Y2YtN2EwYS00ZGVjLWFmZmQtNTlkM2IzNmNlNDRm0',
                'ASP.NET_SessionId' : 'anjij3yloyjcipaxsyj5z4w3',
                'authentication' : 'DNN',
                'dnn_IsMobile' : 'False',
                '.DOTNETNUKE' : '033E9855CAABF5F46B44A69607A1F140610106B7B931C77DCC24C75B3D621357F651778680410226BDCA223D20DF23532F461FED77F07E18A7345C7966EC8034C5FB5EE996006831320DA71FB9DFDDFC6907B47DD82116C7B08CF40E0994BBDFF5EC7B406D4D34E3F9E6DC5D6A899E2B84CEAEA4A2F01D17F480E7E3FCFFF9E48AAA0DD8',
                '_ga' : 'GA1.2.1508715189.1442802415',
                '_gat' : '1',
                'language' : 'en-US'
                })
        

    def secondary_parse(self, response):
        product = json.loads(response.body)
        if len(product['Data']) > 0:
            #print len(product['Data'])
            item = FilesItem()
            item['filename'] = {}
            item['file_urls'] = []
            for val in product['Data']:
                url = response.urljoin(val['datasheet_url'])
                item['filename'][url] = val['partnumber']
                item['file_urls'].append(url)
                self.cnt += 1
                print self.cnt
            return item
