# -*- coding: utf-8 -*-
import scrapy


class GdSpider(scrapy.Spider):
    name = "gd"
    allowed_domains = ["gigadevice.com"]
    start_urls = (
        'http://www.gd.com/',
    )

    def parse(self, response):
        pass
