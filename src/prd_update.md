# PRD Update - Synthetic Dataset Generation for Multi-Failure (Edge Cases)

## 1. Context & Objective
Sebelumnya Anda telah membuat dataset JSONL untuk kasus kegagalan tunggal (Single Failure) berdasarkan dataset AI4I 2020. Sekarang, kita perlu menambahkan variasi **Kerusakan Ganda (Multi-Failure / Edge Cases)**. 
Tujuan tugas ini adalah melatih LLM agar mampu merespons laporan Predictive AI yang mendeteksi 2 atau 3 jenis kegagalan sekaligus secara bersamaan, dan menyusun SOP perbaikan yang memprioritaskan keselamatan (Safety First).

## 2. Your Task
Hasilkan **40 baris data JSONL baru** yang secara khusus berisi skenario kerusakan ganda. Data ini akan digabungkan dengan dataset sebelumnya untuk di-*training* menggunakan format Alpaca.

## 3. Logical Multi-Failure Combinations
Buatlah variasi kombinasi kerusakan yang logis secara mekanis, seperti:
*   **HDF + TWF (Mesin Kepanasan & Alat Aus):** Suhu proses > 310K dan tool_wear_min > 200.
*   **TWF + OSF (Alat Aus & Kelebihan Beban):** tool_wear_min > 200 dan torque_nm > 65.
*   **HDF + PWF (Mesin Kepanasan & Gangguan Daya):** Suhu sangat tinggi disertai anjloknya pasokan daya.
*   **TWF + OSF + HDF (Efek Domino Kritis):** Pisau aus menyebabkan beban torsi naik, yang akhirnya memicu panas berlebih.

## 4. SOP Generation Rules (CRITICAL)
Saat Anda menyusun isi `output` (SOP Perbaikan), Anda wajib mengikuti logika prioritas operasional pabrik berikut:
1.  **Acknowledge All Failures:** Kalimat pertama AI harus dengan tegas menyebutkan semua mode kegagalan yang terdeteksi secara bersamaan.
2.  **Safety First (Prioritas Penanganan):** 
    *   Bahaya Kelistrikan (PWF) dan Termal/Panas (HDF) **harus diutamakan** (dilakukan di Langkah 1 dan 2, seperti *Emergency Stop* dan isolasi daya/pendinginan).
    *   Masalah Mekanis (TWF dan OSF) ditangani **setelah** mesin aman/dingin (dilakukan di Langkah 3 dan 4, seperti mengganti pisau dan kalibrasi torsi).
3.  **Contextual Data:** Tetap sebutkan angka sensor yang anomali di dalam narasi SOP Anda sebagai justifikasi.

## 5. Output Format Requirements
Gunakan format Alpaca berstruktur JSONL (satu baris per JSON). Contoh untuk HDF + TWF:

```json
{
  "instruction": "Kamu adalah asisten teknisi ahli di pabrik manufaktur. Berikan panduan perbaikan (SOP) langkah demi langkah berdasarkan laporan deteksi kerusakan mesin berikut.",
  "input": "Laporan Deteksi AI: Mesin terdeteksi mengalami HDF dan TWF secara bersamaan. Data Sensor -> Suhu Udara: 300K, Suhu Proses: 312K, Kecepatan: 1350 rpm, Torsi: 45 Nm, Keausan Alat: 215 menit.",
  "output": "PERINGATAN KRITIS: Mesin terdeteksi mengalami kerusakan ganda yaitu Heat Dissipation Failure (HDF) dan Tool Wear Failure (TWF). Suhu proses mencapai angka kritis 312K dan alat telah beroperasi selama 215 menit. Segera lakukan prosedur prioritas berikut:\n1. Tekan tombol Emergency Stop untuk menghentikan operasi mesin guna mencegah bahaya kebakaran (Prioritas HDF).\n2. Aktifkan sistem pendingin darurat dan tunggu minimal 45 menit hingga suhu turun di bawah 300K.\n3. Setelah suhu aman, buka kompartemen utama dan lepaskan mata pisau yang sudah aus (Prioritas TWF).\n4. Pasang mata pisau baru, lakukan kalibrasi posisi, lalu reset penghitung waktu keausan alat sebelum memulai ulang (restart) mesin."
}
```

## 6. Execution
Cetak 40 baris JSONL kombinasi kegagalan ganda tersebut secara langsung tanpa dibungkus code block (```) utama, agar bisa langsung saya simpan sebagai file .jsonl.