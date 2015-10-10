# -*- coding: utf-8 -*-
import scrapy


class ExarSpider(scrapy.Spider):
    name = "exar"
    allowed_domains = ["exar.com"]
    start_urls = (
        'http://www.exar.com/',
    )

    def parse(self, response):
        crawl_list = {
            'Power Management-Universal PMICs' : 'http://www.exar.com/power-management/universal-pmics/',
            'Power Management-Power Modules' : 'http://www.exar.com/power-management/power-modules/',
            'Power Management-Power Conversion' : 'http://www.exar.com/power-management/power-conversion/',
            'Power Management-System Controls' : 'http://www.exar.com/power-management/system-controls/',
            'Power Management-LED Lighting' : 'http://www.exar.com/power-management/led-lighting/',
        }

        for (name,url) in crawl_list.items():
            yield scrapy.Request(url, callback=self.secondary_parse, meta={'name' : name})
            break

    def secondary_parse(self, response):
        div = response.xpath('//div[@id="ContentPlaceHolder1_upProductFamilies"]')
        header = div.xpath('./div[@class="category-header"]')
        num = len(header)
        div_path = './div[@id="ContentPlaceHolder1_rptProductFamilies_upProducts_%s"]'
        for x in xrange(1, num + 1):
            text = header[x - 1].xpath('./a/text()').extract()
            if text:
                name = response.meta['name'] + '-' + text[0]
            else:
                name = response.meta['name']
            div_table = div.xpath(div_path % (x - 1)).xpath('./div[@id]')
            num_table = len(div_table)
            for k in xrange(1, num_table + 1):
                text_list = div_table[k - 1].xpath('./div/div[@class="subcategory-header"]/div[1]/text()').extract()
                c_name = name + '-' + ' '.join(text_list).strip()

                title = ['Description']
                for a in div_table[k - 1].xpath('./div/table//a[@class="column-header"]'):
                    title.append(' '.join(a.xpath('./text()').extract()))

                i = 1
                for a in div_table[k - 1].xpath('./div/table//a[@class="product-white"]'):
                    type_num = a.xpath('./text()').extract()[0]
                    desc = a.xpath('./@title').extract()[0]
                    url  = a.xpath('./@href').extract()[0]
                    tr = div_table[k - 1].xpath('./div/table//div[@class="body"]//tr[%s]' % i)
                    params = [desc]
                    i += 1
                    for td in tr.xpath('./td'):
                        val = td.xpath('./div/text()').extract()
                        if val:
                            params.append(' '.join(val))
                        else:
                            params.append('-')
                    yield scrapy.Request(response.urljoin(url), callback=self.tertius_parse, meta={'name' : c_name, 'type_num' : type_num, 'params' : params})
                    break
                break
            break

    def tertius_parse(self, response):
        print response.meta
        print response.url

