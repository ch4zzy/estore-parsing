from app.parse import parse_categories, load_categories_to_json, \
    write_max_pages_number_to_json, parse_all_products_from_categories, \
    load_products_to_json
import json
from typing import Iterator
from app.models import Product
from app.config import URL, DATA_PATH, MONGO_URL
import pymongo as mdb
from datetime import datetime


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
    collection = db["products"]
    return collection


def load_json_to_db(client, products: json) -> None:
    """
    One time action
    """
    with open(products, "r") as file:
        data = json.load(file)
    
    for item in data:
        try: 
            client.insert_one(item)
            print(item)
        except Exception as e:
            print(e)
            continue
    
    return None
    

def delete_duplicates_from_json(file: json):
    with open(DATA_PATH + file, "r", encoding="utf-8") as f:
        data = json.load(f)

    unique_data = list({json.dumps(item, sort_keys=True) for item in data})
    unique_data = [json.loads(item) for item in unique_data]

    with open(f"{DATA_PATH}unique_{file}", "w", encoding="utf-8") as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=4)
    
    return None


def update_db_create_report(products: json, client) -> None:
    """
    Update database and create report
    """
    report_lines = []

    with open(DATA_PATH + products, "r") as file:
        data = json.load(file)
    print("DB started updating")
    for item in data:
        existing_product = client.find_one({"_id": item["_id"]})
        if not existing_product:
            report_lines.append(f"Product {item['_id']} was first time added")
            client.insert_one(item)
        else:
            if existing_product["price_discount"] != item["price_discount"]:
                report_lines.append(f"Product {item['_id']} discount price was updated")
                client.update_one({"_id": item["_id"]}, {"$set": {"price_discount": item["price_discount"]}})
            if existing_product["price_default"] != item["price_default"]:
                report_lines.append(f"Product {item['_id']} price was updated")
                client.update_one({"_id": item["_id"]}, {"$set": {"price_default": item["price_default"]}})
            if existing_product["available_status"] != item["available_status"]:
                report_lines.append(f"Product {item['_id']} available_status was updated")
                client.update_one({"_id": item["_id"]}, {"$set": {"available_status": item["available_status"]}})
    print("DB updated")
    print("Report:", report_lines)
    if report_lines:
        with open(f"{DATA_PATH}{datetime.now()}.txt", "a") as file:
            file.write("\n".join(report_lines))
            file.write("\n\n")
    return None


def parse_shop():
    """
    Parser call order
    """

    categories: json = parse_categories(URL)

    categories_file_name: str = load_categories_to_json(categories)
    categories_file: json = DATA_PATH + categories_file_name
    write_max_pages_number_to_json(categories_file)

    products_generator: Iterator[Product] = parse_all_products_from_categories(categories_file)
    products: list = list(products_generator)
    products_file_name: str = load_products_to_json(products)
    return products_file_name


def start_all():
    file_name = parse_shop()
    delete_duplicates_from_json(file_name)
    file_name = f"unique_{file_name}"
    update_db_create_report(file_name, init_db())
    return None
