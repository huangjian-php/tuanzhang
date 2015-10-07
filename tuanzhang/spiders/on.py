# -*- coding: utf-8 -*-
import scrapy


class OnSpider(scrapy.Spider):
    name = "on"
    allowed_domains = ["onsemi.com"]
    start_urls = (
        'http://www.onsemi.com/',
    )

    def parse(self, response):
        pass
