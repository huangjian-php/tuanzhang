# -*- coding: utf-8 -*-
import scrapy


class IrSpider(scrapy.Spider):
    name = "ir"
    allowed_domains = ["irf.com.cn"]
    start_urls = (
        'http://www.irf.com.cn/',
    )

    def parse(self, response):
        pass
