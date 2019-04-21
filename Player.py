from BattleField import BattleField
from client import BattleShipClient
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
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
        pass

    # @abstractmethod
    # def shot(self, row, col):
    #     """
    #     Вызывается при нажатии на клетку игрового поля.
    #     Если ход игрока, то проверяет выбранну клетку на допустимость выстрела.
    #     В случае успеха отправляет координаты выстрела второму игроку.
    #     """
        # self.last_shot = row, col
        # self.client.send_shot(row, col)

    @abstractmethod
    def _on_other_player_shot(self, x, y):
        pass

    @abstractmethod
    def _on_shot_status(self, status):
        pass


class ActivePlayer(Player):

    def __init__(self, player_field, enemy_filed):
        super().__init__(player_field, enemy_filed)
        self.enemy_filed.table.cellClicked.connect(self.shot)

    def find_enemy(self):
        """
        Обращается к серверу для получения очереди соперника и информации о первом ходе.
        """
        self.client.find_enemy()
        self.enemy_queue = self.client.response.get('enemy_queue')
        self.my_shot = self.client.response.get('first_hit')
        self.shot_status_changed.emit(self.my_shot)
        # если первый ход не наш, то ждем первый выстрел от противника
        if not self.my_shot:
            self.client.wait_shot()

    def shot(self, row, col):
        """
        Реальный игрок получает координаты выстрела от сигнала cellClicked
        """
        if self.my_shot:
            if self.enemy_filed.is_valid_shot(row, col):
                super().shot(row, col)

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
        # если противник промахнулся, то ход переходит к нам
        if not is_hit:
            self.my_shot = not self.my_shot

    def _on_shot_status(self, status):
        """
        Вызывается при получении информации от соперника о промахе или попадании.
        :param: is_hit - мы попали?
        """
        self.enemy_filed.change_field_after_shot(*self.last_shot, status)
        self.shot_status_changed.emit(status)
        # если мы про махнулись, то мы не можем ходить, пока противник не промахнется
        if not status:
            self.my_shot = not self.my_shot
            # нужно некотрое время, чтобы обновить игровое поле перед тем как снова начать слушать очередь
            self.shot_process_timer = QTimer()
            self.shot_process_timer.setSingleShot(True)
            self.shot_process_timer.timeout.connect(self.client.wait_shot)
            self.shot_process_timer.start(500)


class BotPlayer(Player):

    def __init__(self, player_field, enemy_filed):
        super().__init__(player_field, enemy_filed)

    def find_enemy(self):
        """
        Обращается к серверу для получения очереди соперника и информации о первом ходе.
        """
        self.client.find_enemy()
        self.enemy_queue = self.client.response.get('enemy_queue')
        self.my_shot = self.client.response.get('first_hit')
        self.shot_status_changed.emit(self.my_shot)
        # если первый ход не наш, то ждем первый выстрел от противника
        if not self.my_shot:
            self.client.wait_shot()
        else:
            self.shot()

    def shot(self):
        if self.my_shot:
            row, col = self._get_random_coordinats()
            while not self.enemy_filed.is_valid_shot(row, col):
                row, col = self._get_random_coordinats()
            self.last_shot = row, col
            self.client.send_shot(row, col)

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

        # если противник промахнулся, то ход переходит к нам
        if not is_hit:
            self.my_shot = not self.my_shot
            print("My turn:", self.my_shot)

            self.shot_process_timer = QTimer()
            self.shot_process_timer.setSingleShot(True)
            self.shot_process_timer.timeout.connect(self.shot)
            self.shot_process_timer.start(1000)

    def _on_shot_status(self, status):
        """
        Вызывается при получении информации от соперника о промахе или попадании.
        :param: is_hit - мы попали?
        """
        self.enemy_filed.change_field_after_shot(*self.last_shot, status)
        self.shot_status_changed.emit(status)

        # если мы про махнулись, то мы не можем ходить, пока противник не промахнется
        if not status:
            self.my_shot = not self.my_shot
            # нужно некотрое время, чтобы обновить игровое поле перед тем как снова начать слушать очередь
            self.shot_process_timer = QTimer()
            self.shot_process_timer.setSingleShot(True)
            self.shot_process_timer.timeout.connect(self.client.wait_shot)
            self.shot_process_timer.start(1000)
        else:
            print("My turn:", self.my_shot)

            self.shot_process_timer = QTimer()
            self.shot_process_timer.setSingleShot(True)
            self.shot_process_timer.timeout.connect(self.shot)
            self.shot_process_timer.start(1000)

    def _get_random_coordinats(self):
        return random.randint(0, 9), random.randint(0, 9)

