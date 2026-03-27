from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from extract import StegoExtract

class ExtractPage(QWidget):
    def __init__(self, go_back):
        super().__init__()

        self.video_path = ""

        layout = QVBoxLayout()

        layout.addWidget(QLabel("MODE: EXTRACT"))

        back = QPushButton("⬅ BACK")
        back.clicked.connect(go_back)

        btn = QPushButton("Pilih Video")
        btn.clicked.connect(self.choose)

        self.label = QLabel("No file")

        run = QPushButton("RUN")
        run.clicked.connect(self.run_extract)

        self.result = QLabel("")

        layout.addWidget(back)
        layout.addWidget(btn)
        layout.addWidget(self.label)
        layout.addWidget(run)
        layout.addWidget(self.result)

        self.setLayout(layout)

    def choose(self):
        file, _ = QFileDialog.getOpenFileName()
        self.video_path = file
        self.label.setText(file)

    def run_extract(self):
        obj = StegoExtract(self.video_path)
        res = obj.extraction()

        if res["type"] == "teks":
            self.result.setText(res["data"])
        else:
            self.result.setText("File extracted")