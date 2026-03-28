from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit,
    QLabel, QFileDialog, QProgressBar, QComboBox, QHBoxLayout, QCheckBox
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

    def __init__(self, video, payload, output_format, is_file=False, a51_key=None, stego_key=None, lsb_scheme=1, encrypt=False, use_random=False):
        super().__init__()
        self.video = video
        self.payload = payload
        self.output_format = output_format.lower()
        self.is_file = is_file
        
        self.a51_key = a51_key
        self.stego_key = stego_key
        self.lsb_scheme = lsb_scheme
        self.encrypt = encrypt
        self.use_random = use_random

        temp_dir = tempfile.gettempdir()
        self.temp_output = os.path.join(temp_dir, f"temp_stego.{self.output_format}")

    def run(self):
        try:
            obj = StegoEmbed(
                video_path=self.video,
                secret_msg=self.payload,
                a51_key=self.a51_key,
                stego_key=self.stego_key,
                output_path=self.temp_output,
                lsb_scheme=self.lsb_scheme
            )

            result = obj.run_embedding(
                is_file=self.is_file,
                encrypt=self.encrypt,
                use_random=self.use_random
            )

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

        # 1. Pilihan LSB Scheme
        scheme_layout = QHBoxLayout()
        scheme_label = QLabel("LSB Scheme:")
        scheme_label.setFont(load_pixel_font(8))
        self.scheme_box = QComboBox()
        self.scheme_box.addItems(["3-3-2", "2-3-3", "4-2-2"])
        scheme_layout.addWidget(scheme_label)
        scheme_layout.addWidget(self.scheme_box)

        # 2. Checkbox & Input Enkripsi A5/1
        self.cb_encrypt = QCheckBox("Encrypt (A5/1)")
        self.cb_encrypt.setFont(load_pixel_font(8))
        self.input_a51 = QLineEdit()
        self.input_a51.setPlaceholderText("Enter A5/1 Key")
        self.input_a51.setEchoMode(QLineEdit.Password)
        self.input_a51.setEnabled(False) # Nonaktif sampai checkbox dicentang
        self.cb_encrypt.toggled.connect(self.input_a51.setEnabled)

        # 3. Checkbox & Input Stego Key (Random)
        self.cb_random = QCheckBox("Randomize (Stego-key)")
        self.cb_random.setFont(load_pixel_font(8))
        self.input_stego = QLineEdit()
        self.input_stego.setPlaceholderText("Enter Stego-key")
        self.input_stego.setEchoMode(QLineEdit.Password)
        self.input_stego.setEnabled(False) # Nonaktif sampai checkbox dicentang
        self.cb_random.toggled.connect(self.input_stego.setEnabled)

        # Output Format
        format_layout = QHBoxLayout()
        format_label = QLabel("Output Format:")
        format_label.setFont(load_pixel_font(8))
        self.format_box = QComboBox()
        self.format_box.addItems(["AVI", "MP4"])
        self.format_box.setCurrentText("AVI")
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_box)

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
        
        layout.addLayout(scheme_layout)
        layout.addWidget(self.cb_encrypt)
        layout.addWidget(self.input_a51)
        layout.addWidget(self.cb_random)
        layout.addWidget(self.input_stego)
        layout.addLayout(format_layout)
        
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

        encrypt = self.cb_encrypt.isChecked()
        use_random = self.cb_random.isChecked()
        
        a51_key = self.input_a51.text() if encrypt else None
        stego_key = self.input_stego.text() if use_random else None

        if encrypt and not a51_key:
            self.result.setText("A5/1 Key is required!")
            return
            
        if use_random and not stego_key:
            self.result.setText("Stego Key is required!")
            return
            
        scheme_text = self.scheme_box.currentText()
        if scheme_text == "3-3-2": lsb_scheme = 1
        elif scheme_text == "2-3-3": lsb_scheme = 2
        elif scheme_text == "4-2-2": lsb_scheme = 3

        self.output_format = self.format_box.currentText().lower()

        self.download_btn.setVisible(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.result.setText("")

        self.start_progress()

        self.thread = EmbedWorker(
            video=self.video_path,
            payload=payload,
            output_format=self.output_format,
            is_file=is_file,
            a51_key=a51_key,
            stego_key=stego_key,
            lsb_scheme=lsb_scheme,
            encrypt=encrypt,
            use_random=use_random
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

        psnr = result.get("psnr", 0)
        mse = result.get("mse", 0)

        self.result.setText(
            f"Format: {self.output_format.upper()}\n"
            f"MSE: {mse:.6f}\n"
            f"PSNR: {psnr:.2f} dB\n"
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