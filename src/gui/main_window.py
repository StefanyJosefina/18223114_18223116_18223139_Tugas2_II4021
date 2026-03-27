from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from gui.splash_page import SplashPage
from gui.menu_page import MenuPage
from gui.embed_ui import EmbedPage
from gui.extract_ui import ExtractPage
from gui.histogram_ui import HistogramPage
from gui.style import STYLE


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stego Pixel")
        self.setMinimumSize(800, 500)
        self.setStyleSheet(STYLE)

        self.bg = QLabel(self)
        self.bg.setPixmap(QPixmap("assets/BGPIXELGAME.jpg"))
        self.bg.setScaledContents(True)

        self.stack = QStackedWidget(self)

        self.splash = SplashPage(self.go_menu)
        self.menu = MenuPage(self.go_embed, self.go_extract, self.go_hist, self.go_splash)
        self.embed = EmbedPage(self.go_menu)
        self.extract = ExtractPage(self.go_menu)
        self.hist = HistogramPage(self.go_menu)

        self.stack.addWidget(self.splash)
        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.embed)
        self.stack.addWidget(self.extract)
        self.stack.addWidget(self.hist)

        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)

        self.stack.setCurrentIndex(0)

    def resizeEvent(self, event):
        self.bg.setGeometry(0, 0, self.width(), self.height())

    def go_menu(self):
        self.stack.setCurrentIndex(1)

    def go_embed(self):
        self.stack.setCurrentIndex(2)

    def go_extract(self):
        self.stack.setCurrentIndex(3)

    def go_hist(self):
        self.stack.setCurrentIndex(4)

    def go_splash(self):
        self.stack.setCurrentIndex(0)