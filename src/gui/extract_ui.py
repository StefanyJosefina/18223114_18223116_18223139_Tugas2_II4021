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
        self.extracted_file_path = None

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

        self.download_btn = QPushButton("DOWNLOAD FILE")
        self.download_btn.setFont(load_pixel_font(10))
        self.download_btn.setVisible(False)
        self.download_btn.clicked.connect(self.save_file)

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
        layout.addWidget(self.download_btn)
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
            self.result_box.setText("Please select a video first")
            return

        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.result_box.setText("Extracting...")
        self.result_title.setText("")
        self.download_btn.setVisible(False)

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
            import glob
            import shutil
            import tempfile

            before_files = set(glob.glob("*"))

            obj = StegoExtract(self.video_path)
            res = obj.extraction()

            self.timer.stop()
            self.progress.setValue(100)

            after_files = set(glob.glob("*"))
            new_files = list(after_files - before_files)

            data_type = res.get("type", "").lower()

            if data_type in ["text", "teks"]:
                self.result_title.setText("HIDDEN MESSAGE")
                self.result_box.setText(res.get("data", ""))
                self.adjust_textbox_height()

            else:
                self.result_title.setText("FILE EXTRACTED")
                self.result_box.setText("Click download to save the extracted file")

                if new_files:
                    created_file = new_files[0]

                    temp_dir = tempfile.gettempdir()
                    temp_path = os.path.join(temp_dir, os.path.basename(created_file))

                    shutil.move(created_file, temp_path)

                    self.extracted_file_path = temp_path
                    self.download_btn.setVisible(True)

                self.adjust_textbox_height()

        except Exception as e:
            self.timer.stop()
            self.result_box.setText(str(e))

    def save_file(self):
        if not self.extracted_file_path:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            os.path.basename(self.extracted_file_path)
        )

        if not path:
            return

        import shutil
        shutil.copy(self.extracted_file_path, path)

        self.result_box.setText(f"Saved to:\n{path}")

    def adjust_textbox_height(self):
        doc_height = self.result_box.document().size().height()
        self.result_box.setFixedHeight(int(doc_height + 10))