import requests

import json
from bs4 import BeautifulSoup

cookies = {
    """ Вставляем куки"""
}

headers = {
    """ Вставляем заголовок """
}

urls = {
    "catalog": "/catalog/",
    "videokarty": {
        "url":"https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/",
        "tag":"a",
        "class_":"catalog-product__name ui-link ui-link_black"
    }}

def find_values_from_key(key, json_object):
    """TODO посмотреть, может можно переписать эту лагающую херню)"""
    if isinstance(json_object, list):
        for list_element in json_object:
            yield from find_values_from_key(key, list_element)
    elif isinstance(json_object, dict):
        if key in json_object:
            yield json_object[key]
        for dict_value in json_object.values():
            yield from find_values_from_key(key, dict_value)

def search_Pages(url):
    """
        Поиск количества странниц в категории товара
    """
    response = response_get(url)
    data = json.loads(response.text)
    root = BeautifulSoup(data['html'], 'lxml')

    number_str = []
    parse_namber_str = root.find_all('a', class_='pagination-widget__page-link', href=True)
    if len(parse_namber_str)<1:
        return int(1)
    else:
        for tag in parse_namber_str:
            if tag.get('href')[0] == '/':
                number_str.append(tag.get('href'))
        return int(number_str[-1][-2:])

def response_get(url, params=None):
    """
        Метод запросов GET.
        Возвращает строку с HTML документом.
    """
    response = requests.get(url, cookies=cookies, headers=headers, params=params)

    return response

def price(data_product):
    """"
        Метод парсит цену товара, а точнее, пока что извлекает JSON обьект с содержимым productID
        TODO Требуется Ускорить работу
    """
    """ Как ты и заметил куки и заголовки продублированы в методе PRICE
        Это не случайно. По какой то причине те куки с заголовком, которые отправляются с основным запросом
        не работают. Пришлось отправлять новые... Вероятно вся проблема в csrf токене, а может и нет.
        Не было особо времени заниматься этим. 
    """
    cookiessss = {
        """ Вставляем куки 
        """
    }

    headerssss = {
        """ Вставляем заголовок """
    }

    data_headers = f'data={{"type":"product-buy","containers":' \
                   f'[{{"id":"as-X0HjkI","data":{{"id":"%s"}}}}]}}' % data_product

    params_headers = {
        'cityId': '15', # В данном параметре передается наименование города, в котором ищется товар
        'langId': 'ru',
        'v': '2',
    }

    response = requests.post("https://www.dns-shop.ru/ajax-state/product-buy/",
                            cookies=cookiessss, headers=headerssss, data=data_headers,params=params_headers)

    root = json.loads(response.text)

    return root

def par_videokarty(url):
    """
            Парсер стрницы https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/
    """
    pages = {
        "p": str(search_Pages(url)),
    }

    for page_number in range(1,int(pages["p"])+1):
        response = response_get(url, params={"p":page_number})
        data = json.loads(response.text)
        root = BeautifulSoup(data['html'], 'lxml')
        print('___________________________')
        print('Страница - ', page_number,'\n')
        allSmartfony = root.find_all(urls["videokarty"]["tag"], class_=urls["videokarty"]["class_"])
        art_phone = root.find_all("div", class_="catalog-product ui-button-widget")
        product_id = root.find_all("div", class_="catalog-product ui-button-widget")
        hrefs = root.find_all("a", class_="catalog-product__name ui-link ui-link_black")
        for art, name, data_product, href in zip(art_phone,allSmartfony, product_id,hrefs):
            len_product_name = name.find('span')
            product_art = art.get('data-code')
            data_bd_name = data_product.get('data-product')
            href_links = href.get('href')
            a = list(find_values_from_key("current", price(data_bd_name)))[0]
            b = str(a)
            print('найден товар - ', href_links)
            """ insert_table_smart - Запись в БД артикул, наименование, цену и ссылку товара"""
            # insert_table_smart(product_art,len_product_name.text, b, href_links)

            # TODO Написать более простую функцию фарсинга цены у товара.... Слишком большие задержки
            with open("all_tovar_video.txt", 'a', encoding="utf-8") as f:
                f.write(str(product_art+" - "+len_product_name.text+" - "+b+'\n'))
                f.close()
            print(str(product_art)," - ",len_product_name.text, ' ___ ', b, " Р")
    print('Всего страниц - ', search_Pages(url),'\n')

par_videokarty("https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/")
