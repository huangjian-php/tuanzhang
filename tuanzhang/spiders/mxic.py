# -*- coding: utf-8 -*-
import scrapy


class MxicSpider(scrapy.Spider):
    name = "mxic"
    allowed_domains = ["macronix.com"]
    start_urls = (
        'http://www.macronix.com/',
    )

    def parse(self, response):
        pass
