import time
from celery_app import celery_app

@celery_app.task
def add(x, y):
    return x + y

@celery_app.task
def slow_square(n):
    time.sleep(5)                 # blocking is fine in a worker
    return n * n