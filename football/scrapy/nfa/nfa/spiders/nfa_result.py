# -*- coding: utf-8 -*-
import scrapy
import lxml
from nfa.items import NfaItem

class NfaResultSpider(scrapy.Spider):
    name = "nfa_result"
    allowed_domains = ["xleague.com"]
    start_urls = (
        'http://www.xleague.com/kiroku/',
    )

    def parse(self, response):
        path = '//table/tr/td/ul/li/a'
        result_year_items = response.xpath(path)
        if result_year_items:
            for html_element in result_year_items:
                resp_object = lxml.html.fromstring(html_element.extract())
                article = NfaItem()
                article['link'] = resp_object.attrib['href']
                article['link_text'] = resp_object.text
                if article['link'].find('ranking') > 0:
                    article['category'] = 'ranking'
                elif article['link'].find('result_list') > 0:
                    article['category'] = 'result_list'
                    yield scrapy.Request(article['link'], callback=self.parse_year_result_list)
                elif article['link'].find('diagram') > 0:
                    article['category'] = 'diagram'
                else:
                    article['category'] = 'other'
                #yield scrapy.Request(article['link'], callback=self.parse_year_result_list)

    def parse_year_result_list(self, response):
        iframe_tag = response.xpath('//div[@class="iframe"]/iframe[@src]').extract_first()
        iframe_object = lxml.html.fromstring(iframe_tag)
        src_url = iframe_object.attrib['src']
        yield scrapy.Request(src_url, callback=self.parse_result_item_list)

    def parse_result_item_list(self, response):
        html_objects = response.xpath('//table/tr/td[4]/a')
        for html_obj in html_objects:
            anchor_tag = lxml.html.fromstring(html_obj.extract())
            result = {}
            result['url'] = anchor_tag.attrib['href']
            result['text'] = anchor_tag.text
            yield scrapy.Request(result['url'], callback=self.parse_result_item_iframe)
 
    def parse_result_item_iframe(self, response):
        iframe_tag = response.xpath('//*[@id="testIfr1"]').extract_first()
        iframe_object = lxml.html.fromstring(iframe_tag)
        src_url = iframe_object.attrib['src']
        yield scrapy.Request(src_url, callback=self.parse_play_result)

    def parse_play_result(self ,response):
        result = {}
        result['text'] = response.text
        # TODO ここに試合結果のparseとデータの永続化を記載する
        yield response.text
