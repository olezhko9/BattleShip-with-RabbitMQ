# RabbitMQ
# 1. Скачать RabbitMQ - https://www.rabbitmq.com/install-windows.html
# 2. pip install pika
import pika
from random import randint

# подключились к брокеру сообщений
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
# создаем очередь
channel.queue_declare(queue='battle_ship_queue')


def generate_shot():
    x = randint(0, 10 - 1)
    y = randint(0, 10 - 1)
    return x, y


def on_request(ch, method, props, body):
    response = None
    print(body)
    if body.decode("utf-8") == "shot":
        response = generate_shot()

    print("Выстрелил по:", response)
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=str(response))
    # подтверждение сообщений
    ch.basic_ack(delivery_tag=method.delivery_tag)

# не отдавать подписчику единовременно более одного сообщения
channel.basic_qos(prefetch_count=1)
# Получение сообщений
channel.basic_consume(on_request, queue='battle_ship_queue')

print(" [x] Awaiting RPC requests")
channel.start_consuming()