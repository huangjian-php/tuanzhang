# -*- coding: utf-8 -*-
import scrapy
import urlparse, json, re


class FslSpider(scrapy.Spider):
    name = "fsl"
    allowed_domains = ["freescale.com"]
    start_urls = (
        'http://www.freescale.com/zh-Hans/webapp/parametricSelector.sp',
    )
    category = ['c28', 'c32', 'c250', 'c265', 'c358', 'c380', 'c381']

    def parse(self, response):
        uls = response.xpath('//div[@id="prodMenu"]/div/ul')
        url = 'http://www.freescale.com/webapp/search/loadJSON.sp?c=%s&lang_cd=zh-Hans'
        for ul in response.xpath('//div[@id="prodMenu"]/div/ul'):
            for li in ul.xpath('./li'):
                name = li.xpath('./span/span/text()').extract()
                if len(name) > 1:
                    #name = '®'.join(name)
                    name = ' '.join(name)
                else:
                    name = name[0]
                name = name.strip()
                for li_v in li.xpath('./ul/li'):
                    c_name = name + '-' + li_v.xpath('./span/a/text()').extract()[0].strip()
                    src_url = li_v.xpath('./span/a/@href').extract()[0]
                    result = urlparse.urlparse(src_url)
                    params = urlparse.parse_qs(result.fragment, True)
                    yield scrapy.Request(url % params['c'][0], callback=self.secondary_parse, meta = {'name' : c_name, 'num' : params['c'][0]})
                    #break
                #break
            #break

    def secondary_parse(self, response):
        data = json.loads(response.body)
        title = []
        key = []
        tpl = []
        tpl_pre = ['"%s"'] * 6
        for val in data['paraheader']:
            title.append(val['name'])
            key.append(val['shortName'])
            tpl.append('"%(' + val['shortName'] + ')s"')
        title[0:0] = ['brand', 'Series', 'PartNo', 'DetailLink', 'Document', 'Description']
        pattern = r'href="(.+?)"'
        regular = re.compile(pattern, re.DOTALL)

        fp = open('fsl/main/' + re.sub(r'[/:|?*"\\<>]', '&', response.meta['name']) + '.csv', 'w+')
        n = 1
        fp.write(','.join(['"%s"'] * len(title)) % tuple(title) + "\n")
        
        for pro in data['prod']:
            if pro.has_key('p775'):
                match = regular.findall(pro['p775'])
                match = map(response.urljoin, match)
                pro['p775'] = '|'.join(match)
            for val in key:
                if not pro.has_key(val):
                    pro[val] = '-'
            head = [
                'FSL',
                response.meta['name'],
                pro['ProdCode']['Name'],
                response.urljoin(pro['ProdCode'].get('overviewURL', '-')),
                response.urljoin(pro['ProdCode'].get('documentationURL', '-')),
                pro['ProdCode']['Desc']
                ]
            csv_str = (','.join(tpl_pre) % tuple(head)) + ',' + (','.join(tpl) % pro) + "\n"
            fp.write(csv_str.encode('utf-8'))
            n += 1
            if n > 20:
                fp.flush()

            if pro['ProdCode'].has_key('documentationURL'):
                yield scrapy.Request(response.urljoin(pro['ProdCode']['documentationURL']), callback=self.tertius_parse, meta={'name' : response.meta['name'], 'type_number' : pro['ProdCode']['Name']})
        fp.close()

    def tertius_parse(self, response):
        fp = open('fsl/手册/' + response.meta['type_number'] + '.csv', 'w+')
        n = 0
        for section in response.xpath('//section'):
            name = section.xpath('./h2/text()').extract()[0]
            urls = [name]
            for tr in section.xpath('./table/tbody/tr'):
                url = tr.xpath('./td[1]/ul[1]/li/a/@href').extract()[0]
                urls.append(url)

            tpl = ['"%s"'] * len(urls)
            fp.write(','.join(tpl) % tuple(urls) + "\n")
            n += 1
            if n > 20:
                fp.flush()

        fp.close()

