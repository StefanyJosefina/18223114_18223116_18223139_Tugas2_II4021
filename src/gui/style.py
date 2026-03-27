from PyQt5.QtGui import QFontDatabase, QFont
import os

STYLE = """
QWidget {
    background-color: transparent;
    color: white;
}

QPushButton {
    background-color: #333;
    border: 1px solid #aaa;
    padding: 6px;
}

QPushButton:hover {
    background-color: #555;
}

QLineEdit {
    background-color: #222;
    border: 1px solid #555;
    padding: 5px;
}
"""

def load_pixel_font(size=12):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    font_path = os.path.join(base_path, "assets", "PressStart2P.ttf")

    font_id = QFontDatabase.addApplicationFont(font_path)

    if font_id != -1:
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            return QFont(families[0], size)

    return QFont("Courier", size)