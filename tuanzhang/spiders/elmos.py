# -*- coding: utf-8 -*-
import scrapy
import re, codecs


class ElmosSpider(scrapy.Spider):
    name = "elmos"
    allowed_domains = ["elmos.com"]
    start_urls = (
        'http://www.elmos.com/english/index1.html',
    )

    def __init__(self):
        self.sheet = codecs.open(u'elmos/手册/sheet.csv', 'w+', 'utf_8_sig')
        title = ['brand', 'Series', 'PartNo', 'Type', 'Url']
        self.sheet.write(','.join(['"%s"'] * len(title)) % tuple(title) + "\n")

    def parse(self, response):
        for div in response.xpath('//div[@id="c7969"]/div'):
            name = div.xpath('.//h4/a/text()').extract()[0].strip()
            for a in div.xpath('.//p[@class="bodytext"]/a'):
                c_name = name + '-' + a.xpath('./text()').extract()[0].strip()
                url = a.xpath('./@href').extract()[0]
                yield scrapy.Request(response.urljoin(url), callback=self.secondary_parse, meta = {'name' : c_name})
                #break
            #break

    def secondary_parse(self, response):
        section = response.xpath('//section[@id="no-more-tables"]')
        if section.extract():
            title = []
            for th in section.xpath('.//th'):
                text = th.xpath('./text()').extract() + th.xpath('./sub/text()').extract()
                if text:
                    title.append(' '.join(text))
                else:
                    title.append('-')
            title[0:1] = ['brand', 'Series', 'PartNo', 'DetailLink', 'Description']
            fp = codecs.open('elmos/main/' + re.sub(r'[/:|?*"\\<>]', '&', response.meta['name']) + '.csv', 'w+', 'utf_8_sig')
            csv_str = ','.join(['"%s"'] * len(title)) % tuple(title) + "\n"

            for tr in section.xpath('.//tr[position() > 1]'):
                part_num = tr.xpath('./td[1]/a/text()').extract()[0]
                part_num = re.sub(r'\(.+?\)', '', part_num)
                detail_url = tr.xpath('./td[1]/a/@href').extract()[0]
                desc = tr.xpath('./td[1]/text()').extract()[0]
                data = []
                for td in tr.xpath('./td[position() > 1]'):
                    text = td.xpath('./text()').extract() + td.xpath('./sub/text()').extract() + ["\n".join(td.xpath('./p/text()').extract())] + ["\n".join(td.xpath('.//li/text()').extract())]
                    if text:
                        data.append(' '.join(text))
                    else:
                        data.append('-')
                for val in part_num.split(','):
                    data = ['elmos', response.meta['name'], val.strip(), response.urljoin(detail_url), desc] + data
                    csv_str += ','.join(['"%s"'] * len(data)) % tuple(data) + "\n"
                    yield scrapy.Request(response.urljoin(detail_url), callback=self.tertius_parse, meta = {'name' : response.meta['name'], 'part_num' : val})
            fp.write(csv_str)
            fp.close()

    def tertius_parse(self, response):
        sheet_str = ''
        for li in response.xpath('//div[@id="no-more-tables"]/div/div[last()-1]/ul/li'):
            type = li.xpath('./text()').extract()[0].strip(' |\n')
            url = li.xpath('./a/@href').extract()[0]
            sheet_data = ['exar', response.meta['name'], response.meta['part_num'], type, response.urljoin(url)]
            tpl = ['"%s"'] * len(sheet_data)
            sheet_str += ((','.join(tpl) % tuple(sheet_data)) + "\n")
        self.sheet.write(sheet_str)

    def closed(spider, reason):
        spider.sheet.close()
