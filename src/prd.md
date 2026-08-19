# Product Requirements Document (PRD) - Synthetic Dataset Generation for Prescriptive Maintenance

## 1. Project Overview
Kami sedang membangun sistem "Prescriptive Maintenance" menggunakan arsitektur AI ganda. Sistem ini membaca data sensor mesin pabrik untuk memprediksi kerusakan (menggunakan Predictive AI), dan secara otomatis merumuskan langkah perbaikan (SOP) berbasis teks menggunakan model bahasa (Generative AI).

## 2. Your Task as an AI Agent
Tugas utama Anda adalah **menghasilkan dataset sintetis berbentuk JSONL** yang akan digunakan untuk melakukan *instruction fine-tuning* pada model LLM (Qwen2.5-7B-Instruct). Dataset ini berfungsi agar LLM memahami cara merespons laporan sensor dari sistem *Predictive AI* dan mengubahnya menjadi instruksi perbaikan (SOP) berbahasa Indonesia yang profesional, taktis, dan mudah dipahami teknisi pabrik.

## 3. Data Source Context (AI4I 2020 Dataset)
Input yang akan dilaporkan ke LLM berisi 5 parameter sensor:
1. `air_temperature_k` (Suhu udara, ~295K - 305K)
2. `process_temperature_k` (Suhu proses, ~305K - 315K)
3. `rotational_speed_rpm` (Kecepatan putar, ~1200 - 2800 rpm)
4. `torque_nm` (Torsi, ~15 - 70 Nm)
5. `tool_wear_min` (Keausan alat, ~0 - 250 menit)

## 4. Failure Modes & Target SOP
Anda harus membuat variasi data berdasarkan 6 kelas kondisi mesin berikut. Buatlah SOP yang logis dan relevan dengan standar operasional industri manufaktur untuk setiap kondisi:

*   **Normal:** Kondisi mesin sehat. (SOP: Berikan konfirmasi bahwa mesin beroperasi optimal, teruskan pemantauan rutin).
*   **TWF (Tool Wear Failure):** Terjadi jika `tool_wear_min` > 200 menit. (SOP: Instruksikan penghentian mesin, prosedur pelepasan alat lama, kalibrasi alat baru, dan *reset* parameter).
*   **HDF (Heat Dissipation Failure):** Terjadi jika suhu sangat tinggi (contoh: selisih suhu udara dan proses rendah) dan `rotational_speed_rpm` < 1380. (SOP: Instruksikan *emergency stop*, prosedur pendinginan, pembersihan filter udara, dan pengecekan kipas radiator).
*   **PWF (Power Failure):** Terjadi jika suplai tenaga (kombinasi torsi dan kecepatan putar) anjlok secara tidak normal. (SOP: Instruksikan isolasi kelistrikan, pengecekan sekring/panel daya utama, dan verifikasi kestabilan voltase).
*   **OSF (Overstrain Failure):** Terjadi akibat torsi berlebih (contoh: `torque_nm` > 60) dipadukan dengan keausan alat. (SOP: Instruksikan pengurangan beban mekanis (*load*), pengecekan poros engkol/poros utama, dan kalibrasi batas torsi).
*   **RNF (Random Failure):** Kegagalan perangkat keras tak terduga. (SOP: Instruksikan isolasi area, pemanggilan teknisi mekanik level 2, dan diagnostik menyeluruh).

## 5. Output Format Requirements
Dataset harus berformat JSONL (satu JSON per baris). Setiap JSON harus memiliki struktur Alpaca-style berikut:

```json
{
  "instruction": "Kamu adalah asisten teknisi ahli di pabrik manufaktur. Berikan panduan perbaikan (SOP) langkah demi langkah berdasarkan laporan deteksi kerusakan mesin berikut.",
  "input": "Laporan Deteksi AI: Mesin terdeteksi mengalami [MODE KEGAGALAN]. Data Sensor -> Suhu Udara: [X]K, Suhu Proses: [Y]K, Kecepatan: [Z] rpm, Torsi: [A] Nm, Keausan Alat: [B] menit.",
  "output": "[Respons dari AI yang berisi sapaan peringatan, sebutkan angka sensor yang bermasalah sebagai konteks, lalu berikan 3-5 langkah SOP perbaikan industri dalam bahasa Indonesia yang tegas dan profesional.]"
}
```

## 6. Execution Command
Buatkan 100 baris data JSONL dengan distribusi proporsional untuk ke-6 kondisi di atas (sekitar 15-20 data per kondisi). Pastikan angka pada bagian input bervariasi dan masuk akal sesuai aturan di Poin 3 dan 4. Jangan gunakan blok kode (```) yang membungkus keseluruhan hasil, cukup cetak baris JSON-nya secara langsung.