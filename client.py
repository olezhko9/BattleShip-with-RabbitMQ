from PyQt5.QtCore import pyqtSignal, QObject
import pika
import uuid
import json
import random

class BattleShipClient(QObject):

    # shot_status_signal = pyqtSignal()
    make_shot_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        # подключились к брокеру сообщений
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.response = None

        # создаем очередь с уникальным именем
        result = self.channel.queue_declare(auto_delete=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        print(body)
        # сообщение от сервера
        if self.corr_id == props.correlation_id:
            self.response = self._load_from_json(body)
            self.enemy_id = self.response.get('enemy_queue')
            self.my_shot = self.response.get('first_hit')
            print('Ответ от сервера:', self.response)
        # сообщение от другого клиента
        else:
            # self.my_shot = not self.my_shot
            self.response = self._load_from_json(body)
            print("Ответ от клиента:", self.response)

            # обрабатываем выстрел противника
            if self.response.get('action') == 'shot':
                # отправляем результат
                self.shot_status()
                self.make_shot_signal.emit()
                
                # делаем свой выстред
                # self.send_shot()
                # self.wait_shot()

            # узнаем рещультат выстрела
            elif self.response.get('action') == 'status':
                if self.response.get('status') == 0:
                    print('Мимо')
                else:
                    print('Попал')
                self.response = None

    def _call(self, request, queue='battle_ship_queue'):
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=queue,
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,
                                       correlation_id=self.corr_id,
                                   ),
                                   body=json.dumps(request))

        if queue == 'battle_ship_queue':
            while self.response is None:
                self.connection.process_data_events()

        return self.response


    def send_shot(self, x, y):
        print('Стреляю по врагу')
        shot = {
            'action': 'shot',
            'hit': [x, y],
        }
        self._call(shot, self.enemy_id)
        self.wait_shot()


    def shot_status(self):
        print('Отправляю результат')
        status = {
            'action': 'status',
            'status': random.randint(0, 9) % random.randint(1, 9) == 0,
        }
        self._call(status, self.enemy_id)

    def find_enemy(self):
        self._call({
            'action': 'find_enemy'
        })

    def wait_shot(self):
        self.response = None
        while self.response is None:
            print(self.response)
            self.connection.process_data_events(time_limit=2)

    def get_random_coordinats(self):
        return random.randint(0, 9), random.randint(0, 9)

    def _load_from_json(self, byte_json):
        return json.loads(byte_json.decode("utf-8"))


if __name__ == '__main__':
    client = BattleShipClient()
