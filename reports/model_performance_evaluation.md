# Model Performance Evaluation & Operational Workflow Report

**Project**: Smart Manufacturing Maintenance (Predictive & Prescriptive AI)  
**Dataset**: AI4I 2020 Predictive Maintenance Dataset (10,000 observations)  
**Architecture**: Two-Stage Predictive AI + Fine-Tuned Prescriptive LLM (Qwen2.5-7B)

---

## 1. Executive Summary

Sistem **Smart Manufacturing Maintenance** menggunakan arsitektur AI ganda untuk menjamin keandalan operasi mesin pabrik:
1. **Predictive AI**: Membaca sensor real-time untuk mendeteksi apakah mesin mengalami kegagalan (`machine_failure`), serta mendiagnosis secara spesifik mode kegagalannya dari 5 kategori (`twf`, `hdf`, `pwf`, `osf`, `rnf`).
2. **Prescriptive AI**: Menggunakan LLM (Qwen2.5-7B-Instruct) yang telah di-*fine-tune* menggunakan LoRA untuk menyusun *Standard Operating Procedure* (SOP) perbaikan taktis berbahasa Indonesia berbasis prioritas keselamatan (*Safety First*).

---

## 2. Two-Stage Operational Triage Workflow

Di industri manufaktur nyata, alur kerja pemeliharaan mesin beroperasi dalam **3 Tahapan Operasional (Two-Stage Triage + Prescriptive Action)**:

```
[ Sensor Data Real-Time ]
           │
           ▼
┌───────────────────────────────────────────────────────────┐
│ TAHAP 1: Primary Alarm (Predictive Gatekeeper)            │
│ Memprediksi status mesin: Normal (0) vs Failure (1)       │
└──────────────────────────┬────────────────────────────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
       [ Status: NORMAL ]         [ Status: FAILURE ]
    (Lanjutkan pemantauan)               │
                                         ▼
                 ┌───────────────────────────────────────────┐
                 │ TAHAP 2: Root Cause Failure Inspection    │
                 │ Memeriksa mode kegagalan spesifik:        │
                 │ • HDF (Overheating / Panas Tinggi)        │
                 │ • PWF (Power Drop / Gangguan Daya)        │
                 │ • OSF (Overstrain / Torsi Berlebih)       │
                 │ • TWF (Tool Wear / Pisau Aus)             │
                 │ • RNF (Random Failure / Kegagalan Acak)   │
                 │ • Multi-Failure (Kombinasi Edge Cases)    │
                 └─────────────────────┬─────────────────────┘
                                       │
                                       ▼
                 ┌───────────────────────────────────────────┐
                 │ TAHAP 3: Prescriptive SOP Generation      │
                 │ LLM merumuskan langkah perbaikan taktis  │
                 │ berbahasa Indonesia dengan prioritas      │
                 │ keselamatan kerja (Safety First).         │
                 └───────────────────────────────────────────┘
```

Saat alarm Tahap 1 mendeteksi `machine_failure = 1`, sistem **secara otomatis langsung menjalankan Tahap 2** untuk mengidentifikasi penyebab rusaknya mesin secara rinci sebelum menginstruksikan langkah perbaikan di Tahap 3.

---

## 3. Comparative Performance Analysis: Overall Failure vs Specific Failure Modes

| Target / Failure Mode | Recall | Precision | F1-Score | ROC-AUC | Interpretasi Performa & Diagnostik |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **MACHINE_FAILURE** (Tahap 1) | **0.8676** | **0.6629** | **0.7516** | **0.9850** | **Gatekeeper Utama**: Memiliki ROC-AUC 0.9850 (near-perfect ranking) & Recall 86.76%, berhasil menyaring mayoritas potensi kegagalan mesin. |
| **HDF** (Heat Dissipation) | **1.0000** | **1.0000** | **1.0000** | **1.0000** | **Sempurna (100%)**: Dipicu selisih suhu udara & proses (`temp_diff`). Model tidak pernah salah mendeteksi kegagalan panas. |
| **PWF** (Power Failure) | **1.0000** | **0.9286** | **0.9630** | **0.9999** | **Sangat Tinggi (96.3%)**: Dipicu kombinasi daya mekanis (`power_w = torque * rpm`). Deteksi kelelahan suplai daya sangat presisi. |
| **OSF** (Overstrain) | **1.0000** | **0.8889** | **0.9412** | **1.0000** | **Sangat Tinggi (94.1%)**: Dipicu beban torsi tinggi & keausan pisau (`tool_wear_torque`). Seluruh kejadian overstrain tertangkap (Recall 100%). |
| **TWF** (Tool Wear) | **0.3000** | **0.0652** | **0.1071** | **0.8609** | **Kelas Sangat Langka (~0.45%)**: Ditingkatkan dengan rule fisika industri (`tool_wear_min > 200 menit`). |
| **RNF** (Random Failure) | **0.2500** | **0.0046** | **0.0091** | **0.5358** | ***Pure Random Noise***: Kegagalan acak 0.1% di dataset sintesis. Secara matematis tidak memiliki pola deterministik sensor. |

---

## 4. Analisis Kebenaran Diagnostik (Diagnostic Truth)

1. **Deteksi Fisika Deterministik (HDF, PWF, OSF)**:
   - Ketiga jenis kerusakan ini didasari hukum fisika termal dan mekanis. Model memberikan **kebenaran diagnostik yang sangat tinggi (F1-score 94% – 100%)**.
   - Ketika alarm berbunyi untuk HDF, PWF, atau OSF, teknisi dapat yakin 94%–100% bahwa penyebab tersebut akurat.

2. **Deteksi Keausan Alat (TWF)**:
   - Keausan alat terjadi secara gradual. Model ML memadukan probabilitas sensor dengan aturan batas fisik ($> 200\text{ menit}$) untuk memperingatkan penggantian alat sebelum patah total.

3. **Penanganan Multi-Failure (Edge Cases)**:
   - Model *Multi-Label Classification* mampu mendeteksi ketika mesin mengalami kerusakan ganda (misal **HDF + TWF** atau **PWF + OSF**), sehingga LLM dapat memprioritaskan penanganan bahaya kelistrikan/suhu terlebih dahulu sebelum masalah mekanis pisau.

---

## 5. Kesimpulan Komprehensif

1. **Integrasi End-to-End Berhasil**:
   - Seluruh alur kerja telah distandarkan dari notebook `01` hingga `07` dalam Bahasa Inggris dan *clean code*.
   - Objek `Pipeline` tunggal tersimpan di `models/smart_maintenance_pipeline.pkl` dan siap menerima data sensor mentah (*raw input*) tanpa butuh preprocessing manual tambahan.

2. **Performa Sistem Sangat Solid**:
   - Prediksi status kegagalan utama (`machine_failure`) memiliki ketajaman tinggi (ROC-AUC **0.9850**).
   - Diagnosis mode kerusakan spesifik untuk jenis kegagalan utama (HDF, PWF, OSF) mencapai keakuratan mendekati sempurna (F1-Score **94% - 100%**).
3. **Kesiapan Operasional**:
   - Hasil deteksi mode kegagalan spesifik dapat langsung disalurkan ke model bahasa (Qwen2.5-7B) untuk penerbitan SOP perbaikan otomatis.
