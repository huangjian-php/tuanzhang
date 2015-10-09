# -*- coding: utf-8 -*-
import scrapy
import codecs, re


class IssiSpider(scrapy.Spider):
    name = "issi"
    allowed_domains = ["issi.com"]
    start_urls = (
        'http://www.issi.com/US/Index.shtml',
    )

    def parse(self, response):
        path = './ul[%s]/li/a'
        for li in response.xpath('//div[@class="products-nav"]/ul/li'):
            h2 = li.xpath('./h2/text()').extract()
            num = len(h2)
            for x in xrange(1, num + 1):
                name = h2[x - 1]
                for a in li.xpath(path % x):
                    c_name = name + '-' + a.xpath('./text()').extract()[0]
                    url = a.xpath('./@href').extract()[0]
                    yield scrapy.Request(response.urljoin(url), callback=self.secondary_parse, meta={'name' : c_name})
                    #break
                #break
            #break

    def secondary_parse(self, response):
        for article in response.xpath('//div[@id="jumpTable"]/article'):
            if article.xpath('./@class').extract:
                continue

            name = response.meta['name'] + '-' + article.xpath('./h2/a/text()').extract()[0]
            
            title = article.xpath('./table//tr[@class="header-table"]/th/text()').extract()
            k = 0
            for field in title:
                if 'Part Number' == field or 'App Note' == field:
                    break
                else:
                    k += 1
            del title[k]
            title = ['brand', 'Series', 'PartNo', 'dataSheet'] + title
            csv_str = ','.join(['"%s"'] * len(title)) % tuple(title) + "\n"

            
            for tr in article.xpath('./table//tr'):
                data = []
                for td in tr.xpath('./td'):
                    if not td.extract():
                        break
                    else:
                        text = td.xpath('./text()').extract()
                        if text:
                            data.append(text[0])
                        else:
                            data.append('-')

                if data:
                    del data[k]
                    type_num = tr.xpath('./td[@class="partNumber"]/a/text()').extract()
                    if type_num:
                        type_num = type_num[0]
                    else:
                        type_num = tr.xpath('./td[@class="partNumber"]/text()').extract()[0]
                    dataSheet = tr.xpath('./td[@class="partNumber"]/a/@href').extract()
                    if dataSheet:
                        dataSheet = response.urljoin(dataSheet[0])
                    else:
                        dataSheet = '-'
                    data = ['issi', name, type_num, dataSheet] + data
                    tpl = ['"%s"'] * len(data)
                    csv_str += ','.join(tpl) % tuple(data) + "\n"

            fp = codecs.open('issi/main/' + re.sub(r'[/:|?*"\\<>]', '&', name) + '.csv', 'w+', 'utf_8_sig')
            fp.write(csv_str)
            fp.close()


