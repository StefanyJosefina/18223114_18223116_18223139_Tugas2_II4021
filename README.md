# Tugas 2 II4021 Kriptografi - Steganografi LSB pada Berkas Video AVI

## Deskripsi

Repositori ini berisi implementasi perangkat lunak untuk Tugas 2 mata kuliah II4021 Kriptografi. Fungsi utama dari aplikasi ini adalah untuk melakukan penyisipan (steganografi) pesan rahasia ke dalam berkas video berformat AVI menggunakan metode _Least Significant Bit_ (LSB). Program ini juga memiliki kemampuan untuk melakukan ekstraksi pesan dari video stego dan menampilkan hasil analisis histogram.

Selain mendukung format standar AVI, program ini juga memiliki kemampuan untuk melakukan penyisipan pesan pada video _cover_ digital _lossy_ berformat MP4 dan menghasilkan keluaran video _stego_ dalam format yang sama.

## Teknologi yang Digunakan (_Tech Stack_)

Perangkat lunak ini dikembangkan menggunakan bahasa pemrograman Python

## Kebutuhan Sistem (_Dependencies_)

Untuk memastikan aplikasi dapat berjalan dengan baik tanpa kendala, pastikan Anda telah memasang pustaka-pustaka Python berikut:

- `PyQt5==5.15.11` (Untuk antarmuka grafis pengguna)
- `opencv-python==4.13.0.92` (Untuk pemrosesan _frame_ video)
- `matplotlib==3.10.8` (Untuk visualisasi dan analisis histogram)
- `imageio==2.37.3` (Untuk penanganan _input/output_ video)
- `numpy==2.4.3` (Untuk manipulasi matriks dan komputasi numerik)

## Petunjuk Penggunaan

Berikut adalah langkah-langkah instalasi dan eksekusi program:

1. **Kloning Repositori**: Unduh atau lakukan kloning repositori ini ke dalam direktori lokal komputer Anda.
2. **Pemasangan Pustaka**: Buka terminal atau _command prompt_, arahkan ke dalam direktori `src` dengan cara ketik `cd src`, dan jalankan perintah berikut untuk memasang seluruh kebutuhan sistem:
   ```bash
   pip install -r requirements.txt
   ```
3. **Menjalankan Aplikasi**: Setelah seluruh pustaka prasyarat berhasil dipasang, tetap arahkan ke dalam direktori `src`. Eksekusi program utama untuk membuka antarmuka aplikasi menggunakan perintah berikut:
   ```bash
   python main.py
   ```

## Kontributor

<p align="center">
  <table>
    <tbody>
      <tr>
        <td align="center" valign="top" width="14.28%"><a href="https://github.com/rasyidrizky"><img src="https://avatars.githubusercontent.com/u/188223327?v=4?s=100" width="100px;" alt="Rasyid Rizky Susilo N."/><br /><sub><b>Rasyid Rizky Susilo N.</b></sub><br /><sub><b>18223114</b></sub></a><br />   </td>
        <td align="center" valign="top" width="14.28%"><a href="https://github.com/StefanyJosefina"><img src="https://avatars.githubusercontent.com/u/167734949?v=4?s=100" width="100px;" alt="Stefany Josefina Santono"/><br /><sub><b>Stefany Josefina Santono</b></sub><br /><sub><b>18223116</b></sub></a><br /> </td>
        <td align="center" valign="top" width="14.28%"><a href="https://github.com/kifu"><img src="https://avatars.githubusercontent.com/u/136690241?v=4?s=100" width="100px;" alt="Andi Syaichul Mubaraq"/><br /><sub><b>Andi Syaichul Mubaraq</b></sub><br /><sub><b>18223139</b></sub></a><br /> </td>
      </tr>
    </tbody>
  </table>
</p>
