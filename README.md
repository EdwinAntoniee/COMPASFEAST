# Mantain - AI & Machine Learning Pipeline

👉 **To view and run the fully integrated Full-Stack web application (Frontend, Backend, and Docker), please switch to the [`result` branch](https://github.com/EdwinAntoniee/COMPASFEAST/tree/result).**

---

## 📖 Overview
This repository (branch) contains the entire Machine Learning and Deep Learning pipeline that serves as the core intelligence of the **SmartMantAIn** system (COMPFEST 18 AIC). The system operates on a **Dual AI Architecture**:
1. **Predictive AI:** A multi-label failure prediction classification model designed to detect anomalies in manufacturing machine sensors in real-time, trained on the AI4I 2020 dataset.
2. **Generative AI:** A Large Language Model (Qwen2.5-7B-Instruct) fine-tuned using the QLoRA method to autonomously generate tactical Standard Operating Procedures (SOPs) and Root Cause Analysis (RCA) guided by Safety-First principles.

## 📂 Repository Structure
- `data/` : Contains the raw dataset (AI4I 2020), preprocessed data, and train/test splits.
- `models/` : Storage directory for trained model artifacts.
- `notebooks/` : A collection of Jupyter Notebooks for experiments, covering EDA, model training scripts, and LLM testing (via Google Colab).
- `reports/` : Evaluation metrics, classification reports, and performance analysis visualizations.
- `src/` : Modular Python source code for automated preprocessing and training pipelines.
- `requirements.txt` : A list of Python package dependencies required to reproduce the experiments.

## 🛠️ Technology & Tools (AI/ML Stack)
- **Data Science:** Pandas, NumPy, Scikit-Learn, XGBoost / Random Forest.
- **Generative AI:** PyTorch, Hugging Face Transformers, TRL (Transformer Reinforcement Learning), Unsloth (for QLoRA fine-tuning optimization).
- **Deployment Export:** Ollama & GGUF Format (for local CPU inference).

## 🚀 How to Run Local Experiments
If you wish to reproduce our results or re-test the trained models in your local environment, follow these steps:

1. **Clone this repository:**
   ```bash
   git clone https://github.com/EdwinAntoniee/COMPASFEAST
   cd COMPASFEAST
   ```
2. Create a Virtual Environment & Install Dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows users: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Explore the Notebooks:
Open the notebooks/ directory using Jupyter Notebook or VS Code to dive into the Predictive AI and Generative AI training pipelines.

Built with 💡 by Team STRIVE for COMPFEST 18 AIC.
