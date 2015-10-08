# -*- coding: utf-8 -*-
import scrapy
import re, csv, codecs


class OnSpider(scrapy.Spider):
    name = "on"
    allowed_domains = ["onsemi.cn"]
    start_urls = (
        'http://www.onsemi.cn/PowerSolutions/products.do',
    )

    def parse(self, response):
        urls = response.xpath('//table[@id="productMapHome"]').xpath('.//a[contains(@href, "/PowerSolutions/taxonomy.do?id=")]/@href').extract()
        
        for url in urls:
            yield scrapy.Request(response.urljoin(url), callback=self.secondary_parse)
            #break

    def secondary_parse(self, response):
        name = response.xpath('//h1[@class="taxonomyTitle"]/text()').extract()[0].strip()
        name = re.sub(r'\s*\[.+\]\s*', '', name)
        a_tag = response.xpath('//a[@style="color:#fff;font-size:14px;"]')
        for val in a_tag:
            url = val.xpath('./@href').extract()[0]
            c_name = val.xpath('./text()').extract()
            if len(c_name) > 1:
                c_name = name + '-' + val.xpath('./sub/text()').extract()[0].join(c_name).strip()
            else:
                c_name = name + '-' + c_name[0].strip()
            #print url
            #print c_name
            param = '&action=excelCsv&actionData=undefined&sortOrder=asc&sortProperty=&currPage=1&pageSize=0'
            #param = '&action=setPageSize&actionData=0&sortOrder=asc&sortProperty=&currPage=1&pageSize=0'
            yield scrapy.Request(response.urljoin(url) + param, method='POST', callback=self.tertius_parse, meta={'name' : c_name})
            #break

    def tertius_parse(self, response):
        
        sheet_url = 'http://www.onsemi.cn/PowerSolutions/supportDoc.do?type=%s&part=%s'
        detail_url = 'http://www.onsemi.cn/PowerSolutions/product.do?id=%s'
        csv_lst = response.body.strip('"\n').split('"\n"')
        title = '"' + csv_lst[0] + '"'
        title = title.split(',')
        title[0:1] = ['"brand"', '"Series"', '"PartNo"', '"DetailLink"']
        del csv_lst[0]

        csv_str = ','.join(title) + "\n"

        for val in csv_lst:
            val = '"' + val + '"'
            val_lst = val.split(',')
            id = val_lst[0]
            val_lst[0:1] = ['"on"', '"' + response.meta['name'] + '"', id, '"' + detail_url % id.strip('"') + '"']
            csv_str += ','.join(val_lst) + "\n"
        fp = codecs.open('on/main/' + re.sub(r'[/:|?*"\\<>]', '&', response.meta['name']) + '.csv', 'w+', 'utf_8_sig')
        fp.write(csv_str)
        fp.close()

        
        sheet = {
            '应用注释' : 'AppNotes',
            '辅助小册子' : 'Brochures',
            '遵从性报告' : 'Conformance Report',
            '数据表' : 'Datasheets',
            '设计注释' : 'Design Notes',
            '设计和开发工具' : 'tools',
            'Errata' : 'Errata/Addendum',
            '评估板文档' : 'boards',
            '评估/开发工具' : '',
            '封装图纸' : 'drawing',
            '参考设计' : 'Reference Designs', 
            '参考手册' : 'manuals',
            '仿真模型' : 'models',
            '培训教材' : 'Tutorials',
            '视频' : 'Video',
            '软件' : 'software',
            '白皮书' : 'White Papers'
        }

