from parse import parse_categories, load_categories_to_json, \
    write_max_pages_number_to_json, parse_all_products_from_categories, \
    load_products_to_json
import json
from typing import Iterator
from models import Product
from config import URL, DATA_PATH
import pymongo as mdb
import os 
from dotenv import load_dotenv


load_dotenv()
MONGO_URL = os.get_env("MONGO_URL")


def init_db():
    """
    Database init
    """
    client = mdb.MongoClient(
        MONGO_URL,
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    db = client["chazzy-cluster"]
    collection = db["estore-parsing"]
    return collection


def load_json_to_db(client):
    """
    One time action
    """
    pass


def main():
    """
    Parser call order
    """

    categories: json = parse_categories(URL)

    categories_file_name: str = load_categories_to_json(categories)
    categories_file: json = DATA_PATH + categories_file_name
    write_max_pages_number_to_json(categories_file)
    exit

    products_generator: Iterator[Product] = parse_all_products_from_categories(categories_file)
    products: list = list(products_generator)
    products_file_name: str = load_products_to_json(products)

if __name__ == "__main__":
    main()


