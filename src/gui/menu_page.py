from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class MenuPage(QWidget):
    def __init__(self, go_embed, go_extract, go_hist):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("SELECT MODE")
        title.setStyleSheet("font-size: 18px;")

        btn1 = QPushButton("EMBED")
        btn2 = QPushButton("EXTRACT")
        btn3 = QPushButton("HISTOGRAM")

        btn1.clicked.connect(go_embed)
        btn2.clicked.connect(go_extract)
        btn3.clicked.connect(go_hist)

        layout.addWidget(title)
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)

        self.setLayout(layout)