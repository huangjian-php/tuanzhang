# -*- coding: utf-8 -*-
import scrapy
import csv
import codecs


class OnSpSpider(scrapy.Spider):
    name = "on_sp"
    #allowed_domains = ["monolithicpower.com"]
    start_urls = (
        'http://www.onsemi.cn/',
    )

    def __init__(self):
        self.fp = codecs.open(u'on/手册/sheet1.csv', 'w+', 'utf_8_sig')
        self.fp_fail = codecs.open(u'on/手册/sheet_fail.csv', 'w+', 'utf_8_sig')
        self.fp_re = codecs.open(u'on/手册/sheet_re.csv', 'w+', 'utf_8_sig')
        title = ['"型号ID"', '"型号名称"', '"所属节点"', '"节点路径"', '"DataSheet"']
        csv_str = ','.join(title) + "\n"
        self.fp.write(csv_str)
        self.fp_fail.write(csv_str)
        csvfile = open('ON.csv', 'rb')
        reader = csv.reader(csvfile)
        self.info = {}
        i = 0
        for line in reader:
            i += 1
            if 1 == i:
                continue
            self.info[line[1]] = line

        print '------------------', i
        k = 0
        for key, val in self.info.items():
            k += 1
        print '------------------', k
        csvfile.close()

    def parse(self, response):
        url = 'http://www.onsemi.cn/PowerSolutions/search.do?query={0}&exc=yes&basic=yes&param1=type&param1_val=document&param2=doc_type&param2_val=Data%20Sheet'

        for key, val in self.info.items():
            yield scrapy.Request(url.format(key), callback=self.second_parse, meta={'name' : key}, dont_filter=True)

    def second_parse(self, response):
        item = response.xpath('//h4[@class="result-title"]/a/@href').extract()
        key = response.meta['name']
        info = self.info[key]
        if item:
            for url in item:
                sheet_url = response.urljoin(url)
                csv_list = info[:4] + [sheet_url]
                tpl = ['"%s"'] * 5
                csv_str = ','.join(tpl) % tuple(csv_list) + "\n"
                self.fp.write(csv_str)
                print sheet_url
        else:
            tpl = ['"%s"'] * 4
            csv_str = ','.join(tpl) % tuple(info[:4]) + "\n"
            self.fp_fail.write(csv_str)

        del self.info[key]


    def closed(spider, reason):
        spider.fp.close()
        spider.fp_fail.close()
        for key, val in spider.info.items():
            tpl = ['"%s"'] * 4
            csv_str = ','.join(tpl) % tuple(val[:4]) + "\n"
            spider.fp_re.write(csv_str)
        spider.fp_re.close()

