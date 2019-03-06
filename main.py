from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout
from BattleField import BattleField
import sys


class BattleShip(QMainWindow):

    def __init__(self):
        super().__init__()

        self.title = 'Battle Ship'
        self.left = 600
        self.top = 400
        self.width = 900
        self.height = 600
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setup_UI()

    def setup_UI(self):
        self.battleField = BattleField()

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.battleField)
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BattleShip()
    window.show()
    sys.exit(app.exec_())
