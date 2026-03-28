from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit,
    QLabel, QFileDialog, QProgressBar, QComboBox, QHBoxLayout
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from gui.style import load_pixel_font
from embed import StegoEmbed
import os
import shutil
import tempfile


class EmbedWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, video, payload, output_format, is_file=False):
        super().__init__()
        self.video = video
        self.payload = payload
        self.output_format = output_format.lower()
        self.is_file = is_file

        temp_dir = tempfile.gettempdir()
        self.temp_output = os.path.join(temp_dir, f"temp_stego.{self.output_format}")

    def run(self):
        try:
            obj = StegoEmbed(
                self.video,
                self.payload,
                None,
                None,
                self.temp_output
            )

            result = obj.run_embedding(is_file=self.is_file)

            self.finished.emit({
                "result": result,
                "path": self.temp_output,
                "format": self.output_format
            })

        except Exception as e:
            self.error.emit(str(e))


class EmbedPage(QWidget):
    def __init__(self, go_back):
        super().__init__()

        self.video_path = ""
        self.file_path = None
        self.output_path = None
        self.output_format = "avi"
        self.mode = "TEXT"

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        title = QLabel("EMBED")
        title.setFont(load_pixel_font(14))
        title.setAlignment(Qt.AlignCenter)

        btn_select = QPushButton("Select Video")
        btn_select.setFont(load_pixel_font(10))
        btn_select.clicked.connect(self.choose_video)

        self.file_label = QLabel("No file")
        self.file_label.setAlignment(Qt.AlignCenter)

        self.btn_text = QPushButton("TEXT")
        self.btn_file = QPushButton("FILE")

        for b in [self.btn_text, self.btn_file]:
            b.setFont(load_pixel_font(10))
            b.setFixedWidth(120)

        self.btn_text.clicked.connect(lambda: self.set_mode("TEXT"))
        self.btn_file.clicked.connect(lambda: self.set_mode("FILE"))

        mode_layout = QHBoxLayout()
        mode_layout.setAlignment(Qt.AlignCenter)
        mode_layout.addWidget(self.btn_text)
        mode_layout.addWidget(self.btn_file)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Message")
        self.input.setStyleSheet("""
        QLineEdit {
            background-color: white;
            color: black;
            border: 1px solid black;
            padding: 6px;
        }
        """)

        self.file_btn = QPushButton("Select File")
        self.file_btn.setFont(load_pixel_font(10))
        self.file_btn.clicked.connect(self.choose_payload)
        self.file_btn.setVisible(False)

        self.payload_label = QLabel("")
        self.payload_label.setAlignment(Qt.AlignCenter)
        self.payload_label.setVisible(False)

        format_label = QLabel("Output Format")
        format_label.setFont(load_pixel_font(8))
        format_label.setAlignment(Qt.AlignCenter)

        self.format_box = QComboBox()
        self.format_box.addItems(["AVI", "MP4"])
        self.format_box.setCurrentText("AVI")

        self.progress = QProgressBar()
        self.progress.setVisible(False)

        run = QPushButton("RUN")
        run.setFont(load_pixel_font(10))
        run.clicked.connect(self.run_embed)

        self.download_btn = QPushButton("DOWNLOAD")
        self.download_btn.setFont(load_pixel_font(10))
        self.download_btn.setVisible(False)
        self.download_btn.clicked.connect(self.save_file)

        self.result = QLabel("")
        self.result.setAlignment(Qt.AlignCenter)

        back = QPushButton("BACK")
        back.setFont(load_pixel_font(10))
        back.clicked.connect(go_back)

        layout.addWidget(title)
        layout.addWidget(btn_select)
        layout.addWidget(self.file_label)
        layout.addLayout(mode_layout)
        layout.addWidget(self.input)
        layout.addWidget(self.file_btn)
        layout.addWidget(self.payload_label)
        layout.addWidget(format_label)
        layout.addWidget(self.format_box)
        layout.addWidget(self.progress)
        layout.addWidget(run)
        layout.addWidget(self.download_btn)
        layout.addWidget(self.result)
        layout.addSpacing(10)
        layout.addWidget(back)

        self.setLayout(layout)

        self.set_mode("TEXT")

    def set_mode(self, mode):
        self.mode = mode

        if mode == "TEXT":
            self.input.setVisible(True)
            self.file_btn.setVisible(False)
            self.payload_label.setVisible(False)

            self.btn_text.setStyleSheet("background-color: white; color: black;")
            self.btn_file.setStyleSheet("")
        else:
            self.input.setVisible(False)
            self.file_btn.setVisible(True)
            self.payload_label.setVisible(True)

            self.btn_file.setStyleSheet("background-color: white; color: black;")
            self.btn_text.setStyleSheet("")

    def choose_video(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video",
            "",
            "Video Files (*.avi *.mp4)"
        )
        if file:
            self.video_path = file
            self.file_label.setText(os.path.basename(file))

    def choose_payload(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file:
            self.file_path = file
            self.payload_label.setText(os.path.basename(file))

    def run_embed(self):
        if not self.video_path:
            self.result.setText("Select video first")
            return

        payload = None
        is_file = False

        if self.mode == "TEXT":
            if not self.input.text():
                self.result.setText("Enter message")
                return
            payload = self.input.text()
        else:
            if not self.file_path:
                self.result.setText("Select file")
                return
            payload = self.file_path
            is_file = True

        self.output_format = self.format_box.currentText().lower()

        self.download_btn.setVisible(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.result.setText("")

        self.start_progress()

        self.thread = EmbedWorker(
            self.video_path,
            payload,
            self.output_format,
            is_file
        )
        self.thread.finished.connect(self.finish)
        self.thread.error.connect(self.show_error)
        self.thread.start()

    def start_progress(self):
        self.val = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_bar)
        self.timer.start(80)

    def update_bar(self):
        if self.val < 90:
            self.val += 1
            self.progress.setValue(self.val)

    def finish(self, data):
        self.timer.stop()
        self.progress.setValue(100)

        self.output_path = data["path"]
        self.output_format = data["format"]

        result = data["result"]

        self.result.setText(
            f"Format: {self.output_format.upper()}\n"
            f"PSNR: {result['psnr']:.2f}"
        )

        self.download_btn.setVisible(True)

    def save_file(self):
        if not self.output_path:
            return

        ext = self.output_format
        default_name = f"stego_output.{ext}"

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            default_name,
            f"{ext.upper()} File (*.{ext})"
        )

        if not path:
            return

        if not path.lower().endswith(f".{ext}"):
            path += f".{ext}"

        shutil.copyfile(self.output_path, path)

        try:
            os.remove(self.output_path)
        except:
            pass

        self.result.setText(f"Saved to:\n{path}")

    def show_error(self, msg):
        if hasattr(self, "timer"):
            self.timer.stop()
        self.progress.setVisible(False)
        self.result.setText(msg)