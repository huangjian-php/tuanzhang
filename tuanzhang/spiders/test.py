# -*- coding: utf-8 -*-
import scrapy
import re
import libxml2


class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["monolithicpower.com"]
    start_urls = (
        'http://www.monolithicpower.com/Desktopmodules/Product/Ajax.ashx?method=getColumns&categoryID=69',
    )

    def __init__(self):
        self.field_enum = {}
        doc = libxml2.parseFile('enum.xml')
        for val in doc.xpathEval('//Field'):
            shortname = val.xpathEval('@shortName')[0].content
            self.field_enum[shortname] = {}
            for item in val.xpathEval('Enum/Item'):
                label = item.xpathEval('Label/text()')[0].content
                value = item.xpathEval('Value/text()')[0].content
                self.field_enum[shortname][value] = label
        doc.freeDoc()

    def parse(self, response):
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
                    #if 1 == val['displayable'] or 1 == val['columnvisible'] or 1 == val['displayableindetail']:
                        field.append(val['shortname'].decode('utf8'))
                        field_name.append('"' + val['name'] + '"')
                print field
                print field_name
                for name in field_name:
                    print name
                print len(field)
                #print data
                print len(data)
                print data[0]
                #url = 'http://www.monolithicpower.com/Desktopmodules/Product/Ajax.ashx?method=getProducts&categoryID=%s&_=%d'
                #_url = url % (response.meta['CategoryID'], (time.time() * 1000))
        else:
            print "Not match!"
