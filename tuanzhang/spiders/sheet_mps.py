# -*- coding: utf-8 -*-
import scrapy
from tuanzhang.items import FilesItem
import json, re
import time
import types


class SheetMpsSpider(scrapy.Spider):
    name = "sheet_mps"
    allowed_domains = ["monolithicpower.com"]
    start_urls = (
        'http://www.monolithicpower.com/',
    )

    def __init__(self):
        self.cnt = 0
        self.relation = open('relation.csv', 'w+')
        self.relation.write("型号, 地址, 系列\n")

    def parse(self, response):
        fp = open('category.json', 'r+')
        category = json.load(fp)
        fp.close()
        url_third = 'http://www.monolithicpower.com/Desktopmodules/Product/Ajax.ashx?method=getColumns&categoryID=%s'
        for val in category['Data']:
            _url_third = url_third % val['CategoryID']
            yield scrapy.Request(_url_third, callback=self.third_parse, cookies={
                '.ASPXANONYMOUS' : 'HkZetkYp0QEkAAAANDc0ZDRlNDYtODIyYy00Mjg2LWE2MzYtYWU4ZGZiNmEzMmE40',
                'ASP.NET_SessionId' : 'anjij3yloyjcipaxsyj5z4w3',
                'authentication' : 'DNN',
                'dnn_IsMobile' : 'False',
                '.DOTNETNUKE' : '6E03BB48103C884FF2E41F0F229AA3CA241D106A9755288841E8C5FB56F63202FC825E39C887CEDE5AE1A13F0C22CE2F9CD324FE718AEAF2A15C68AA2616C859770DD50E917A6C71E78DBA8E9FE68D814B55E42980351861CB2ECC43AEA67215C676A10441CA5AAEAD29D493ED5C3BA8A3039916D8741310D30C0BCBB829240FC9C5E062',
                '_ga' : 'GA1.2.1645343463.1442651428',
                '_gat' : '1',
                'language' : 'en-US'
                }, meta={'name' : val['Name'], 'CategoryID' : val['CategoryID']})
        

    def secondary_parse(self, response):
        product = json.loads(response.body)
        if len(product['Data']) > 0:
            #print len(product['Data'])
            base_url = 'http://new.zlgmcu.com/mps_datasheet/'
            item = FilesItem()
            item['filename'] = {}
            item['file_urls'] = []
            sheet = open('sheet/' + re.sub(r'[\/\\><]', '_', response.meta['name'].strip()) + '.csv', 'w+')
            sheet.write(','.join(response.meta['field_name']) + "\n")
            for val in product['Data']:
                url = response.urljoin(val['datasheet_url'])
                item['filename'][url] = val['partnumber']
                item['file_urls'].append(url)

                #relation.csv
                self.relation.write(','.join([val['partnumber'], base_url + val['partnumber'] + '.pdf', response.meta['name']]) + "\n")

                #sheet
                lst_csv = ['%s'] * len(response.meta['field']);
                lst = []
                for field in response.meta['field']:
                    lst.append(val[field])
                str_csv = (','.join(lst_csv)) % tuple(lst)
                sheet.write(str_csv.decode('utf8') + "\n")

                self.cnt += 1
                #print self.cnt
                if 0 == self.cnt % 20:
                    self.relation.flush()

            sheet.close()
            #return item

    def third_parse(self, response):
        body = response.body

        pattern = r'^define\(function\s*\(\)\s*\{return\s*\{\s*Data\s*:\s*(.+)\s*,\s*"Status"\s*:\s*0\s*,\s*"Message":null\s*\}\s*\}\s*\);\s*$'
        regular = re.compile(pattern, re.DOTALL)
        match = regular.findall(body)
        if match:
            match =re.sub(r'"formatter":.+?\);\},',' ',match[0])
            data = eval(match.replace('null', 'None'))
            if data:
                field = []
                field_name = []
                for val in data:
                    #if 1 == val['displayable'] or '1' == val['displayable']:
                    field.append(val['shortname'])
                    field_name.append(val['name'])
                url = 'http://www.monolithicpower.com/Desktopmodules/Product/Ajax.ashx?method=getProducts&categoryID=%s&_=%d'
                _url = url % (response.meta['CategoryID'], (time.time() * 1000))
                yield scrapy.Request(_url, callback=self.secondary_parse, cookies={
                    '.ASPXANONYMOUS' : 'HkZetkYp0QEkAAAANDc0ZDRlNDYtODIyYy00Mjg2LWE2MzYtYWU4ZGZiNmEzMmE40',
                    'ASP.NET_SessionId' : 'anjij3yloyjcipaxsyj5z4w3',
                    'authentication' : 'DNN',
                    'dnn_IsMobile' : 'False',
                    '.DOTNETNUKE' : '6E03BB48103C884FF2E41F0F229AA3CA241D106A9755288841E8C5FB56F63202FC825E39C887CEDE5AE1A13F0C22CE2F9CD324FE718AEAF2A15C68AA2616C859770DD50E917A6C71E78DBA8E9FE68D814B55E42980351861CB2ECC43AEA67215C676A10441CA5AAEAD29D493ED5C3BA8A3039916D8741310D30C0BCBB829240FC9C5E062',
                    '_ga' : 'GA1.2.1645343463.1442651428',
                    '_gat' : '1',
                    'language' : 'en-US'
                    }, meta={'name' : response.meta['name'], 'field' : field, 'field_name' : field_name})
        else:
            print "Not match!"

        

    def closed(spider, reason):
        spider.relation.close()
