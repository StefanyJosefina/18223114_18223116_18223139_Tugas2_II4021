from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit,
    QLabel, QFileDialog, QProgressBar
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from embed import StegoEmbed
import os


class EmbedWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, video, msg, key, stego, output):
        super().__init__()
        self.video = video
        self.msg = msg
        self.key = key
        self.stego = stego
        self.output = output

    def run(self):
        try:
            obj = StegoEmbed(
                self.video,
                self.msg,
                self.key,
                self.stego,
                output_path=self.output
            )

            result = obj.run_embedding(
                is_file=False,
                encrypt=bool(self.key),
                use_random=bool(self.stego)
            )

            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class EmbedPage(QWidget):
    def __init__(self, go_back):
        super().__init__()

        self.video_path = ""

        layout = QVBoxLayout()

        layout.addWidget(QLabel("MODE: EMBED"))

        back_btn = QPushButton("BACK")
        back_btn.clicked.connect(go_back)
        layout.addWidget(back_btn)

        btn_file = QPushButton("Pilih Video")
        btn_file.clicked.connect(self.choose_file)
        layout.addWidget(btn_file)

        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)

        self.input_msg = QLineEdit()
        self.input_msg.setPlaceholderText("Masukkan pesan rahasia")
        layout.addWidget(self.input_msg)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.loading_label = QLabel("")
        layout.addWidget(self.loading_label)

        run_btn = QPushButton("RUN EMBED")
        run_btn.clicked.connect(self.run_embed)
        layout.addWidget(run_btn)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def choose_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih Video",
            "",
            "Video Files (*.avi *.mp4)"
        )

        if file:
            self.video_path = file
            self.file_label.setText(os.path.basename(file))

    def run_embed(self):
        if not self.video_path:
            self.result_label.setText("Pilih video dulu")
            return

        if not self.input_msg.text():
            self.result_label.setText("Pesan kosong")
            return

        save_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Simpan Stego Video",
            "stego_video.avi",
            "AVI Video (*.avi);;MP4 Video (*.mp4)"
        )

        if not save_path:
            return

        ext = os.path.splitext(save_path)[1]

        if not ext:
            if "mp4" in selected_filter.lower():
                save_path += ".mp4"
            else:
                save_path += ".avi"

        self.progress.setValue(0)
        self.start_loading_animation()

        self.thread = EmbedWorker(
            self.video_path,
            self.input_msg.text(),
            None,
            None,
            save_path
        )

        self.thread.finished.connect(self.on_finish)
        self.thread.error.connect(self.on_error)

        self.thread.start()

    def start_loading_animation(self):
        self.dots = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_loading_text)
        self.timer.start(500)

    def update_loading_text(self):
        self.dots = (self.dots + 1) % 4
        self.loading_label.setText("Processing" + "." * self.dots)

    def on_finish(self, result):
        self.timer.stop()
        self.progress.setValue(100)
        self.loading_label.setText("Done")

        format_type = "MP4" if self.thread.output.endswith(".mp4") else "AVI"

        info = f"""
Embed berhasil

Lokasi:
{self.thread.output}

Format: {format_type}

PSNR: {result['psnr']:.2f}
MSE : {result['mse']:.6f}
"""

        self.result_label.setText(info)

    def on_error(self, msg):
        self.timer.stop()
        self.loading_label.setText("Error")
        self.result_label.setText(msg)