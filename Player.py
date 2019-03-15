from BattleField import BattleField
from client import BattleShipClient

class Player:
    def __init__(self, player_field: BattleField, enemy_filed):
        self.my_shot = False
        self.last_hit_success = False
        self.enemy_queue = None

        self.enemy_filed = enemy_filed
        self.player_field = player_field
        self.client = BattleShipClient()

        self.enemy_filed.table.cellClicked.connect(self.shot)
        self.client.make_shot_signal.connect(self._on_other_player_shot)
        self.client.shot_status_signal.connect(self._on_shot_status)

    def find_enemy(self):
        """
        Обращается к серверу для получения очереди соперника и информации о первом ходе.
        """
        self.client.find_enemy()
        self.enemy_queue = self.client.response.get('enemy_queue')
        self.my_shot = self.client.response.get('first_hit')
        # если первый ход не наш, то ждем первый выстрел от противника
        if not self.my_shot:
            self.client.wait_shot()

    def shot(self):
        print('my shot:', self.my_shot)
        """
        Вызывается при нажатии на клетку игрового поля.
        Если ход игрока, то проверяет выбранну клетку на допустимость выстрела.
        В случае успеха отправляет координаты выстрела второму игроку.
        """
        if self.my_shot:
            item = self.enemy_filed.table.currentItem()
            x = item.row()
            y = item.column()
            if self.enemy_filed.is_valid_shot(x, y):
                print("Человек выстрелил по", x, y)
                self.client.send_shot(x, y)
                # self.enemy_filed.shooted.emit()
                # self.enemy_filed.change_field_after_shot(x, y)

    def _on_other_player_shot(self, x, y):
        # меняем очередь хода
        is_hit = self.player_field.field[x][y] == BattleField.SHIP_CELL
        self.client.send_shot_status(is_hit)
        if not is_hit:
            self.my_shot = not self.my_shot

    def _on_shot_status(self, is_hit):
        if not is_hit:
            self.my_shot = not self.my_shot
