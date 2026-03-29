import cv2
import numpy as np
import random
import os
import hashlib
from a51 import A51 

class StegoExtract:
    def __init__(self, video_path, a51_key=None, stego_key=None, output_dir=None):
        self.video_path = video_path
        self.a51_key = a51_key
        self.stego_key = stego_key
        self.output_dir = output_dir

    def get_seed(self, key_str):
        return int(hashlib.sha256(key_str.encode('utf-8')).hexdigest(), 16)

    def extract_rgb(self, pixel, lsb_scheme):
        r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])
        
        if lsb_scheme == 1: # Skema 3-3-2
            r_bits = r & 0b111
            g_bits = g & 0b111
            b_bits = b & 0b11
            return (r_bits << 5) | (g_bits << 2) | b_bits

        elif lsb_scheme == 2: # Skema 2-3-3
            r_bits = r & 0b11
            g_bits = g & 0b111
            b_bits = b & 0b111
            return (r_bits << 6) | (g_bits << 3) | b_bits

        elif lsb_scheme == 3: # Skema 4-2-2
            r_bits = r & 0b1111
            g_bits = g & 0b11
            b_bits = b & 0b11
            return (r_bits << 4) | (g_bits << 2) | b_bits
            
        return 0

    def get_metadata(self, frame):
        extract_bytes = bytearray()
        height, width, _ = frame.shape
        end = b'||'

        for y in range(height):
            for x in range(width):
                byte_val = self.extract_rgb(frame[y, x], lsb_scheme=1)
                extract_bytes.append(byte_val)

                if len(extract_bytes) >= 2 and extract_bytes[-2:] == end:
                    meta_str = extract_bytes[:-2].decode('utf-8', errors='ignore')
                    parts = meta_str.split(';')
                    try:
                        return {
                            "type": parts[0],
                            "extension": parts[1],
                            "byte_size": int(parts[2]),
                            "filename": parts[3],
                            "is_encrypted": bool(int(parts[4])),
                            "is_random": bool(int(parts[5])),
                            "capacity": int(parts[6]),
                            "lsb_scheme": int(parts[7])
                        }
                    except Exception:
                        raise ValueError("Metadata format is corrupted")
        raise ValueError("End tag not found")

    # Tambahan Fungsi A5/1
    def a51_decrypt(self, ciphertext_bytes):
        cipher = A51(self.a51_key)
        return cipher.decrypt(ciphertext_bytes)

    def extraction(self, progress_callback=None):
        if not os.path.exists(self.video_path):
            raise FileNotFoundError(f"'{self.video_path}' not found")

        try:
            cap = cv2.VideoCapture(self.video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            ret, frame0 = cap.read()
            if not ret:
                raise ValueError("Gagal membaca frame pertama dari video.")

            height, width, _ = frame0.shape
            pixels_per_frame = width * height

            meta = self.get_metadata(frame0)
            target_bytes = meta['byte_size']
            payload_lsb_scheme = meta['lsb_scheme']

            if meta['is_random']:
                if not self.stego_key:
                    raise ValueError("Stego key is missing")
                random.seed(self.get_seed(self.stego_key))
                pixel_indices = random.sample(range(meta['capacity']), target_bytes)
            else:
                pixel_indices = range(target_bytes)

            frame_targets = {}
            for byte_order, idx_1d in enumerate(pixel_indices):
                frame_idx = 1 + (idx_1d // pixels_per_frame)
                pixel_in_frame = idx_1d % pixels_per_frame
                y = pixel_in_frame // width
                x = pixel_in_frame % width

                if frame_idx not in frame_targets:
                    frame_targets[frame_idx] = []
                frame_targets[frame_idx].append((y, x, byte_order))

            extracted_data = [0] * target_bytes
            current_frame = 1

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if current_frame in frame_targets:
                    for (y, x, byte_order) in frame_targets[current_frame]:
                        extracted_data[byte_order] = self.extract_rgb(frame[y, x], lsb_scheme=payload_lsb_scheme)

                if progress_callback and total_frames > 0:
                    progress_percent = int((current_frame / total_frames) * 100)
                    progress_callback(progress_percent)
                
                current_frame += 1
                if current_frame >= total_frames:
                    break

            cap.release()

            ciphertext_bytes = bytearray(extracted_data)

            if meta['is_encrypted']:
                if not self.a51_key:
                    raise ValueError("Pesan Terenkripsi, tetapi Kunci A5/1 kosong!")
                final_bytes = self.a51_decrypt(ciphertext_bytes)
            else:
                final_bytes = ciphertext_bytes

            if meta['type'] == 'text':
                pesan_teks = final_bytes.decode('utf-8', errors='ignore')
                return {
                    "status": "success",
                    "type": "teks",
                    "data": pesan_teks,
                    "metadata": meta
                }
            else:
                output_filename = f"extract_{meta['filename']}{meta['extension']}"
                
                if self.output_dir:
                    os.makedirs(self.output_dir, exist_ok=True)
                    output_filepath = os.path.join(self.output_dir, output_filename)
                else:
                    output_filepath = output_filename

                with open(output_filepath, 'wb') as f:
                    f.write(final_bytes)
                return {
                    "status": "success",
                    "type": "file",
                    "filepath": output_filepath,
                    "metadata": meta
                }

        except Exception as e:
            if 'cap' in locals() and cap.isOpened():
                cap.release()
            raise RuntimeError(f"Extraction failed: {str(e)}")