import re
import sys



from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule

GOOGLE_RE = re.compile('https://www.google\.\w{2,3}')


class DataSpider(CrawlSpider):
    """
    Spider responsible for gathering urls matching given word.
    """
    name = 'data_spider'

    rules = (
        Rule(LinkExtractor(restrict_xpaths="//h3[@class='r']"), callback='parse_item'),
    )

    def __init__(self, mongodb_params=None, *a, **kw):
        super(DataSpider, self).__init__(*a, **kw)
        try:
            self.client = MongoClient('mongodb://{user}:{passwd}@{host}:{port}/{db}'
                .format(**mongodb_params))
            self.client.server_info()
            self.database_name = mongodb_params['db']
        except ServerSelectionTimeoutError:
            self.logger.error("Could not connect to mongo (timeout), nothing will be saved!")
            self.client = None

    def parse_item(self, response):
        """
        Parses single item.
        """
        if GOOGLE_RE.match(response.url):
            return
        selector = Selector(response)
        title = selector.xpath('//title/text()').extract()[0]
        self.save_item(title, response.url)

    def save_item(self, text, url):
        """
        Saves single item in database.
        """
        self.logger.info("Saving %s - %s", text, url)
        if self.client:
            try:
                self.client[self.database_name].text.insert_one({'title': text, 'url': url})
            except Exception as e:
                self.logger.error("Could not save item: %s", e)
        else:
            self.logger.error("Could not save item: db connection not active!")
