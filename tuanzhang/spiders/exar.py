# -*- coding: utf-8 -*-
import scrapy


class ExarSpider(scrapy.Spider):
    name = "exar"
    allowed_domains = ["exar.com"]
    start_urls = (
        'http://www.exar.com/',
    )

    def parse(self, response):
        pass
