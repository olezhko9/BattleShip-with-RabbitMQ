from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont
import sys
from BattleField import BattleField
from BattleShipPlayer import RealPlayer, BotPlayer


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

        self.message_area = QLabel("Ваш ход!")
        self.message_area.setFont(QFont("Times", 14, QFont.Normal))

        battle_field_layout = QHBoxLayout()
        battle_field_layout.addWidget(self.myBattleField)
        battle_field_layout.addWidget(self.enemyBattleField)

        main_layout = QVBoxLayout()
        main_layout.addLayout(battle_field_layout)
        main_layout.addWidget(self.message_area)

        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(main_layout)

    def battle_loop(self):
        # Инициализируем бота
        self.battle_bot = BotPlayer(self.myBattleField)
        self.real_player = RealPlayer(self.enemyBattleField)

        [print(self.battle_bot.shot()) for i in range(50)]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BattleShip()
    window.show()
    sys.exit(app.exec_())
