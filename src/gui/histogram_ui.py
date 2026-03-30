from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from gui.style import load_pixel_font
import cv2
import matplotlib.pyplot as plt
import os
import tempfile
import shutil
import numpy as np


class HistogramPage(QWidget):
    def __init__(self, go_back):
        super().__init__()

        self.original_path = ""
        self.stego_path = ""

        temp_dir = tempfile.gettempdir()
        self.image_path = os.path.join(temp_dir, "histogram.png")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        title = QLabel("HISTOGRAM ANALYSIS")
        title.setFont(load_pixel_font(14))
        title.setAlignment(Qt.AlignCenter)

        btn_original = QPushButton("Select Original Video")
        btn_original.setFont(load_pixel_font(10))
        btn_original.clicked.connect(self.choose_original)

        self.label_original = QLabel("No original selected")
        self.label_original.setFont(load_pixel_font(8))
        self.label_original.setAlignment(Qt.AlignCenter)

        btn_stego = QPushButton("Select Stego Video")
        btn_stego.setFont(load_pixel_font(10))
        btn_stego.clicked.connect(self.choose_stego)

        self.label_stego = QLabel("No stego selected")
        self.label_stego.setFont(load_pixel_font(8))
        self.label_stego.setAlignment(Qt.AlignCenter)

        button_layout = QHBoxLayout()
        
        run_normal = QPushButton("SHOW OVERLAY HIST")
        run_normal.setFont(load_pixel_font(10))
        run_normal.clicked.connect(self.generate_histogram)
        
        run_diff = QPushButton("SHOW DIFF HIST")
        run_diff.setFont(load_pixel_font(10))
        run_diff.clicked.connect(self.generate_diff_histogram)
        
        button_layout.addWidget(run_normal)
        button_layout.addWidget(run_diff)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: white;")

        self.download_btn = QPushButton("DOWNLOAD IMAGE")
        self.download_btn.setFont(load_pixel_font(10))
        self.download_btn.setVisible(False)
        self.download_btn.clicked.connect(self.download_image)

        self.info = QLabel("")
        self.info.setAlignment(Qt.AlignCenter)

        back = QPushButton("BACK")
        back.setFont(load_pixel_font(10))
        back.clicked.connect(go_back)

        layout.addWidget(title)
        layout.addWidget(btn_original)
        layout.addWidget(self.label_original)
        layout.addWidget(btn_stego)
        layout.addWidget(self.label_stego)
        layout.addLayout(button_layout) 
        layout.addWidget(self.image_label)
        layout.addWidget(self.download_btn)
        layout.addWidget(self.info)
        layout.addSpacing(10)
        layout.addWidget(back)

        self.setLayout(layout)

    def choose_original(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Original Video")
        if file:
            self.original_path = file
            self.label_original.setText(os.path.basename(file))

    def choose_stego(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Stego Video")
        if file:
            self.stego_path = file
            self.label_stego.setText(os.path.basename(file))

    def get_frame(self, path):
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        cap.release()
        return frame if ret else None

    def plot_hist(self, frame, title):
        colors = ('b', 'g', 'r') 
        for i, c in enumerate(colors):
            hist = cv2.calcHist([frame], [i], None, [256], [0, 256])
            plt.plot(hist, color=c)
        plt.title(title)
        plt.xlabel("Pixel Value")
        plt.ylabel("Frequency")

    def calculate_metrics(self, img1, img2):
        mse = np.mean((img1.astype(np.float64) - img2.astype(np.float64)) ** 2)

        if mse == 0:
            psnr = 100
        else:
            psnr = 10 * np.log10((255 ** 2) / mse)

        if psnr > 40:
            quality = "Excellent"
        elif psnr > 30:
            quality = "Good"
        else:
            quality = "Low"

        return mse, psnr, quality

    def generate_histogram(self):
        if not self.original_path or not self.stego_path:
            self.info.setText("Select both videos first")
            return

        frame_ori = self.get_frame(self.original_path)
        frame_stego = self.get_frame(self.stego_path)

        if frame_ori is None or frame_stego is None:
            self.info.setText("Error reading video")
            return

        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        self.plot_hist(frame_ori, "Original")

        plt.subplot(1, 2, 2)
        self.plot_hist(frame_stego, "Stego")

        plt.tight_layout()
        plt.savefig(self.image_path, bbox_inches='tight')
        plt.close()

        pixmap = QPixmap(self.image_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)
        self.image_label.setMaximumHeight(400)

        self.update_info_panel(frame_ori, frame_stego)

    def generate_diff_histogram(self):
        if not self.original_path or not self.stego_path:
            self.info.setText("Select both videos first")
            return

        frame_ori = self.get_frame(self.original_path)
        frame_stego = self.get_frame(self.stego_path)

        if frame_ori is None or frame_stego is None:
            self.info.setText("Error reading video")
            return

        frame_ori_int = frame_ori.astype(np.int16)
        frame_stego_int = frame_stego.astype(np.int16)

        diff_frame = frame_stego_int - frame_ori_int

        colors = ('b', 'g', 'r')
        fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
        fig.suptitle('Difference Histogram (Stego - Original)', fontsize=14, fontweight='bold')

        bins = np.arange(-5, 7) - 0.5 

        for i, col in enumerate(colors):
            channel_diff = diff_frame[:, :, i].flatten()

            axes[i].hist(channel_diff, bins=bins, color=col, alpha=0.8, edgecolor='black', rwidth=0.8)
            axes[i].set_title(f'Difference Channel {col.upper()}', fontsize=10)
            axes[i].set_xticks(np.arange(-5, 6))
            
            axes[i].set_yscale('log') 
            axes[i].grid(axis='y', linestyle='--', alpha=0.5)

        plt.xlabel('Nilai Selisih Piksel (Stego - Original)')
        plt.ylabel('Frekuensi (Log Scale)')
        plt.tight_layout()
        plt.savefig(self.image_path, bbox_inches='tight')
        plt.close()

        pixmap = QPixmap(self.image_path)
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)
        self.image_label.setMaximumHeight(550) 

        self.update_info_panel(frame_ori, frame_stego)

    def update_info_panel(self, frame_ori, frame_stego):
        mse, psnr, quality = self.calculate_metrics(frame_ori, frame_stego)

        self.download_btn.setVisible(True)

        self.info.setText(
            f"MSE: {mse:.4f}\n"
            f"PSNR: {psnr:.2f} dB\n"
            f"Quality: {quality}"
        )
        self.info.setFont(load_pixel_font(8))

    def download_image(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Histogram",
            "histogram.png",
            "PNG Image (*.png)"
        )

        if not path:
            return

        if not path.endswith(".png"):
            path += ".png"

        shutil.copy(self.image_path, path)

        self.info.setText(f"Saved to:\n{path}")