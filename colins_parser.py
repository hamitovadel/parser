import logging
import collections
import csv

import bs4
import requests


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('wb')


ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'goods_name',
        'url',
        'price'
    ),
)

HEADERS = (
    'Товар',
    'Цена'
    'Ссылка',
)

class Client:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.result = []

    def load_page(self):
        url = 'https://www.colins.ru/c/muzhchinam-sweatshirt-177'
        res = self.session.get(url=url)
        res.raise_for_status()
        return res.text

    def parse_page(self, text:str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.col-lg-4.md-4.col-sm-4.col-4.col-mobile-list')
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):
        #logger.info(block)
        #logger.info('=' * 100)

        product_block = block.select_one('a.product-name.track-link')
        if not product_block:
            logger.error('no product_block')
            return

        goods_name = product_block.get('title')
        if not goods_name:
            logger.error(f'no goods_name on')
            return

        url = product_block.get('href')
        if not url:
            logger.error('no href')
            return

        price = block.select_one('div.product-price-content')
        if not price:
            logger.error(f'no price on {url}')
            return

        price = price.text.strip()

        self.result.append(ParseResult(
            goods_name=goods_name,
            url=url,
            price=price,
        ))

        logger.debug('%s, %s, %s', url, goods_name, price)
        logger.debug('-' * 100)

    def save_result(self):
        path='/Users/hamitov/PycharmProjects/parser/colins.csv'
        with open(path, 'w', encoding='utf-8') as f:
            writer = csv.writer(f,quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

    def run(self):
        text = self.load_page()
        self.parse_page(text=text)
        logger.info(f'Получили {len(self.result)} элементов')
        self.save_result()

if __name__ == '__main__':
    parser = Client()
    parser.run()
