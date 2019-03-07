from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor


class BattleField(QWidget):

    # возможные состояния клеток
    EMPTY_CELL = 0
    SHIP_CELL = 1
    HIT_CELL = 2
    DEAD_CELL = 3
    MISS_CELL = 4
    FREE_CELL = 5

    def __init__(self):
        super(BattleField, self).__init__()
        self.state = []
        self.setup_UI()

    def setup_UI(self):
        """
        Инициализация интерфейса поля морского боя
        """
        cell_size = 32
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setRowCount(10)

        horizontal_header = QHeaderView(Qt.Horizontal)
        horizontal_header.setDefaultSectionSize(cell_size)
        self.table.setHorizontalHeader(horizontal_header)
        self.table.setHorizontalHeaderLabels([c for c in "АБВГДЕЖЗИК"])

        for r in range(10):
            for c in range(10):
                self.table.setItem(r, c, QTableWidgetItem())

        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.cellClicked.connect(self.cell_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.init_ships()

    def init_ships(self):
        """
        Случайная расстановка кораблей и их отрисовка
        """
        # TODO изменить способ инициализации кораблей
        self.state = [
            [0,1,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,1,0],
            [0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,1],
            [0,0,0,1,0,0,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,1,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0],
            [1,1,0,0,0,0,0,1,1,1],
            [0,0,0,0,1,0,0,0,0,0],
        ]

        for y, line in enumerate(self.state):
            for x, cell in enumerate(line):
                if cell == 1:
                    self.table.item(y, x).setBackground(QColor(100, 100, 150))


    @pyqtSlot()
    def cell_clicked(self):
        """
        Вызывается при нажатии на клетку игрового поля
        """
        item = self.table.currentItem()
        print(item.row(), item.column())

