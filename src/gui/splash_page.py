from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QSize
from gui.style import load_pixel_font
import os


class SplashPage(QWidget):
    def __init__(self, go_next):
        super().__init__()

        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        gif_path = os.path.join(base_path, "assets", "PUYOJALAN.gif")

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(25)

        self.title = QLabel("STEGO PIXEL")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(load_pixel_font(20))

        self.char = QLabel()
        self.char.setAlignment(Qt.AlignCenter)

        self.movie = QMovie(gif_path)
        self.movie.setScaledSize(QSize(120, 120))
        self.char.setMovie(self.movie)
        self.movie.start()

        self.play_btn = QPushButton("PLAY")
        self.play_btn.setFont(load_pixel_font(12))
        self.play_btn.setFixedWidth(160)
        self.play_btn.clicked.connect(go_next)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.play_btn)
        btn_layout.addStretch()

        main_layout.addWidget(self.title)
        main_layout.addWidget(self.char)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)