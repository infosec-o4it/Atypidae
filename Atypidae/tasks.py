from celery import Celery

#app = Celery('tasks', backend='amqp', broker='amqp://')
app = Celery('tasks', backend='amqp', broker='amqp://guest:linux@localhost/')


@app.task
def add(x, y):
    return x + y
