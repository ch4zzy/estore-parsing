from celery import Celery, signals
from app.main import start_all
from app.config import CELERY_BROKER_URL

app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_BROKER_URL)


@app.task
def parse_shop_task():
    start_all()


@signals.worker_ready.connect
def at_start(sender, **kwargs):
    parse_shop_task.delay()
