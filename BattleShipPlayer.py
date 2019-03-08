from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from BattleField import BattleField
from random import randint


class BattleShipPlayer(QObject):
    """
    Базовый класс для игроков, сражающихся друг против друга
    """
    shooted = pyqtSignal()

    def __init__(self, enemy: BattleField):
        """
        :param enemy: Поле боя соперника
        """
        super(BattleShipPlayer, self).__init__()
        self.my_shot = False
        self.last_hit_success = False
        self.enemy = enemy

    @pyqtSlot()
    def shot(self, x, y):
        # смотрим, попал ли выстрел в цель
        self.last_hit_success = self.enemy.field[x][y] == BattleField.HIT_CELL
        # оповещаем о выстреле
        self.shooted.emit()
        # TODO: отправка данных о выстреле на сервер

    def is_valid_shot(self, x, y):
        return self.enemy.change_field_after_shot(x, y)

    @staticmethod
    def next_player(player_1, player_2):
        """
        Меняет очередность хода.
        """
        player_1.my_shot = not player_1.my_shot
        player_2.my_shot = not player_2.my_shot



class RealPlayer(BattleShipPlayer):

    def __init__(self, enemy):
        super(RealPlayer, self).__init__(enemy)
        self.enemy.table.cellClicked.connect(self.shot)

    def shot(self, *args):
        if self.my_shot:
            item = self.enemy.table.currentItem()
            x = item.row()
            y = item.column()
            if self.is_valid_shot(x, y):
                print("Человек выстрелил по", x, y)
                super().shot(x, y)
                return True
        return False



class BotPlayer(BattleShipPlayer):
    """
    Бот, играющий в морской бой против соперника, указанного в конструкторе.
    """

    def shot(self, *args):
        """
        Функция выстрела, пытающаяся найти еще не обстреленные координаты на поле противника случайным образом.
        :return: x, y - координаты выстрела.
        """
        if self.my_shot:
            while True:
                x = randint(0, self.enemy.FIELDS_NUM - 1)
                y = randint(0, self.enemy.FIELDS_NUM - 1)
                if self.is_valid_shot(x, y):
                    print("Бот выстрелил по", x, y)
                    super().shot(x, y)
                    return True
        return False
