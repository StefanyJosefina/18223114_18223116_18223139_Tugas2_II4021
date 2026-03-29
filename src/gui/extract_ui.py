from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit,
    QLabel, QFileDialog, QProgressBar, QTextEdit, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from gui.style import load_pixel_font
from extract import StegoExtract
import os
import shutil
import tempfile
import time

class ExtractWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, video_path, a51_key=None, stego_key=None, output_dir=None):
        super().__init__()
        self.video_path = video_path
        self.a51_key = a51_key
        self.stego_key = stego_key
        self.output_dir = output_dir

    def run(self):
        try:
            obj = StegoExtract(
                video_path=self.video_path,
                a51_key=self.a51_key,
                stego_key=self.stego_key,
                output_dir=self.output_dir
            )
            res = obj.extraction(progress_callback=self.progress.emit)
            self.finished.emit(res)
        except Exception as e:
            self.error.emit(str(e))

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
        self.file_label.setFont(load_pixel_font(8))
        self.file_label.setAlignment(Qt.AlignCenter)

        self.cb_encrypt = QCheckBox("Has A5/1 Encryption")
        self.cb_encrypt.setFont(load_pixel_font(8))
        self.input_a51 = QLineEdit()
        self.input_a51.setPlaceholderText("Enter A5/1 Key")
        self.input_a51.setEchoMode(QLineEdit.Password)
        self.input_a51.setEnabled(False)
        self.cb_encrypt.toggled.connect(self.input_a51.setEnabled)

        self.cb_random = QCheckBox("Has Stego-key (Randomized)")
        self.cb_random.setFont(load_pixel_font(8))
        self.input_stego = QLineEdit()
        self.input_stego.setPlaceholderText("Enter Stego-key")
        self.input_stego.setEchoMode(QLineEdit.Password)
        self.input_stego.setEnabled(False)
        self.cb_random.toggled.connect(self.input_stego.setEnabled)

        self.progress = QProgressBar()
        self.progress.setVisible(False)

        self.time_label = QLabel("Elapsed Time: 00:00")
        self.time_label.setFont(load_pixel_font(8))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setVisible(False)

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
        
        layout.addWidget(self.cb_encrypt)
        layout.addWidget(self.input_a51)
        layout.addWidget(self.cb_random)
        layout.addWidget(self.input_stego)
        
        layout.addWidget(self.progress)
        layout.addWidget(self.time_label)
        layout.addWidget(run)
        layout.addWidget(self.result_title)
        layout.addWidget(self.result_box)
        layout.addWidget(self.download_btn)
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

    def run_extract(self):
        if not self.video_path:
            self.result_box.setText("Please select a video first")
            return

        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.time_label.setVisible(True)
        self.time_label.setText("Elapsed Time: 00:00")
        self.start_time = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        self.result_box.setText("Extracting...")
        self.result_title.setText("")
        self.download_btn.setVisible(False)

        a51_key = self.input_a51.text() if self.cb_encrypt.isChecked() else None
        stego_key = self.input_stego.text() if self.cb_random.isChecked() else None

        temp_dir = tempfile.gettempdir()

        # self.start_progress()

        self.thread = ExtractWorker(
            video_path=self.video_path,
            a51_key=a51_key,
            stego_key=stego_key,
            output_dir=temp_dir
        )
        self.thread.progress.connect(self.progress.setValue)
        self.thread.finished.connect(self.finish_extract)
        self.thread.error.connect(self.show_error)
        self.thread.start()

    # def start_progress(self):
    #     self.val = 0
    #     self.timer = QTimer()
    #     self.timer.timeout.connect(self.update_bar)
    #     self.timer.start(80)

    # def update_bar(self):
    #     if self.val < 90:
    #         self.val += 1
    #         self.progress.setValue(self.val)

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        mins, secs = divmod(elapsed, 60)
        self.time_label.setText(f"Elapsed Time: {mins:02d}:{secs:02d}")

    def finish_extract(self, res):
        # self.timer.stop()
        if hasattr(self, "timer"): 
            self.timer.stop()
        self.progress.setValue(100)

        data_type = res.get("type", "").lower()

        if data_type in ["text", "teks"]:
            self.result_title.setText("HIDDEN MESSAGE")
            self.result_box.setText(res.get("data", ""))
            self.adjust_textbox_height()

        else:
            self.result_title.setText("FILE EXTRACTED")
            self.result_box.setText("Click download to save the extracted file")
            
            self.extracted_file_path = res.get("filepath")
            self.download_btn.setVisible(True)
            self.adjust_textbox_height()

    def show_error(self, msg):
        if hasattr(self, "timer"):
            self.timer.stop()
        self.progress.setVisible(False)
        self.time_label.setVisible(False)
        self.result_box.setText(f"Error: {msg}")
        self.result_title.setText("EXTRACTION FAILED")

    def save_file(self):
        if not self.extracted_file_path:
            return

        default_name = os.path.basename(self.extracted_file_path)
        ext = os.path.splitext(default_name)[1]

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            default_name,
            f"Extracted File (*{ext})"
        )

        if not path:
            return

        shutil.move(self.extracted_file_path, path)
        
        self.extracted_file_path = None
        self.download_btn.setVisible(False)

        self.result_box.setText(f"Saved to:\n{path}")

    def adjust_textbox_height(self):
        doc_height = self.result_box.document().size().height()
        self.result_box.setFixedHeight(int(doc_height + 10))