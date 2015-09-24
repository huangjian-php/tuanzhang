# -*- coding: utf-8 -*-
import scrapy
from tuanzhang.items import FilesItem
import json, re
import time
import libxml2


class SheetMpsSpider(scrapy.Spider):
    name = "sheet_mps"
    allowed_domains = ["monolithicpower.com"]
    start_urls = (
        'http://www.monolithicpower.com/',
    )

    def __init__(self):
        self.cnt = 0
        self.relation = open('relation.csv', 'w+')
        self.relation.write("型号, 地址, 系列, 原厂\n")
        self.field_enum = {}
        doc = libxml2.parseFile('enum.xml')
        for val in doc.xpathEval('//Field'):
            shortname = val.xpathEval('@shortName')[0].content
            self.field_enum[shortname] = {}
            for item in val.xpathEval('Enum/Item'):
                label = item.xpathEval('Label/text()')[0].content
                value = item.xpathEval('Value/text()')[0].content
                self.field_enum[shortname][value] = label
        print self.field_enum
        doc.freeDoc()


    def parse(self, response):
        fp = open('category.json', 'r+')
        category = json.load(fp)
        fp.close()
        index_category = {}
        for val in category['Data']:
            index_category[val['CategoryID']] = val

        url_third = 'http://www.monolithicpower.com/Desktopmodules/Product/Ajax.ashx?method=getColumns&categoryID=%s'
        for val in category['Data']:
            _url_third = url_third % val['CategoryID']
            name = val['Name']
            tmp = val
            while 0 != tmp['ParentID']:
                tmp = index_category[tmp['ParentID']]
                name = tmp['Name'] + '-' + name

            yield scrapy.Request(_url_third, callback=self.third_parse, cookies={
                '.ASPXANONYMOUS' : '9bMi0aYq0QEkAAAAZDBjMzQ2Y2YtN2EwYS00ZGVjLWFmZmQtNTlkM2IzNmNlNDRm0',
                'ASP.NET_SessionId' : 'e0e5rqj0pz3tj4b203messi0',
                'authentication' : 'DNN',
                'dnn_IsMobile' : 'False',
                '.DOTNETNUKE' : '733F94091403C78179B5B8BDEF80AC5992DB09D95CC4644C4BC7091AD7FCC63498EF540A80A226E738293D59070ECA903F81DAB38FEF317E8122F2106D20EAACF3BD287CC585CBA78DE20829F4E32520A2E8ACCE356C3C81B34E0FB6900368E6EFE532AEA10AF90F5B3290FED5E873432FC4E8C432CD2862CD8C024B1048F6128FFADB6C',
                '_ga' : 'GA1.2.1508715189.1442802415',
                '_gat' : '1',
                'language' : 'en-US'
                }, meta={'name' : name, 'CategoryID' : val['CategoryID']})
        

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
                self.relation.write(','.join([val['partnumber'], base_url + val['partnumber'] + '.pdf', response.meta['name'], url]) + "\n")

                #sheet
                lst_csv = ['"%s"'] * len(response.meta['field']);
                lst = []
                for field in response.meta['field']:
                    if self.field_enum.has_key(field) and self.field_enum[field].has_key(val[field]):
                        lst.append(self.field_enum[field][val[field]])
                    else:
                        lst.append(val[field] if val[field] else '')
                    #print response.meta['field']
                    #print response.meta['field_name']
                    #print val

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
            match =re.sub(r'function\(value,item\)\s*\{.+?\}','1',match[0])
            data = eval(match.replace('null', 'None'))
            if data:
                field = []
                field_name = []
                for val in data:
                    if 1 == val['columnvisible']:
                        field.append(val['shortname'].decode('utf8'))
                        field_name.append(val['name'])
                url = 'http://www.monolithicpower.com/Desktopmodules/Product/Ajax.ashx?method=getProducts&categoryID=%s&_=%d'
                _url = url % (response.meta['CategoryID'], (time.time() * 1000))
                yield scrapy.Request(_url, callback=self.secondary_parse, cookies={
                    '.ASPXANONYMOUS' : '9bMi0aYq0QEkAAAAZDBjMzQ2Y2YtN2EwYS00ZGVjLWFmZmQtNTlkM2IzNmNlNDRm0',
                    'ASP.NET_SessionId' : 'e0e5rqj0pz3tj4b203messi0',
                    'authentication' : 'DNN',
                    'dnn_IsMobile' : 'False',
                    '.DOTNETNUKE' : '733F94091403C78179B5B8BDEF80AC5992DB09D95CC4644C4BC7091AD7FCC63498EF540A80A226E738293D59070ECA903F81DAB38FEF317E8122F2106D20EAACF3BD287CC585CBA78DE20829F4E32520A2E8ACCE356C3C81B34E0FB6900368E6EFE532AEA10AF90F5B3290FED5E873432FC4E8C432CD2862CD8C024B1048F6128FFADB6C',
                    '_ga' : 'GA1.2.1508715189.1442802415',
                    '_gat' : '1',
                    'language' : 'en-US'
                    }, meta={'name' : response.meta['name'], 'field' : field, 'field_name' : field_name})
        else:
            print "Not match!"

        

    def closed(spider, reason):
        spider.relation.close()
