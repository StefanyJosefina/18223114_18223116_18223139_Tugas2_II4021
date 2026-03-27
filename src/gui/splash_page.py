from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class SplashPage(QWidget):
    def __init__(self, go_next):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("STEGO PIXEL GAME")
        title.setStyleSheet("font-size: 24px;")

        btn = QPushButton("▶ PLAY")
        btn.clicked.connect(go_next)

        layout.addWidget(title)
        layout.addWidget(btn)

        self.setLayout(layout)