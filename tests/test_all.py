import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")

sys.path.insert(0, SRC_DIR)

print("SRC DIR:", SRC_DIR) 

from a51 import A51
from embed import StegoEmbed
from extract import StegoExtract

# =========================
# 1. TEST A5/1
# =========================
print("=== TEST A5/1 ===")
msg = b"Hello Test A51"
cipher = A51("kunci123")

enc = cipher.encrypt(msg)
dec = cipher.decrypt(enc)

print("Original :", msg)
print("Decrypted:", dec)

if msg == dec:
    print("A5/1 OK\n")
else:
    print("A5/1 ERROR\n")
    exit()


# =========================
# 2. TEST EMBED
# =========================
print("=== TEST EMBED ===")

# Customable (Bisa diubah sesuai kebutuhan antara avi/mp4, pesan teks/file, dll)
video_path = "video2.mp4" 
stego_path = "stego_video.mp4"
message = "INI PESAN RAHASIA"

embedder = StegoEmbed(
    video_path=video_path,
    secret_msg=message,
    a51_key="kunci123",
    stego_key="randomkey",
    output_path=stego_path,
    lsb_scheme=2 # Bisa memilih antara 1, 2, atau 3 sesuai dengan skema LSB yang diinginkan
)

result_embed = embedder.run_embedding(
    is_file=False,
    encrypt=True, # True untuk mengenkripsi pesan, False untuk tidak menggunakan enkripsi
    use_random=True # True untuk menggunakan penyisipan acak, False untuk penyisipan sequential
)

print("Embed Result:", result_embed, "\n")


# =========================
# 3. TEST EXTRACT
# =========================
print("=== TEST EXTRACT ===")

extractor = StegoExtract(
    video_path=stego_path,
    a51_key="kunci123",
    stego_key="randomkey"
)

result_extract = extractor.extraction()

print("Extract Result:", result_extract, "\n")


# =========================
# 4. VALIDASI HASIL
# =========================
print("=== VALIDATION ===")

if result_extract["type"] == "teks":
    extracted_msg = result_extract["data"]

    print("Original Message :", message)
    print("Extracted Message:", extracted_msg)

    if message == extracted_msg:
        print("SUCCESS: Pesan cocok!")
    else:
        print("ERROR: Pesan tidak sama!")

else:
    print("File extracted:", result_extract["filepath"])