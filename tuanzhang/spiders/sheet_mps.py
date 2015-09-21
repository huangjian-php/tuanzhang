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

    def parse(self, response):
        #url = 'http://www.monolithicpower.com/DesktopModules/ProductManage/API/Product/GetCategoryTree?orderBy='
        #url = 'http://www.htckorea.co.kr/Datasheet/Voltage Stabilizer/TL432-R1.5.pdf'
        fp = open('category.json', 'r+')
        category = json.load(fp)
        fp.close()
        url = 'http://www.monolithicpower.com/Desktopmodules/Product/Ajax.ashx?method=getProducts&categoryID=%s&_=%d'
        for val in category['Data']:
            _url = url % (val['CategoryID'], (time.time() * 1000))
            yield scrapy.Request(_url, callback=self.secondary_parse, cookies={
                '.ASPXANONYMOUS' : 'HkZetkYp0QEkAAAANDc0ZDRlNDYtODIyYy00Mjg2LWE2MzYtYWU4ZGZiNmEzMmE40',
                'ASP.NET_SessionId' : 'anjij3yloyjcipaxsyj5z4w3',
                'authentication' : 'DNN',
                'dnn_IsMobile' : 'False',
                '.DOTNETNUKE' : '46C2302193779383F45DE7C199AD0F0589E557FE8013A744A8DD7AA1445FC7F953D509DD3FB59FA0F6AB48ADFA44895EBF9ACC0802E763AA42AC1F8C20397B3CC4E9FA994BA4BF5C3AF436CD7B5E2DEFB0BC4BA47360477CBD369C634BDA92E9959EBF26EFB834AC751F849CEF297B2C9B14568010BA924D28F45D48AAE025D25392C4C8',
                '_ga' : 'GA1.2.1645343463.1442651428',
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
            return item
