import pika
import uuid


class BattleShipClient(object):
    def __init__(self):
        # подключились к брокеру сообщений
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        # создаем очередь с уникальным именем
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, action):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        """
        Отправка сообщений.
        exchange - точка обмена
        routing_key - имя очереди
        """
        self.channel.basic_publish(exchange='',
                                   routing_key='battle_ship_queue',
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=action)
        while self.response is None:
            self.connection.process_data_events()
        return self.response

if __name__ == '__main__':
    fibonacci_rpc = BattleShipClient()

    print(" [x] Requesting shot")
    response = fibonacci_rpc.call("shot")
    print(" [.] Got %r" % (response,))
