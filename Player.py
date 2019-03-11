from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from BattleField import BattleField
from BattleShipClient import BattleShipClient
from random import randint
import json

class Player(BattleShipClient):
    def __init__(self, enemy_filed):
        super().__init__()
        self.my_shot = False
        self.last_hit_success = False
        self.enemy_filed = enemy_filed

        self.enemy_filed.table.cellClicked.connect(self.shot)
        self.find_enemy()

    def find_enemy(self):
        request = json.dumps({
            'action': 'find_enemy'
        })
        response = self.call(request)
        # response = json.loads(response.decode("utf-8"))
        self.enemy_id = response.get('enemy_queue')
        print(self.enemy_id)
        self.my_shot = response.get('first_hit')

        self.response = None
        if not self.my_shot:
            while self.response is None:
                self.connection.process_data_events()

    def shot(self):
        if self.my_shot:
            item = self.enemy_filed.table.currentItem()
            x = item.row()
            y = item.column()
            if self.is_valid_shot(x, y):
                print("Человек выстрелил по", x, y)
                # self.last_hit_success = self.enemy_filed.field[x][y] == BattleField.HIT_CELL

                hit = json.dumps({
                    'action': 'shot',
                    'enemy_id': self.enemy_id,
                    'x': x,
                    'y': y,
                })
                self.last_hit_success = self.call(hit)
                # оповещаем о выстреле
                self.enemy_filed.shooted.emit()
                # self.channel.start_consuming()
                return True
        return False

    def is_valid_shot(self, x, y):
        return self.enemy_filed.field[x][y] == BattleField.EMPTY_CELL
        # return self.enemy_filed.change_field_after_shot(x, y)
