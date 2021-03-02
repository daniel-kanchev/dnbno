import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from dnbno.items import Article


class DnbnoSpider(scrapy.Spider):
    name = 'dnbno'
    start_urls = ['https://www.dnb.no/dnbnyheter/']

    def parse(self, response):
        links = response.xpath('//a[contains(@class, "card-inner")]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="title"]/span//text()').get()
        if title:
            title = title.strip()
        else:
            return

        date = response.xpath('//div[@class="new-article"]/@data-timestamp').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="aem-Grid aem-Grid--10 aem-Grid--default--10 "]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
