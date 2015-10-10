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
