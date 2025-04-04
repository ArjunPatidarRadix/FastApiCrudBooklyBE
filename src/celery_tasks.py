from celery import Celery
from src.mail import mail, create_message
from asgiref.sync import async_to_sync

"""
# To start the celery server to send the emails in background worked
# celery -A src.celery_tasks.c_app worker --loglevel=INFO

#Setup the redis in docker image
docker pull redis/redis-stack-server:latest
docker run -d --name redis-stack-server -p 6379:6379 redis/redis-stack-server:latest
docker ps


Also to check the celery task in background use the flower for the UI
pip install flower
celery -A src.celery_tasks.c_app flower

"""


c_app = Celery()

c_app.config_from_object("src.config")


@c_app.task()
def send_email(recipients: list[str], subject: str, body: str):

    message = create_message(recipients=recipients, subject=subject, body=body)

    async_to_sync(mail.send_message)(message)
    print("Email sent")
