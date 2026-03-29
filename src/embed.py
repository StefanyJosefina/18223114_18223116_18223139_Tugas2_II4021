import cv2
import numpy as np
import os
import random
import hashlib
import math
import imageio
from a51 import A51

class StegoEmbed:
    def __init__(self, video_path, secret_msg, a51_key=None, stego_key=None, output_path="stego_video.avi", lsb_scheme=1):
        self.video_path = video_path
        self.secret_msg = secret_msg
        self.a51_key = a51_key
        self.stego_key = stego_key
        self.output_path = output_path
        self.lsb_scheme = lsb_scheme

    def get_seed(self, key_str):
        return int(hashlib.sha256(key_str.encode('utf-8')).hexdigest(), 16)
    
    def calculate_metrics(self, original_frame, stego_frame):
        # mse
        mse = np.mean((original_frame.astype(np.float64) - stego_frame.astype(np.float64)) ** 2)
        if mse == 0:
            return 0, 100
        # psnr
        psnr = 10 * math.log10((255 ** 2) / mse)
        return mse, psnr
    
    # Perbaikan fungsi enkripsi A5/1 
    def a51_encrypt(self, data_bytes):
        cipher = A51(self.a51_key)
        return cipher.encrypt(data_bytes)

    def a51_decrypt(self, data_bytes):
        cipher = A51(self.a51_key)
        return cipher.decrypt(data_bytes)
    
    def embed_rgb(self, pixel, message_byte, lsb_scheme):
        r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])

        if lsb_scheme == 1: # Skema 3-3-2
            r_msg = (message_byte >> 5) & 0b111
            g_msg = (message_byte >> 2) & 0b111
            b_msg = message_byte & 0b11
            new_r = (r & 0b11111000) | r_msg
            new_g = (g & 0b11111000) | g_msg
            new_b = (b & 0b11111100) | b_msg

        elif lsb_scheme == 2: # Skema 2-3-3
            r_msg = (message_byte >> 6) & 0b11
            g_msg = (message_byte >> 3) & 0b111
            b_msg = message_byte & 0b111
            new_r = (r & 0b11111100) | r_msg
            new_g = (g & 0b11111000) | g_msg
            new_b = (b & 0b11111000) | b_msg

        elif lsb_scheme == 3: # Skema 4-2-2
            r_msg = (message_byte >> 4) & 0b1111
            g_msg = (message_byte >> 2) & 0b11
            b_msg = message_byte & 0b11
            new_r = (r & 0b11110000) | r_msg
            new_g = (g & 0b11111100) | g_msg
            new_b = (b & 0b11111100) | b_msg
            
        else:
            raise ValueError("Skema LSB tidak valid!")

        return np.array([new_r, new_g, new_b], dtype=np.uint8)
    
    def run_embedding(self, is_file=False, encrypt=False, use_random=False, progress_callback=None):
        if is_file:
            basename = os.path.basename(self.secret_msg)
            filename = os.path.splitext(basename)[0] 
            ext = os.path.splitext(basename)[1]
            
            with open(self.secret_msg, 'rb') as f:
                payload = bytearray(f.read())
            msg_type = "file"
        else:
            payload = bytearray(self.secret_msg.encode('utf-8'))
            filename = "text_msg"
            ext = ".txt"
            msg_type = "text"

        if encrypt:
            if not self.a51_key:
                raise ValueError("Kunci A5/1 wajib diisi!")
            payload = self.a51_encrypt(payload)

        cap = cv2.VideoCapture(self.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # FIX: nama variabel
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        total_pixels = (total_frames - 1) * w * h  # FIX: pakai total_frames

        if len(payload) > total_pixels:
            cap.release()
            raise ValueError(f"Pesan terlalu besar! Kapasitas maksimum: {total_pixels} bytes.")
        
        is_mp4 = self.output_path.lower().endswith('.mp4')

        if is_mp4:
            writer = imageio.get_writer(
                self.output_path, 
                fps=fps, 
                codec='libx264rgb', 
                macro_block_size=1,
                ffmpeg_params=['-crf', '0', '-loglevel', 'error']
            )
        else:
            fourcc = cv2.VideoWriter_fourcc(*'FFV1')
            out = cv2.VideoWriter(self.output_path, fourcc, fps, (w, h))

        meta_str = f"{msg_type};{ext};{len(payload)};{filename};{int(encrypt)};{int(use_random)};{total_pixels};{self.lsb_scheme}||"
        meta_bytes = meta_str.encode('utf-8')

        ret, frame = cap.read()
        if not ret: return

        idx = 0
        for y in range(h):
            for x in range(w):
                if idx < len(meta_bytes):
                    frame[y, x] = self.embed_rgb(frame[y, x], meta_bytes[idx], lsb_scheme=1)
                    idx += 1

        if is_mp4:
            writer.append_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        else:
            out.write(frame)

        if use_random: 
            if not self.stego_key: raise ValueError("Stego-key wajib diisi!")
            random.seed(self.get_seed(self.stego_key))
            pixel_indices = random.sample(range(total_pixels), len(payload))
        else:
            pixel_indices = range(len(payload))

        payload_map = {}
        for byte_order, p_idx in enumerate(pixel_indices):
            f_idx = (p_idx // (w * h)) + 1
            p_in_f = p_idx % (w * h)
            y, x = p_in_f // w, p_in_f % w
            if f_idx not in payload_map: payload_map[f_idx] = []
            payload_map[f_idx].append((y, x, byte_order))

        current_f = 1
        total_mse, total_psnr, count = 0, 0, 0

        while True: 
            ret, frame = cap.read()
            if not ret: break
            original_frame = frame.copy()
            if current_f in payload_map:
                for (y, x, b_idx) in payload_map[current_f]:
                    frame[y, x] = self.embed_rgb(frame[y, x], payload[b_idx], lsb_scheme=self.lsb_scheme)

                mse, psnr = self.calculate_metrics(original_frame, frame)
                total_mse += mse
                total_psnr += psnr
                count += 1

            if is_mp4:
                writer.append_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                out.write(frame)

            if progress_callback and total_frames > 0:
                progress_percent = int((current_f / total_frames) * 100)
                progress_callback(progress_percent)
                
            current_f += 1

        cap.release()

        if is_mp4:
            writer.close()
        else:
            out.release()

        avg_psnr = total_psnr / count if count > 0 else 100
        return {"status": "success", "psnr": avg_psnr, "mse": total_mse/count if count > 0 else 0}