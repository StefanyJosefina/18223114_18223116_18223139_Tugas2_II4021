from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout
from gui.splash_page import SplashPage
from gui.menu_page import MenuPage
from gui.embed_ui import EmbedPage
from gui.extract_ui import ExtractPage
from gui.histogram_ui import HistogramPage
from gui.style import STYLE

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stego Pixel Game")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet(STYLE)

        self.stack = QStackedWidget()

        self.splash = SplashPage(self.go_menu)
        self.menu = MenuPage(self.go_embed, self.go_extract, self.go_hist)
        self.embed = EmbedPage(self.go_menu)
        self.extract = ExtractPage(self.go_menu)
        self.hist = HistogramPage(self.go_menu)

        self.stack.addWidget(self.splash)
        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.embed)
        self.stack.addWidget(self.extract)
        self.stack.addWidget(self.hist)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.stack.setCurrentIndex(0)

    def go_menu(self):
        self.stack.setCurrentIndex(1)

    def go_embed(self):
        self.stack.setCurrentIndex(2)

    def go_extract(self):
        self.stack.setCurrentIndex(3)

    def go_hist(self):
        self.stack.setCurrentIndex(4)