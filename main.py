from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont
import sys
from BattleField import BattleField
from Player import Player


class BattleShip(QMainWindow):
    """
    Класс приложения, необходимый для инициализации интерфейса и запуска игры
    """
    def __init__(self):
        super().__init__()
        # Создаем 2 поля боя
        self.myBattleField = BattleField(enemy_field=False)
        self.enemyBattleField = BattleField(enemy_field=True)
        # Инициализируем интерфейс
        self.setup_UI()
        # Запускаем игру
        self.battle_loop()

    def setup_UI(self):
        """
        Инициализация интерфейса
        """
        self.title = 'Battle Ship'
        self.left = 600
        self.top = 400
        self.width = 808
        self.height = 390
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.message_area = QLabel("Игра начинается!")
        self.message_area.setFont(QFont("Times", 14, QFont.Normal))
        self.start_button = QPushButton('Старт')

        battle_field_layout = QHBoxLayout()
        battle_field_layout.addWidget(self.myBattleField)
        battle_field_layout.addWidget(self.enemyBattleField)
        battle_field_layout.addWidget(self.start_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(battle_field_layout)
        main_layout.addWidget(self.message_area)

        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(main_layout)
        self.show()

    def battle_loop(self):
        """
        Глаавный игровой цикл
        """
        self.game_over = False
        # Инициализируем игроков
        self.player = Player(self.enemyBattleField)
        self.start_button.clicked.connect(self.player.find_enemy)

        # Каждый игрок обрабатывает выстрелы
        self.enemyBattleField.shooted.connect(self.on_shot)
        self.myBattleField.shooted.connect(self.on_shot)

        if self.player.my_shot:
            self.message_area.setText("Ваш ход!")
        else:
            self.message_area.setText("Ход противника")


    def on_shot(self):
        """
        Функция вызывается после выстрела одного из игроков
        """
        # если бот попал, то пусть стреляет еще раз
        # if self.battle_bot.last_hit_success:
        #     self.battle_bot.shot()
        # # если мы промахнулись, то ход переходит боту
        # elif not self.real_player.last_hit_success:
        #     BattleShipPlayer.next_player(self.real_player, self.battle_bot)
        #     self.battle_bot.shot()
        # self.message_area.setText("Очередь - моя: {}, противника: {}".format(self.real_player.my_shot, self.battle_bot.my_shot))

        self.is_game_over()

    def is_game_over(self):
        max_hits = 20
        # если 20 клеток помечены, как попадание, то все корабли потоплены
        if self.myBattleField.count_if(BattleField.HIT_CELL) == max_hits or \
                self.enemyBattleField.count_if(BattleField.HIT_CELL) == max_hits:
            self.game_over = True
            print("Game over")
            self.message_area.setText("Игра окончена!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BattleShip()
    # window.show()
    sys.exit(app.exec_())
