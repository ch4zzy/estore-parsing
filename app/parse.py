from models import Product, Category
import requests
from bs4 import BeautifulSoup as bs
import json
from dataclasses import asdict
from enum import Enum
from datetime import datetime
from config import DATA_PATH, URL
from typing import Iterator, List


def load_categories_to_json(categories: list) -> str:
    file_name = 'categories.json'
    categories_dict = [asdict(category) for category in categories]
    with open(f'{DATA_PATH}{file_name}', 'w', encoding='utf-8') as file:
        json.dump(categories_dict, file, ensure_ascii=False, indent=4)
    return file_name


def parse_categories(url: str) -> list:
    result = requests.get(url)
    soup = bs(result.text, 'lxml')
    categories = []
    for category in soup.find_all(
        'li', 
        class_='nav-item level0 nav-1 level-top first nav-item--parent classic nav-item--only-subcategories parent'):
        category_name = category.find('span').text
        category_link = category.find('a', class_='level-top').get('href')
        if category_link != URL + "#":
            categories.append(Category(name=category_name, link=category_link))
        else:
            result = requests.get(url + '#')
            soup = bs(result.text, 'lxml')
            print("Breakpoint", soup)
            for category in soup.find_all(
                'li', 
                class_='nav-item level1 nav-12-2 last nav-item--parent classic nav-item--only-subcategories parent'):
                category_name = category.find('a').text
                category_link = category.find('a').get('href')
                categories.append(Category(name=category_name, link=category_link))
    result = list({(cat.name, cat.link): cat for cat in categories}.values())
    result.pop(0)
    return result


def parse_max_page_number_from_category(category_link: str) -> list:
    result = requests.get(category_link)
    soup = bs(result.text, 'lxml')
    try:
        pages_count = soup.find('a', class_='last').text
        pages_count = int(pages_count)
    except:
        pages_count = soup.find(
            'nav', class_='pages'
        ).find('ol').find_all('li')
        page_numbers = []
        for link in soup.find_all('a'):
            try:
                page_num = int(link.text)
                page_numbers.append(page_num)
            except ValueError:
                continue
        pages_count = max(page_numbers) if page_numbers else None
    return pages_count     


def write_max_pages_number_to_json(categories_file: json) -> None:
    with open(categories_file, 'r', encoding='utf-8') as file:
        categories = json.load(file)
        
    for category in categories:
        page_number = parse_max_page_number_from_category(category['link'])
        category['page_count'] = page_number  

    with open(categories_file, 'w', encoding='utf-8') as file:
        json.dump(categories, file, ensure_ascii=False, indent=4)
    return None


def parse_products_from_category(category_params: dict) -> Iterator[List]:
    link = category_params["link"]
    pages_count = category_params["page_count"]
    status_translate = {
        "Есть в наличии": "Available",
        "Нет в наличии": "Not available",
        "Заканчивается": "Expires"
    }
    
    for page in range(1, pages_count + 1):
        result = requests.get(f"{link}page={page}/")
        print(f"Page {link}page={page}/ parsed")
        soup = bs(result.text, 'lxml')
        for product in soup.find_all('div', class_='item-inner'):
            url = product.find('a').get('href')
            result = requests.get(url)
            soup = bs(result.text, 'lxml')
            try:
                product_id = soup.find('div', class_='sku-holder').find('span', class_='value').text
            except AttributeError as e:
                product_id = None
                print("product not found", e)
            try:
                product_name = soup.find('h1', itemprop='name').text.strip('\n').strip().replace('\xa0', '').rstrip()
            except AttributeError as e:
                product_name = None
                print("product not found", e)
            product_category = category_params["name"]
            try:
                statuses = soup.find('p', class_='availability').text.strip()
                product_status = status_translate.get(statuses, None)
            except AttributeError as e:
                product_status = None
                print("product not found", e)
            
            if product_status is not None and product_status != "Not available":
                try: 
                    product_price_default = soup.find(
                        'p', class_='old-price'
                    ).find('span', class_='price').text.strip('\n').strip().replace('\xa0', '').rstrip()
                except AttributeError as e:
                    product_price_default = None
                    print("product price default", e)

                try:
                    product_price_discount = soup.find(
                        'p', class_='special-price'
                    ).find('span', class_='price').text.strip('\n').strip().replace('\xa0', '').rstrip()
                except AttributeError as e:
                    product_price_discount = None
                    print("product price discount", e)
            else:
                product_price_default = None
                product_price_discount = None

            product_link = url

            yield Product(
                    _id=product_id,
                    name=product_name,
                    category=product_category,
                    price_default=product_price_default,
                    price_discount=product_price_discount,
                    available_status=product_status,
                    link=product_link
                )
    

def parse_all_products_from_categories(categories_file: str) -> Iterator[List]:
    with open(categories_file, 'r', encoding='utf-8') as file:
        categories = json.load(file)

    for item in categories:
        yield from parse_products_from_category(item)


def load_products_to_json(products: Iterator[Product]) -> None:
    file_name = f"Snapshot-{datetime.now()}.json"
    products_dict = [asdict(product) for product in products]
    with open(f'{DATA_PATH}{file_name}', 'w', encoding='utf-8') as file:
        json.dump(products_dict, file, ensure_ascii=False, indent=4)
    return file_name
