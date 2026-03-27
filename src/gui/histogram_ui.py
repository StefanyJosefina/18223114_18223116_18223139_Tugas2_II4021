from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog
import cv2
import matplotlib.pyplot as plt

class HistogramPage(QWidget):
    def __init__(self, go_back):
        super().__init__()

        layout = QVBoxLayout()

        back = QPushButton("⬅ BACK")
        back.clicked.connect(go_back)

        btn = QPushButton("SHOW HISTOGRAM")
        btn.clicked.connect(self.show)

        layout.addWidget(back)
        layout.addWidget(btn)

        self.setLayout(layout)

    def show(self):
        file, _ = QFileDialog.getOpenFileName()

        cap = cv2.VideoCapture(file)
        ret, frame = cap.read()

        colors = ('r','g','b')
        for i, c in enumerate(colors):
            hist = cv2.calcHist([frame],[i],None,[256],[0,256])
            plt.plot(hist, color=c)

        plt.show()
        cap.release()