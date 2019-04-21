from BattleField import BattleField
from client import BattleShipClient
from PyQt5.QtCore import QTimer, QObject, pyqtSignal, pyqtSlot
from abc import ABC, ABCMeta, abstractmethod
import random


class MetaPlayer(ABCMeta, type(QObject)):
    pass


class Player(ABC, QObject, metaclass=MetaPlayer):
    shot_status_changed = pyqtSignal(bool)

    def __init__(self, player_field, enemy_filed):
        super().__init__()
        self.my_shot = False
        self.last_hit_success = False
        self.enemy_queue = None
        self.last_shot = None, None
        self.enemy_filed = enemy_filed
        self.player_field = player_field
        self.client = BattleShipClient(self)
        self.client.make_shot_signal.connect(self._on_other_player_shot)
        self.client.shot_status_signal.connect(self._on_shot_status)

    @abstractmethod
    def find_enemy(self):
        """
        Обращается к серверу для получения очереди соперника и информации о первом ходе.
        """
        self.client.find_enemy()
        self.enemy_queue = self.client.response.get('enemy_queue')
        self.my_shot = self.client.response.get('first_hit')
        self.shot_status_changed.emit(self.my_shot)

    @abstractmethod
    def shot(self, *kargs):
        """
        Отправляет координаты выстрела второму игроку.
        :param kargs: координаты выстрела
        """
        self.last_shot = kargs[0], kargs[1]
        self.client.send_shot(self.last_shot)

    @abstractmethod
    def _on_other_player_shot(self, x, y):
        """
        Вызывается при получении данных о выстреле соперника.
        Отправляет информацию о попадании или промахе сопернику.
        :param x, y: координаты выстрела соперника
        """
        # противник попал?
        is_hit = self.player_field.field[x][y] == BattleField.SHIP_CELL
        self.player_field.change_field_after_shot(x, y, is_hit)
        self.client.send_shot_status(is_hit)
        self.shot_status_changed.emit(not is_hit)

        return is_hit

    @abstractmethod
    def _on_shot_status(self, status):
        """
        Вызывается при получении информации от соперника о промахе или попадании.
        :param: status - мы попали?
        """
        self.enemy_filed.change_field_after_shot(*self.last_shot, status)
        self.shot_status_changed.emit(status)

    def _do_action_with_delay(self, action, delay):
        self.shot_process_timer = QTimer()
        self.shot_process_timer.setSingleShot(True)
        self.shot_process_timer.timeout.connect(action)
        self.shot_process_timer.start(delay)


class ActivePlayer(Player):

    def __init__(self, player_field, enemy_filed):
        super().__init__(player_field, enemy_filed)
        self.enemy_filed.table.cellClicked.connect(self.shot)

    def find_enemy(self):
        super().find_enemy()
        # если первый ход не наш, то ждем первый выстрел от противника
        if not self.my_shot:
            self.client.wait_shot()

    @pyqtSlot(int, int)
    def shot(self):
        """
        Вызывается при нажатии на клетку игрового поля.
        Если ход игрока, то проверяет выбранну клетку на допустимость выстрела.
        """
        if self.my_shot:
            item = self.enemy_filed.table.currentItem()
            row = item.row()
            col = item.column()
            if self.enemy_filed.is_valid_shot(row, col):
                super().shot(row, col)

    @pyqtSlot(int, int)
    def _on_other_player_shot(self, x, y):
        is_hit = super()._on_other_player_shot(x, y)
        # если противник промахнулся, то ход переходит к нам
        if not is_hit:
            self.my_shot = not self.my_shot

    @pyqtSlot(bool)
    def _on_shot_status(self, status):
        super()._on_shot_status(status)
        # если мы про махнулись, то мы не можем ходить, пока противник не промахнется
        if not status:
            self.my_shot = not self.my_shot
            # нужно некотрое время, чтобы обновить игровое поле перед тем как снова начать слушать очередь
            self._do_action_with_delay(self.client.wait_shot, 1000)


class BotPlayer(Player):

    def __init__(self, player_field, enemy_filed):
        super().__init__(player_field, enemy_filed)

    def find_enemy(self):
        super().find_enemy()
        # если первый ход не наш, то ждем первый выстрел от противника
        if not self.my_shot:
            self.client.wait_shot()
        # иначе стреляем сами
        else:
            self.shot()

    def shot(self):
        if self.my_shot:
            row, col = self._get_random_coordinats()
            while not self.enemy_filed.is_valid_shot(row, col):
                row, col = self._get_random_coordinats()
            super().shot(row, col)

    @pyqtSlot(int, int)
    def _on_other_player_shot(self, x, y):
        is_hit = super()._on_other_player_shot(x, y)
        # если противник промахнулся, то ход переходит к нам
        if not is_hit:
            self.my_shot = not self.my_shot
            self._do_action_with_delay(self.shot, 1000)

    @pyqtSlot(bool)
    def _on_shot_status(self, status):
        super()._on_shot_status(status)
        # если мы про махнулись, то мы не можем ходить, пока противник не промахнется
        if not status:
            self.my_shot = not self.my_shot
            # нужно некотрое время, чтобы обновить игровое поле перед тем как снова начать слушать очередь
            self._do_action_with_delay(self.client.wait_shot, 1000)
        else:
            self._do_action_with_delay(self.shot, 1000)

    def _get_random_coordinats(self):
        return random.randint(0, 9), random.randint(0, 9)

