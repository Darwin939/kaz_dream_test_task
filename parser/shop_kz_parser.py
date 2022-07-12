from cgitb import text
import requests
import logging
from multiprocessing import Pool
import json

from bs4 import BeautifulSoup


URL = 'https://shop.kz/smartfony/'

logger = logging.getLogger(__name__)


MAPPER = {
    "Емкость аккумулятора:": "battery_capacity",
    "Размер экрана, дюйм:": "screen_size",
    "Разрешение экрана:": "screen_resolution",
    "Тип матрицы:": "matrix_type",
    "Объем встроенной памяти:": "built_in_memory_size",
    "Модель процессора:": "processor_model",
    "Основная камера, Мп:": "main_camera",
    "Фронтальная камера, Мп:": "front_cam",
    "Беспроводные интерфейсы:": "wireless_interface",
    "Дополнительно:": "additional",
    "Объем оперативной памяти:": "ram_memory_size",
}


class Request:

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:102.0) Gecko/20100101 Firefox/102.0'}

    def make_request(self, uri: str, path: str, request_method: str, *args, **kwargs) -> requests.Response:
        url = uri + path
        request = getattr(requests, request_method)
        try:
            resp = request(url, **kwargs)
        except requests.exceptions.ConnectionError as exc:
            logger.error(
                f'HTTP error {url} {request_method.upper()}',
                extra={'error_msg': exc.args[0]},
            )
            raise exc

        log_message = (
            f'HTTP response ({resp.status_code}) {request_method.upper()} {url}'
        )
        log_extra = {
            'response_headers': resp.headers,
            'response_url': resp.url,
        }

        log_extra.update({'response_data': resp.text})
        logger.info(log_message, extra=log_extra)

        return resp


class ShopKzParser(Request):

    _SMARTPHONE_PATH = 'filter/almaty-is-v_nalichii-or-ojidaem-or-dostavim/apply/'

    def parse_smartphones(self):
        products = []
        with Pool() as pool:
            results_iter = pool.imap(self.smartphone_request_and_parse, range(1,14))

            for res in results_iter:
                products += res

        # smartphones.json
        json_object = json.dumps(products, indent = 4)

        with open("smartphones.json", "w") as outfile:
            outfile.write(json_object)


    def smartphone_request_and_parse(self, page_num: int) -> list:
        print(page_num)
        path: str = f'{ self._SMARTPHONE_PATH }?PAGEN_1={ page_num }'
        response: requests.Response = self.make_request(
            URL, path=path, request_method='get', headers=self.HEADERS)
        soup = BeautifulSoup(response.content)
        product_div_items: list = soup.find_all(
            'div', class_='bx_catalog_item')

        products = []
        for product_div_item in product_div_items:
            product_name = self.parse_name(product_div_item)
            articul = self.parse_articul(product_div_item)
            price = self.parse_price(product_div_item)
            characteristics = self.parse_characteristics(product_div_item)
            product_dict = {
                'product_name': product_name,
                'articul': articul,
                'price': price,
                **characteristics,
            }
            products.append(product_dict)

        return products

    def parse_price(self, product_div_item) -> int:
        price_spans = product_div_item.find_all(
            'span', class_='bx-more-price-text')

        prices = []
        for price_span in price_spans:
            price_text = price_span.get_text()
            price = ''.join([str(s) for s in price_text.rstrip() if s.isdigit()])
            prices.append(int(price))

        price = ''.join([str(s) for s in price_text.rstrip() if s.isdigit()])
        return min(prices)

    def parse_articul(self, product_div_item):

        articul_text = product_div_item.find_all(
            'div', class_='bx_catalog_item_XML_articul')[0].get_text()

        articul_number = ''.join(
            [str(s) for s in articul_text.rstrip() if s.isdigit()])
        return int(articul_number)

    def parse_name(self, product_div_item):

        name = product_div_item.find_all(
            'h4', class_='bx_catalog_item_title_text')[0].get_text()

        return name

    def parse_characteristics(self, product_div_item) -> dict:
        characteristics = dict()

        property_names = product_div_item.find_all(
            'span', class_='bx_catalog_item_prop')
        property_values = product_div_item.find_all(
            'span', class_='bx_catalog_item_value')

        for property_name, property_value in zip(property_names, property_values):
            name = MAPPER.get(property_name.get_text(), 'other')
            characteristic = {
                name: property_value.get_text()
            }
            characteristics.update(
                **characteristic
            )

        return characteristics


if __name__ == '__main__':
    parser = ShopKzParser()
    parser.parse_smartphones()
