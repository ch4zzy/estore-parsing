import os
from dotenv import load_dotenv


load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
URL = "https://estore.ua/"
DATA_PATH = "data/"
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
