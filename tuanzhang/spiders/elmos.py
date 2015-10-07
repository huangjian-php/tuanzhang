# -*- coding: utf-8 -*-
import scrapy


class ElmosSpider(scrapy.Spider):
    name = "elmos"
    allowed_domains = ["elmos.com"]
    start_urls = (
        'http://www.elmos.com/',
    )

    def parse(self, response):
        pass
