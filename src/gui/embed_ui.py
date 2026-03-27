from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit,
    QLabel, QFileDialog, QProgressBar, QComboBox
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

    def __init__(self, video, msg, output_format):
        super().__init__()
        self.video = video
        self.msg = msg
        self.output_format = output_format.lower()

        temp_dir = tempfile.gettempdir()
        self.temp_output = os.path.join(temp_dir, f"temp_stego.{self.output_format}")

    def run(self):
        try:
            obj = StegoEmbed(
                self.video,
                self.msg,
                None,
                None,
                self.temp_output
            )

            result = obj.run_embedding()

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
        self.output_path = None
        self.output_format = "avi"

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        title = QLabel("EMBED")
        title.setFont(load_pixel_font(14))
        title.setAlignment(Qt.AlignCenter)

        btn_select = QPushButton("Select Video")
        btn_select.setFont(load_pixel_font(10))
        btn_select.clicked.connect(self.choose_file)

        self.file_label = QLabel("No file")
        self.file_label.setAlignment(Qt.AlignCenter)

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

        format_label = QLabel("Output Format")
        format_label.setFont(load_pixel_font(8))
        format_label.setAlignment(Qt.AlignCenter)

        self.format_box = QComboBox()
        self.format_box.addItems(["AVI", "MP4"])
        self.format_box.setCurrentText("AVI")
        self.format_box.setStyleSheet("""
        QComboBox {
            background-color: white;
            color: black;
            border: 1px solid black;
            padding: 4px;
        }
        QComboBox QAbstractItemView {
            background-color: white;
            color: black;
            selection-background-color: #dcdcdc;
            selection-color: black;
        }
        """)

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
        layout.addWidget(self.input)
        layout.addWidget(format_label)
        layout.addWidget(self.format_box)
        layout.addWidget(self.progress)
        layout.addWidget(run)
        layout.addWidget(self.download_btn)
        layout.addWidget(self.result)
        layout.addSpacing(10)
        layout.addWidget(back)

        self.setLayout(layout)

    def choose_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video",
            "",
            "Video Files (*.avi *.mp4)"
        )
        if file:
            self.video_path = file
            self.file_label.setText(os.path.basename(file))

    def run_embed(self):
        if not self.video_path or not self.input.text():
            self.result.setText("Input belum lengkap")
            return

        self.output_path = None
        self.output_format = self.format_box.currentText().lower()

        self.download_btn.setVisible(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.result.setText("")

        self.start_progress()

        self.thread = EmbedWorker(
            self.video_path,
            self.input.text(),
            self.output_format
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