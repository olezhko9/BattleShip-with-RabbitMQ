import pika
import uuid
import json


class BattleShipClient(object):
    # TODO: клиент читает новое сообщение, только когда отправлят запрос сам
    def __init__(self):
        # подключились к брокеру сообщений
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        # создаем очередь с уникальным именем
        result = self.channel.queue_declare(auto_delete=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)


    def on_response(self, ch, method, props, body):

        body = self._load_from_json(body)
        print(body)
        if body.get('action') == 'shot':
            self.response = body
            self.call(json.dumps({
                'hitted': True,
            }), body.get('enemy_id'))
        if self.corr_id == props.correlation_id:
            self.response = body
            print('response:', self.response)


    def call(self, request, queue='battle_ship_queue'):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        """
        Отправка сообщений.
        exchange - точка обмена
        routing_key - имя очереди
        """
        self.channel.basic_publish(exchange='',
                                   routing_key=queue,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=request)

        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def get_response(self):
        return self.response

    def _load_from_json(self, byte_json):
        return json.loads(byte_json.decode("utf-8"))
