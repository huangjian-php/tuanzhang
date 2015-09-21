# -*- coding: utf-8 -*-
import scrapy


class SheetMpsSpider(scrapy.Spider):
    name = "sheet_mps"
    allowed_domains = ["monolithicpower.com"]
    start_urls = (
        'http://www.monolithicpower.com/',
    )

    def parse(self, response):
        pass
