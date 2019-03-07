from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel
from BattleField import BattleField
import sys


class BattleShip(QMainWindow):
    """
    Класс приложения, необходимый для инициализации интерфейса и запуска игры
    """
    def __init__(self):
        super().__init__()
        self.title = 'Battle Ship'
        self.left = 600
        self.top = 400
        self.width = 808
        self.height = 380
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setup_UI()

    def setup_UI(self):
        """
        Инициализация интерфейса
        """
        self.myBattleField = BattleField(enemy_field=False)
        self.enemyBattleField = BattleField(enemy_field=True)

        self.message_area = QLabel("Здесь будут выводиться сообщения игры.")
        battle_field_layout = QHBoxLayout()
        battle_field_layout.addWidget(self.myBattleField)
        battle_field_layout.addWidget(self.enemyBattleField)

        main_layout = QVBoxLayout()
        main_layout.addLayout(battle_field_layout)
        main_layout.addWidget(self.message_area)

        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BattleShip()
    window.show()
    sys.exit(app.exec_())
