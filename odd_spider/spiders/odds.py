# -*- coding: utf-8 -*-
import scrapy, csv, os
from scrapy.selector import HtmlXPathSelector
from scrapy.http.request import Request
from scrapy.spiders import CrawlSpider
# import urlparse
from collections import OrderedDict


class OddsSpider(CrawlSpider):
    name = 'odds'
    allowed_domains = ['odds.pt']
    start_urls = ['http://odds.pt/']
    house_name = {
        'https://odds.pt/public/content/dd5530bf438ec1ae797ce4397d28a6be169e82991490114277.png?v58' : 'Betclic',
        'https://odds.pt/public/content/a6700bbc5a0db5db61012fab6ccfe51112ab11d61505477910.png?v58' : 'Bet.pt',
        'https://odds.pt/public/content/6beddc50902e3392678a0fb0b4d65cb19d76c3001488545659.jpg?v58': 'Casino Portugal',
        'https://odds.pt/public/content/1cf0d926e365d3c6b3688aaf9564bc3e58f5a2f71490114273.png?v58' : 'Placard'
    }
    results = []
    def parse(self, response):
        game_url = response.xpath('//td[@class="tiny"]/a/@href').extract()
        for i, url in enumerate(game_url):
            url1 = response.urljoin(url)
            yield Request(url1, callback=self.parse_dir_contents, meta={'id': i+1})

    def parse_dir_contents(self, response):
        # item = OddsScrapeItem()

        hxs = HtmlXPathSelector(response)
        home_team = hxs.select('.//div[@class="odd-game base-padding-full"]/div[@class="box40 f-left odd-team odd-home"]/span/text()').extract()[0]
        away_team = hxs.select('.//div[@class="odd-game base-padding-full"]/div[@class="box40 f-left odd-team odd-away"]/span/text()').extract()[0]


        headers = ['RESULTADOFINAL_1', 'RESULTADOFINAL_*', 'RESULTADOFINAL_2', 'RESULTADOINTERVALO_1', 'RESULTADOINTERVALO_*', 'RESULTADOINTERVALO_2',
                   'ACIMA 1.5', 'ABAIXO 1.5', 'ACIMA 2.5', 'ABAIXO 2.5', 'ACIMA 3.5', 'ABAIXO 3.5', 'ACIMA 4.5', 'ABAIXO 4.5']
        json_data = {}
        resultadofinal = response.xpath('.//table[contains(@class,"odd-comparator op1")]/tr')
        for i, tr in enumerate(resultadofinal):
            if i == 0: continue
            house_name = self.house_name[tr.xpath('./td[1]/img/@src').extract_first()]
            json_data[house_name] = {}
            json_data[house_name]['RESULTADOFINAL_1'] = ''.join(tr.xpath('./td[2]//text()').extract())
            json_data[house_name]['RESULTADOFINAL_*'] = ''.join(tr.xpath('./td[3]//text()').extract())
            json_data[house_name]['RESULTADOFINAL_2'] = ''.join(tr.xpath('./td[4]//text()').extract())

        resultadofinal = response.xpath('.//table[contains(@class,"odd-comparator op2")]/tr')
        for i, tr in enumerate(resultadofinal):
            if i == 0: continue
            house_name = self.house_name[tr.xpath('./td[1]/img/@src').extract_first()]
            json_data[house_name]['RESULTADOINTERVALO_1'] = ''.join(tr.xpath('./td[2]//text()').extract())
            json_data[house_name]['RESULTADOINTERVALO_*'] = ''.join(tr.xpath('./td[3]//text()').extract())
            json_data[house_name]['RESULTADOINTERVALO_2'] = ''.join(tr.xpath('./td[4]//text()').extract())

        tables_unders = response.xpath('//table[@class="odd-comparator op3"]')
        for j, table1 in enumerate(tables_unders):
            for i, tr in enumerate(table1.xpath('./tr')):
                if i == 0: continue
                house_name = self.house_name[tr.xpath('./td[1]/img/@src').extract_first()]
                json_data[house_name]['ACIMA {}'.format(1.5 + j)] = ''.join(tr.xpath('./td[2]//text()').extract())
                json_data[house_name]['ABAIXO {}'.format(1.5 + j)] = ''.join(tr.xpath('./td[4]//text()').extract())

        for key in json_data.keys():
            odd_dict = OrderedDict()
            odd_dict['Game ID'] = response.meta['id']
            odd_dict['House'] = key
            odd_dict['HomeTeam'] = home_team
            odd_dict['AwayTeam'] = away_team
            for value in headers:
                if value in json_data[key].keys():
                    odd_dict[value] = json_data[key][value]
                else:
                    odd_dict[value] =''

            # odd_dict['url'] = response.url
            yield odd_dict
            self.results.append(odd_dict)

