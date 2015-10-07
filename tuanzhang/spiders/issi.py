# -*- coding: utf-8 -*-
import scrapy


class IssiSpider(scrapy.Spider):
    name = "issi"
    allowed_domains = ["issi.com"]
    start_urls = (
        'http://www.issi.com/',
    )

    def parse(self, response):
        pass
