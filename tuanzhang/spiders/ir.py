# -*- coding: utf-8 -*-
import scrapy


class IrSpider(scrapy.Spider):
    name = "ir"
    allowed_domains = ["irf.com"]
    start_urls = (
        'http://www.irf.com/product/',
    )

    def parse(self, response):
        for ul in response.xpath('//ul[@class=" level-3"]'):
            i = 0
            ele = ul.xpath('./*')
            max = len(ele)
            
            print ele[i].xpath('./@class').extract()[0]
            for val in ele:
                i += 1
                if i == max or ' level-4' == val.xpath('./@class').extract()[0]:
                    pass
                else:
                    cls = ele[i].xpath('./@class').extract()
                    if cls and ' level-4' == cls[0]:
                        continue
                url = val.xpath('./a/@href').extract()
                if not url:
                    for li in val.xpath('./li'):
                        url = li.xpath('./a/@href').extract()
                        yield scrapy.Request(response.urljoin(url[0]), callback=self.secondary_parse)
                else:
                    yield scrapy.Request(response.urljoin(url[0]), callback=self.secondary_parse)
                break
            break

    def secondary_parse(self, response):
        print response.url
        for div in response.xpath('//div[@id="nav-sec-options"]/div[contains(@class, "option")]'):
            url = div.xpath('./a/@href').extract()[0]
            print url
            print '-----'
            #yield scrapy.Request(response.urljoin(url), callback=self.secondary_parse)
        div = response.xpath('//div[@class="ag-tabs"]/div/div[@id="table1"]')
        if div:
            name = response.xpath('//div[@id="breadcrumb"]/div[@class="option"]/*/text()').extract()
            name = '-'.join(name[1:-1])
            title = div.xpath('.//li[@data-column-name]/@data-column-name').extract()
            print title
            print len(title)
        

    def tertius_parse(self, response):
        pass