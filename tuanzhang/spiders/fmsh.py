# -*- coding: utf-8 -*-
import scrapy


class FmshSpider(scrapy.Spider):
    name = "fmsh"
    allowed_domains = ["fmsh.com"]
    start_urls = (
        'http://www.fmsh.com/',
    )

    def parse(self, response):
        pass
