from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QProgressBar, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer
from gui.style import load_pixel_font
from extract import StegoExtract
import os


class ExtractPage(QWidget):
    def __init__(self, go_back):
        super().__init__()

        self.video_path = ""

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        title = QLabel("EXTRACT")
        title.setFont(load_pixel_font(14))
        title.setAlignment(Qt.AlignCenter)

        btn_select = QPushButton("Select Video")
        btn_select.setFont(load_pixel_font(10))
        btn_select.clicked.connect(self.choose_file)

        self.file_label = QLabel("No file")
        self.file_label.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setVisible(False)

        run = QPushButton("RUN")
        run.setFont(load_pixel_font(10))
        run.clicked.connect(self.run_extract)

        self.result_title = QLabel("")
        self.result_title.setAlignment(Qt.AlignCenter)
        self.result_title.setFont(load_pixel_font(10))

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setPlaceholderText("Extracted message will appear here")
        self.result_box.setStyleSheet("""
        QTextEdit {
            background-color: white;
            color: black;
            border: 1px solid black;
            padding: 6px;
        }
        """)

        back = QPushButton("BACK")
        back.setFont(load_pixel_font(10))
        back.clicked.connect(go_back)

        layout.addWidget(title)
        layout.addWidget(btn_select)
        layout.addWidget(self.file_label)
        layout.addWidget(self.progress)
        layout.addWidget(run)
        layout.addWidget(self.result_title)
        layout.addWidget(self.result_box)
        layout.addSpacing(10)
        layout.addWidget(back)

        self.setLayout(layout)

    def choose_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Video")
        if file:
            self.video_path = file
            self.file_label.setText(os.path.basename(file))

    def run_extract(self):
        if not self.video_path:
            self.result_title.setText("")
            self.result_box.clear()
            self.result_box.setPlaceholderText("Please select a video first")
            return

        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.result_title.setText("")
        self.result_box.clear()
        self.result_box.setPlaceholderText("Extracting hidden message...")

        self.start_progress()
        QTimer.singleShot(10, self.finish_extract)

    def start_progress(self):
        self.val = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_bar)
        self.timer.start(80)

    def update_bar(self):
        if self.val < 90:
            self.val += 1
            self.progress.setValue(self.val)

    def finish_extract(self):
        try:
            obj = StegoExtract(self.video_path)
            res = obj.extraction()

            self.timer.stop()
            self.progress.setValue(100)

            if res["type"] == "teks":
                self.result_title.setText("HIDDEN MESSAGE")
                self.result_box.setText(res["data"])
                self.adjust_textbox_height()
            else:
                self.result_title.setText("FILE EXTRACTED")
                self.result_box.setText("Extracted file has been recovered successfully.")
                self.adjust_textbox_height()

        except Exception as e:
            self.timer.stop()
            self.result_title.setText("")
            self.result_box.clear()
            self.result_box.setPlaceholderText(str(e))

    def adjust_textbox_height(self):
        doc_height = self.result_box.document().size().height()
        self.result_box.setFixedHeight(int(doc_height + 10))