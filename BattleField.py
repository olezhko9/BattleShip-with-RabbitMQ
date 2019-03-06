from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView
from PyQt5.QtCore import Qt

class BattleField(QWidget):

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
        cell_size = 32
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setRowCount(10)

        horizontal_header = QHeaderView(Qt.Horizontal)
        horizontal_header.setDefaultSectionSize(cell_size)
        self.table.setHorizontalHeader(horizontal_header)
        self.table.setHorizontalHeaderLabels([c for c in "АБВГДЕЖЗИК"])

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

