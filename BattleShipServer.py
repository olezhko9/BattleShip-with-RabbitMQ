import pika
import json

# подключились к брокеру сообщений
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
# создаем очередь
channel.queue_declare(queue='battle_ship_queue')

# список подключенных игроков
clients = []

class ConnectedPlayer:
    def __init__(self, queue_name, corr_id):
        self.queue_name = queue_name
        self.enemy_queue_name = None
        self.last_msg_corr_id = corr_id

    def set_enemy(self, enemy):
        self.enemy_queue_name = enemy.queue_name


def on_request(ch, method, props, body):
    # переводим байты в словарь
    request = json.loads(body.decode("utf-8"))
    action = request.get('action')
    print(request)
    # клиент запрашивает подбор противника
    if action == 'find_enemy':
        client = ConnectedPlayer(props.reply_to, props.correlation_id)
        clients.append(client)
        # при каждом втором подключенном игроке объединяем 2 последних игрока в пару
        if len(clients) % 2 == 0:
            clients[-1].set_enemy(clients[-2])
            clients[-2].set_enemy(clients[-1])
            first = True
            for c in clients[-2:]:
                print('send from {} to {}'.format(c.queue_name, c.enemy_queue_name))
                response = json.dumps({
                    'enemy_queue': c.enemy_queue_name,
                    'first_hit': first,
                })
                first = not first
                ch.basic_publish(exchange='',
                                 routing_key=c.queue_name,
                                 properties=pika.BasicProperties(correlation_id=c.last_msg_corr_id),
                                 body=response)
    elif action == 'shot':
        for client in clients:
            if client.queue_name == props.reply_to:
                client.last_msg_corr_id = props.correlation_id
                ch.basic_publish(exchange='',
                                 routing_key=client.enemy_queue_name,
                                 properties=pika.BasicProperties(correlation_id=client.last_msg_corr_id),
                                 body=body)

    # подтверждение сообщений
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(consumer_callback=on_request, queue='battle_ship_queue')

print("Сервер стартовал")
channel.start_consuming()
