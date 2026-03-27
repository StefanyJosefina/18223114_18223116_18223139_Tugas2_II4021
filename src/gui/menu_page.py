from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from gui.style import load_pixel_font


class MenuPage(QWidget):
    def __init__(self, go_embed, go_extract, go_hist, go_back):
        super().__init__()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        title = QLabel("SELECT MODE")
        title.setFont(load_pixel_font(14))
        title.setAlignment(Qt.AlignCenter)

        btn1 = QPushButton("EMBED")
        btn2 = QPushButton("EXTRACT")
        btn3 = QPushButton("HISTOGRAM")
        back_btn = QPushButton("BACK")

        for b in [btn1, btn2, btn3, back_btn]:
            b.setFont(load_pixel_font(10))

        btn1.clicked.connect(go_embed)
        btn2.clicked.connect(go_extract)
        btn3.clicked.connect(go_hist)
        back_btn.clicked.connect(go_back)

        layout.addWidget(title)
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)
        layout.addSpacing(10)
        layout.addWidget(back_btn)

        self.setLayout(layout)