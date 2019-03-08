from PyQt5.QtCore import pyqtSlot
from abc import ABC, abstractmethod
from BattleField import BattleField
from random import randint


class BattleShipPlayer(ABC):
    """
    Базовый класс для игроков, сражающихся друг против друга
    """
    def __init__(self, enemy: BattleField):
        """
        :param enemy: Поле боя соперника
        """
        self.enemy = enemy

    @pyqtSlot()
    @abstractmethod
    def shot(self, x, y):
        return self.enemy.change_field_after_shot(x, y)



class RealPlayer(BattleShipPlayer):

    def __init__(self, enemy):
        super(RealPlayer, self).__init__(enemy)
        self.enemy.table.cellClicked.connect(self.shot)

    def shot(self, *args):
        item = self.enemy.table.currentItem()
        row = item.row()
        col = item.column()
        if super().shot(row, col):
            return row, col



class BotPlayer(BattleShipPlayer):
    """
    Бот, играющий в морской бой против соперника, указанного в конструкторе.
    """

    def shot(self, *args):
        """
        Функция выстрела, пытающаяся найти еще не обстреленные координаты на поле противника случайным образом.
        :return: x, y - координаты выстрела.
        """
        while True:
            x = randint(0, self.enemy.FIELDS_NUM - 1)
            y = randint(0, self.enemy.FIELDS_NUM - 1)
            if super().shot(x, y):
                return x, y
